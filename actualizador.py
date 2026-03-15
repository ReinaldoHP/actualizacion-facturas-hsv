import os
import re
from pathlib import Path

class ActualizadorFacturas:
    def __init__(self):
        pass

    def procesar_carpeta(self, ruta_carpeta: str) -> dict:
        """
        Procesa una carpeta de factura, buscando un nuevo FEV, 
        actualizando los demás archivos y renombrando la carpeta.
        Returns un dict con el status y las acciones tomadas.
        """
        carpeta = Path(ruta_carpeta)
        if not carpeta.exists() or not carpeta.is_dir():
            return {"exito": False, "mensaje": f"La carpeta {ruta_carpeta} no existe o no es un directorio válida."}
        
        # 1. Encontrar todos los archivos FEV
        archivos_fev = list(carpeta.glob("FEV_*.pdf"))
        
        if len(archivos_fev) < 2:
            return {"exito": False, "mensaje": f"No se encontraron 2 archivos FEV en {carpeta.name}. Se requiere el FEV antiguo y el FEV nuevo en la misma carpeta antes de ejecutar."}
        
        numero_carpeta = carpeta.name
        fev_antiguo = None
        fev_nuevo = None
        
        # Intentar determinar cuál es el nuevo basado en el que NO coincide con el nombre de la carpeta
        for fev in archivos_fev:
            # Extraer número FEV (Formato FEV_NIT_NUMERO.pdf o similar)
            match = re.search(r'FEV_.*_(\d+)\.pdf', fev.name, re.IGNORECASE)
            if not match:
                # Intento secundario: último bloque separado por guion bajo
                num_fact_fev = fev.stem.split('_')[-1]
            else:
                num_fact_fev = match.group(1)
            
            if num_fact_fev == numero_carpeta: 
                fev_antiguo = fev
            else:
                fev_nuevo = fev
                
        # Fallback: Determinar por fecha de modificación
        if not fev_antiguo or not fev_nuevo:
            archivos_fev.sort(key=lambda x: x.stat().st_mtime)
            fev_antiguo = archivos_fev[0] # Modificado más antiguo
            fev_nuevo = archivos_fev[-1]  # Modificado más recientemente

        if fev_antiguo == fev_nuevo:
             return {"exito": False, "mensaje": "No hay un archivo FEV diferente para realizar la actualización."}

        # Extraer números limpios para reemplazar en los demás PDFs
        def extraer_numero(archivo):
            match = re.search(r'FEV_.*_(\d+)\.pdf', archivo.name, re.IGNORECASE)
            return match.group(1) if match else archivo.stem.split('_')[-1]

        num_nuevo = extraer_numero(fev_nuevo)
        num_antiguo = extraer_numero(fev_antiguo)
        
        if not num_antiguo:
             num_antiguo = numero_carpeta

        if not fev_antiguo or not fev_nuevo:
             return {"exito": False, "mensaje": "No se pudieron identificar los archivos FEV necesarios (antiguo y nuevo)."}

        acciones = []
        try:
            # Eliminar el FEV antiguo
            fev_antiguo.unlink()
            acciones.append(f"Eliminado: {fev_antiguo.name}")
            
            # Renombrar los demás archivos (HEV, OPF, PDE, etc.)
            for archivo in carpeta.iterdir():
                if archivo.is_file() and archivo.suffix.lower() == '.pdf' and archivo != fev_nuevo:
                    nuevo_nombre = archivo.name.replace(num_antiguo, num_nuevo)
                    if nuevo_nombre != archivo.name:
                        nuevo_path = archivo.with_name(nuevo_nombre)
                        archivo.rename(nuevo_path)
                        acciones.append(f"Renombrado: {archivo.name} -> {nuevo_nombre}")
            
            # Renombrar la carpeta principal
            nuevo_nombre_carpeta = carpeta.name.replace(num_antiguo, num_nuevo)
            if num_antiguo not in carpeta.name: # Si el num antiguo no era parte exacta del nombre, sobreescribir
                nuevo_nombre_carpeta = num_nuevo
                
            nueva_carpeta = carpeta.with_name(nuevo_nombre_carpeta)
            
            if nueva_carpeta != carpeta:
                if nueva_carpeta.exists():
                     return {"exito": True, "advertencia": f"Se modificaron los archivos, pero NO se pudo renombrar la carpeta madre porque ya existe una llamada '{nueva_carpeta.name}'.", "acciones": acciones, "nueva_ruta": str(carpeta)}
                     
                carpeta.rename(nueva_carpeta)
                acciones.append(f"Carpeta renombrada a: {nuevo_nombre_carpeta}")
                return {"exito": True, "mensaje": "Archivos y carpeta actualizados correctamente.", "acciones": acciones, "nueva_ruta": str(nueva_carpeta)}
            
            return {"exito": True, "mensaje": "Archivos actualizados.", "acciones": acciones, "nueva_ruta": str(carpeta)}
            
        except Exception as e:
            return {"exito": False, "mensaje": f"Error del sistema: {str(e)}"}
