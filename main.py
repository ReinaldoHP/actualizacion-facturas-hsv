import tkinter as tk
from tkinter import filedialog, messagebox, BOTH, YES, X, LEFT, RIGHT, W, Y, BOTTOM # type: ignore
from pathlib import Path
from typing import Any
import sys
import os
import shutil

# Asegurar que el directorio actual esté en el path para importaciones locales
sys.path.append(str(Path(__file__).parent))

import ttkbootstrap as tb # type: ignore
from actualizador import ActualizadorFacturas # type: ignore
import shutil

class ActualizadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Actualizador de Facturas")
        self.root.geometry("620x600")
        self.root.resizable(True, True)
        
        # Inicialización de atributos (usando Any para silenciar el linter)
        self.actualizador: Any = ActualizadorFacturas() # type: ignore
        self.ruta_seleccionada: Any = tk.StringVar()
        self.destino_seleccionado: Any = tk.StringVar()
        self.ruta_raiz: Any = tk.StringVar()
        self.busqueda_factura: Any = tk.StringVar()
        self.entry_ruta: Any = None
        self.entry_destino: Any = None
        self.entry_raiz: Any = None
        self.tree: Any = None
        self.txt_log: Any = None
        self.btn_actualizar: Any = None
        self.ultima_ruta_carpeta: str = "D:/"
        self.ultima_ruta_destino: str = "D:/"
        self.ultima_ruta_raiz: str = "D:/"
        self.ultima_ruta_fev: str = "D:/"
        
        # Estilo del tema
        self.style = tb.Style("cosmo") # type: ignore
        
        self.actualizador = ActualizadorFacturas()
        self.ruta_seleccionada = tk.StringVar()
        self.destino_seleccionado = tk.StringVar()
        self.ruta_raiz = tk.StringVar()
        self.busqueda_factura = tk.StringVar()
        
        self.crear_interfaz()

    def crear_interfaz(self):
        # Contenedor principal con scroll o fijo
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=YES, padx=25, pady=20)
        
        # TÍTULO PRINCIPAL
        tb.Label(main_frame, text="ACTUALIZADOR DE FACTURAS", font=("Helvetica", 22, "bold"), bootstyle="primary").pack(pady=(0, 20))

        # --- SECCIÓN 1: ORIGEN ---
        sec1 = tb.Frame(main_frame)
        sec1.pack(fill=X, pady=(0, 15))
        
        tb.Label(sec1, text="1. SELECCIONAR FACTURA ORIGINAL", font=("Helvetica", 12, "bold"), bootstyle="primary").pack(anchor=W, pady=(0, 5))
        
        # Fila de Búsqueda y Manual
        row1 = tb.Frame(sec1)
        row1.pack(fill=X, pady=5)
        
        tb.Label(row1, text="Nº Factura:").pack(side=LEFT, padx=(0, 5))
        ent_search = tb.Entry(row1, textvariable=self.busqueda_factura, width=12)
        ent_search.pack(side=LEFT, padx=(0, 10))
        ent_search.bind("<Return>", lambda e: self.buscar_factura())
        
        tb.Button(row1, text="🔍 Buscar", bootstyle="primary", command=self.buscar_factura).pack(side=LEFT, padx=2)
        tb.Button(row1, text="📂 Manual", bootstyle="warning-outline", command=self.seleccionar_carpeta).pack(side=LEFT, padx=5)
        tb.Button(row1, text="⚙️ Raíz", bootstyle="link", command=self.seleccionar_raiz).pack(side=RIGHT)

        # Ruta actual
        self.entry_ruta = tb.Label(sec1, textvariable=self.ruta_seleccionada, font=("Helvetica", 8), bootstyle="secondary")
        self.entry_ruta.pack(anchor=W, pady=(2, 5))

        # Visor de archivos (Treeview)
        self.tree = tb.Treeview(sec1, columns=("archivo", "tipo", "tamaño"), show="headings", height=3, bootstyle="info")
        self.tree.heading("archivo", text="Archivo")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("tamaño", text="Tamaño")
        self.tree.column("archivo", width=250)
        self.tree.column("tipo", width=70)
        self.tree.column("tamaño", width=70)
        self.tree.pack(fill=X, pady=5)

        # --- SECCIÓN 2: DESTINO ---
        sec2 = tb.Frame(main_frame)
        sec2.pack(fill=X, pady=10)
        
        tb.Label(sec2, text="2. CARPETA DE DESTINO (COPIA)", font=("Helvetica", 12, "bold"), bootstyle="success").pack(anchor=W, pady=(0, 5))
        
        row2 = tb.Frame(sec2)
        row2.pack(fill=X, pady=5)
        
        self.entry_destino = tb.Entry(row2, textvariable=self.destino_seleccionado, state="readonly")
        self.entry_destino.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        tb.Button(row2, text="🎯 Destino", bootstyle="success", command=self.seleccionar_destino).pack(side=RIGHT)

        # --- SECCIÓN 3: PROCESO ---
        sec3 = tb.Frame(main_frame)
        sec3.pack(fill=X, pady=15)
        
        tb.Label(sec3, text="3. CARGAR FEV Y PROCESAR", font=("Helvetica", 12, "bold"), bootstyle="info").pack(anchor=W, pady=(0, 5))
        
        self.btn_actualizar = tb.Button(
            sec3, 
            text="📄 SELECCIONAR NUEVO FEV Y ACTUALIZAR COPIA", 
            bootstyle="info", 
            command=self.cargar_nuevo_fev,
            padding=12
        )
        self.btn_actualizar.pack(fill=X, pady=10)

        # Log de salida
        self.txt_log = tk.Text(main_frame, height=3, font=("Consolas", 9), state="disabled", bg="#f8f9fa", borderwidth=1)
        self.txt_log.pack(fill=BOTH, expand=YES, pady=(10, 0))
        
        # Pie de página con firma
        footer = tb.Frame(main_frame)
        footer.pack(fill=X, side=BOTTOM, pady=5)
        tb.Label(footer, text="Reinaldo HP", font=("Helvetica", 9, "bold"), bootstyle="secondary").pack(side=RIGHT)
        tb.Label(footer, text="Tus originales no se tocan. Todo se hace en la copia.", font=("Helvetica", 8), bootstyle="secondary").pack(side=LEFT)

    def escribir_log(self, mensaje, tipo="info"):
        self.txt_log.config(state="normal")
        tag = "normal"
        if tipo == "success":
            tag = "success"
            self.txt_log.tag_config("success", foreground="green")
        elif tipo == "error":
            tag = "error"
            self.txt_log.tag_config("error", foreground="red")
        elif tipo == "warning":
            tag = "warning"
            self.txt_log.tag_config("warning", foreground="orange")
            
        self.txt_log.insert(tk.END, f"> {mensaje}\n", tag)
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def seleccionar_raiz(self):
        raiz = filedialog.askdirectory(initialdir=self.ultima_ruta_raiz, title="Seleccionar Carpeta Principal de Facturas")
        if raiz:
            self.ultima_ruta_raiz = raiz
            self.ruta_raiz.set(raiz)
            self.escribir_log(f"Raíz configurada: {raiz}")

    def actualizar_visor_archivos(self, ruta: str):
        # Limpiar treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            p = Path(ruta)
            if not p.exists(): return
            
            for archivo in p.glob("*.pdf"):
                size = f"{archivo.stat().st_size / 1024:.1f} KB"
                tipo = "FEV" if "FEV" in archivo.name.upper() else "Documento"
                self.tree.insert("", tk.END, values=(archivo.name, tipo, size))
        except Exception as e:
            self.escribir_log(f"Error al listar archivos: {str(e)}", "error")

    def buscar_factura(self):
        raiz = self.ruta_raiz.get()
        numero = self.busqueda_factura.get().strip()
        
        if not raiz:
            messagebox.showwarning("Atención", "Primero define la Carpeta Principal (Raíz).")
            return
        if not numero:
            messagebox.showwarning("Atención", "Ingresa un número de factura para buscar.")
            return
        
        self.escribir_log(f"Buscando factura '{numero}' en {Path(raiz).name}...")
        
        # Buscar en subcarpetas de la raíz
        coincidencias = []
        try:
            for item in Path(raiz).iterdir():
                if item.is_dir() and numero in item.name:
                    coincidencias.append(item)
            
            if not coincidencias:
                self.escribir_log(f"No se encontró ninguna carpeta con el número '{numero}'", "error")
                messagebox.showinfo("Búsqueda", f"No se encontró ninguna carpeta que contenga '{numero}'")
            elif len(coincidencias) == 1:
                ruta_encontrada = coincidencias[0]
                self.ruta_seleccionada.set(str(ruta_encontrada))
                self.actualizar_visor_archivos(str(ruta_encontrada))
                self.escribir_log(f"Factura encontrada: {ruta_encontrada.name}", "success")
            else:
                # Si hay varias, intentar coincidencia exacta o dejar que el usuario elija
                ruta_exacta = next((c for c in coincidencias if c.name == numero), None)
                if ruta_exacta:
                    self.ruta_seleccionada.set(str(ruta_exacta))
                    self.actualizar_visor_archivos(str(ruta_exacta))
                    self.escribir_log(f"Factura exacta encontrada: {ruta_exacta.name}", "success")
                else:
                    self.escribir_log(f"Múltiples coincidencias para '{numero}'. Seleccionada la primera: {coincidencias[0].name}", "warning")
                    self.ruta_seleccionada.set(str(coincidencias[0]))
                    self.actualizar_visor_archivos(str(coincidencias[0]))
                    
        except Exception as e:
            self.escribir_log(f"Error al buscar: {str(e)}", "error")

    def seleccionar_carpeta(self):
        # Ahora permitimos seleccionar un archivo para auto-identificar la carpeta
        archivo = filedialog.askopenfilename(
            initialdir=self.ultima_ruta_carpeta, 
            title="Selecciona cualquier PDF dentro de la carpeta de la factura",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if archivo:
            carpeta = Path(archivo).parent
            self.ultima_ruta_carpeta = str(carpeta.parent)
            self.ruta_seleccionada.set(str(carpeta))
            self.actualizar_visor_archivos(str(carpeta))
            self.escribir_log(f"Origen detectado por archivo: {carpeta.name}")

    def seleccionar_destino(self):
        destino = filedialog.askdirectory(initialdir=self.ultima_ruta_destino, title="Seleccionar Carpeta de Destino")
        if destino:
            self.ultima_ruta_destino = destino
            self.destino_seleccionado.set(destino)
            self.escribir_log(f"Destino seleccionado: {destino}")

    def cargar_nuevo_fev(self):
        ruta_origen = self.ruta_seleccionada.get()
        ruta_destino_base = self.destino_seleccionado.get()
        
        if not ruta_origen:
            messagebox.showwarning("Atención", "Primero selecciona la Carpeta Original.")
            return
        if not ruta_destino_base:
            messagebox.showwarning("Atención", "Selecciona una Carpeta de Destino para guardar la copia.")
            return
            
        archivo_fev_nuevo = filedialog.askopenfilename(
            initialdir=self.ultima_ruta_fev,
            title="Seleccionar el nuevo archivo FEV",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if archivo_fev_nuevo:
            try:
                self.ultima_ruta_fev = str(Path(archivo_fev_nuevo).parent)
                nombre_carpeta = Path(ruta_origen).name
                ruta_copia_destino = Path(ruta_destino_base) / nombre_carpeta
                
                # 1. Crear copia si no existe, o avisar
                if ruta_copia_destino.exists():
                    resp = messagebox.askyesno("Carpeta existente", f"La carpeta '{nombre_carpeta}' ya existe en el destino. ¿Deseas sobreescribirla? (Se borrará lo que haya allí)")
                    if not resp: return
                    shutil.rmtree(ruta_copia_destino)
                
                self.escribir_log(f"Copiando carpeta a destino...")
                shutil.copytree(ruta_origen, ruta_copia_destino)
                
                # 2. Copiar el nuevo FEV a la copia
                nombre_fev = Path(archivo_fev_nuevo).name
                destino_fev = ruta_copia_destino / nombre_fev
                shutil.copy2(archivo_fev_nuevo, destino_fev)
                
                self.escribir_log(f"Copia creada y FEV nuevo añadido.", "success")
                
                # 3. Guardar la ruta de la copia para el procesador
                self.ruta_seleccionada.set(str(ruta_copia_destino))
                
                # 4. Ejecutar actualización automáticamente
                self.ejecutar_actualizacion()
                
                # Restaurar ruta original en la UI para evitar confusiones posteriores
                self.ruta_seleccionada.set(ruta_origen)
                
            except Exception as e:
                self.escribir_log(f"Error en el proceso: {str(e)}", "error")
                messagebox.showerror("Error", str(e))

    def ejecutar_actualizacion(self):
        # NOTA: En este flujo, 'ruta' debería ser la de la copia si viene de cargar_nuevo_fev
        # Pero para mantener compatibilidad si el usuario ya puso el FEV manualmente en la copia:
        ruta = self.ruta_seleccionada.get()
        
        if not ruta:
            messagebox.showwarning("Atención", "Selecciona la carpeta a procesar.")
            return
            
        self.btn_actualizar.config(state="disabled")
        self.escribir_log(f"Procesando: {Path(ruta).name}...", "info")
        
        try:
            resultado = self.actualizador.procesar_carpeta(ruta)
            
            if resultado.get("exito"):
                for accion in resultado.get("acciones", []):
                    self.escribir_log(accion, "success")
                
                if resultado.get("advertencia"):
                    self.escribir_log(resultado.get("advertencia"), "warning")
                    messagebox.showwarning("Aviso", resultado.get("advertencia"))
                else:
                    self.escribir_log(f"ÉXITO: {resultado.get('mensaje')}", "success")
                    messagebox.showinfo("Éxito", resultado.get("mensaje"))
            else:
                self.escribir_log(f"FALLO: {resultado.get('mensaje')}", "error")
                messagebox.showerror("Error", resultado.get("mensaje"))
                
        except Exception as e:
            self.escribir_log(f"ERROR CRÍTICO: {str(e)}", "error")
            messagebox.showerror("Error del Sistema", str(e))
        
        self.btn_actualizar.config(state="normal")

if __name__ == "__main__":
    app_root = tb.Window(themename="cosmo") # type: ignore
    actualizador_app = ActualizadorGUI(app_root)
    app_root.mainloop()
