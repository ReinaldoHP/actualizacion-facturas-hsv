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
            return {"exito": False, "mensaje": f"La carpeta {ruta_carpeta} no existe o no es un directorio válido."}
        
        # 1. Encontrar archivos FEV
        archivos_fev = list(carpeta.glob("FEV_*.pdf"))
        
        if len(archivos_fev) < 2:
            return {
                "exito": False, 
                "mensaje": f"Se requieren al menos 2 archivos FEV. Encontrados: {[f.name for f in archivos_fev]}"
            }
        
        num_carpeta = carpeta.name
        fev_antiguo = None
        fev_nuevo = None
        
        # Intentar identificar por nombre (el que coincide con la carpeta es el viejo)
        for f in archivos_fev:
            match = re.search(r'FEV_.*_(\d+)\.pdf', f.name, re.IGNORECASE)
            num = match.group(1) if match else f.stem.split('_')[-1]
            if num == num_carpeta:
                fev_antiguo = f
                break
        
        # Si no se encontró por nombre, el más antiguo por fecha es el viejo
        if fev_antiguo is None:
            archivos_fev.sort(key=lambda x: x.stat().st_mtime)
            fev_antiguo = archivos_fev[0]
            
        # El FEV nuevo es el más reciente de los archivos restantes
        otros = [f for f in archivos_fev if str(f) != str(fev_antiguo)]
        if not otros:
            return {"exito": False, "mensaje": "Error: Solo se detectó un archivo FEV único."}
            
        otros.sort(key=lambda x: x.stat().st_mtime)
        fev_nuevo = otros[-1]

        # Validación final de seguridad antes de proceder
        if fev_antiguo is None or fev_nuevo is None:
             return {"exito": False, "mensaje": "No se pudieron identificar los archivos FEV (antiguo/nuevo)."}

        # Extraer IDs completos (NIT + Factura) para un renombrado más robusto
        # Formato esperado: FEV_<NIT>_<FACTURA>.pdf -> Capturamos <NIT>_<FACTURA>
        def extraer_id_completo(archivo):
            match = re.search(r'FEV_(.*)\.pdf', archivo.name, re.IGNORECASE)
            return match.group(1) if match else archivo.stem.split('FEV_')[-1]

        def extraer_solo_factura(archivo):
            match = re.search(r'FEV_.*_(\d+)\.pdf', archivo.name, re.IGNORECASE)
            return match.group(1) if match else archivo.stem.split('_')[-1]

        id_nuevo = extraer_id_completo(fev_nuevo)
        id_antiguo = extraer_id_completo(fev_antiguo)
        fact_nueva = extraer_solo_factura(fev_nuevo)
        fact_antigua = extraer_solo_factura(fev_antiguo)
        
        # Patrones a reemplazar en los otros PDFs (HEV, OPF, etc.)
        # Priorizamos el ID completo (NIT_Factura)
        patrones_reemplazo = [
            (id_antiguo, id_nuevo),           # NIT_Factura antigua -> NIT_Factura nueva
            (num_carpeta, fact_nueva),        # Carpeta (ej. 12345) -> Factura nueva
            (fact_antigua, fact_nueva)        # Factura antigua sola -> Factura nueva
        ]

        acciones = []
        try:
            # Eliminar el FEV antiguo de forma segura
            nombre_viejo = fev_antiguo.name if fev_antiguo else "FEV_antiguo"
            if fev_antiguo:
                fev_antiguo.unlink()
            acciones.append(f"Eliminado: {nombre_viejo}")
            
            # Renombrar TODOS los archivos PDFs en la carpeta
            for archivo in carpeta.iterdir():
                if archivo.is_file() and archivo.suffix.lower() == '.pdf' and str(archivo) != str(fev_nuevo):
                    nombre_final = archivo.name
                    # Aplicamos reemplazos en cadena para asegurar que todo cambie
                    for viejo, nuevo in patrones_reemplazo:
                        if viejo:
                            nombre_final = nombre_final.replace(viejo, nuevo)
                    
                    if nombre_final != archivo.name:
                        nuevo_path = archivo.with_name(nombre_final)
                        # Evitar colisiones si el archivo ya existe
                        if not nuevo_path.exists():
                            archivo.rename(nuevo_path)
                            acciones.append(f"Renombrado: {archivo.name} -> {nombre_final}")
            
            # Renombrar la carpeta madre
            # Priorizamos renombrarla con el número de factura nueva
            nueva_carpeta = carpeta.with_name(fact_nueva)
            
            if nueva_carpeta != carpeta:
                if nueva_carpeta.exists():
                     return {"exito": True, "advertencia": f"Archivos actualizados. No se pudo renombrar la carpeta madre porque '{fact_nueva}' ya existe.", "acciones": acciones, "nueva_ruta": str(carpeta)}
                
                carpeta.rename(nueva_carpeta)
                acciones.append(f"Carpeta renombrada a factura: {fact_nueva}")
                return {"exito": True, "mensaje": "¡Proceso finalizado con éxito!", "acciones": acciones, "nueva_ruta": str(nueva_carpeta)}
            
            return {"exito": True, "mensaje": "Archivos actualizados.", "acciones": acciones, "nueva_ruta": str(carpeta)}
            
            
        except Exception as e:
            return {"exito": False, "mensaje": f"Error del sistema: {str(e)}"}
