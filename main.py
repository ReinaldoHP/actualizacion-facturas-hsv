import tkinter as tk
from tkinter import filedialog, messagebox, BOTH, YES, X, LEFT, RIGHT, W, Y # type: ignore
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
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Inicialización de atributos (usando Any para silenciar el linter)
        self.actualizador: Any = ActualizadorFacturas() # type: ignore
        self.ruta_seleccionada: Any = tk.StringVar()
        self.entry_ruta: Any = None
        self.txt_log: Any = None
        self.btn_actualizar: Any = None
        self.ultima_ruta_carpeta: str = "D:/"
        self.ultima_ruta_fev: str = "D:/"
        
        # Estilo del tema
        self.style = tb.Style("cosmo") # type: ignore
        
        self.actualizador = ActualizadorFacturas()
        self.ruta_seleccionada = tk.StringVar()
        
        self.crear_interfaz()

    def crear_interfaz(self):
        # Contenedor principal
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Título del Proyecto
        header_frame = tb.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        tb.Label(header_frame, text="ACTUALIZADOR DE FACTURAS", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(side=LEFT)
        
        # Sección 5: Diseño del Programa (Título del mockup)
        tb.Label(main_frame, text="5. Diseño del Programa", font=("Helvetica", 14), bootstyle="dark").pack(anchor=W, pady=(0, 10))
        
        # Subtítulo descriptivo
        desc_text = "Este programa permite actualizar automáticamente los PDFs de una carpeta de facturas cuando el usuario pega un nuevo archivo FEV con un número distinto."
        tb.Label(main_frame, text=desc_text, wraplength=550, bootstyle="secondary", font=("Helvetica", 10)).pack(anchor=W, pady=(0, 20))
        
        # Recuadro de selección (Frame similar al del mockup)
        selection_frame = tb.LabelFrame(main_frame, text="Carpeta seleccionada:")
        selection_frame.pack(fill=X, pady=(0, 10))
        
        # Frame interno para el padding de los elementos de selección
        inner_selection = tb.Frame(selection_frame)
        inner_selection.pack(fill=X, padx=15, pady=15)
        
        self.entry_ruta = tb.Entry(inner_selection, textvariable=self.ruta_seleccionada, state="readonly", width=50)
        self.entry_ruta.pack(side=LEFT, padx=(0, 10), fill=X, expand=YES)
        
        btn_seleccionar = tb.Button(inner_selection, text="📂 Seleccionar carpeta", bootstyle="warning-outline", command=self.seleccionar_carpeta)
        btn_seleccionar.pack(side=RIGHT)

        # Nueva Sección: Cargar Nuevo FEV
        fev_frame = tb.LabelFrame(main_frame, text="Paso 1: Cargar Nuevo FEV (Opcional):")
        fev_frame.pack(fill=X, pady=(0, 10))
        
        inner_fev = tb.Frame(fev_frame)
        inner_fev.pack(fill=X, padx=15, pady=15)
        
        tb.Label(inner_fev, text="Si tienes el nuevo PDF fuera de la carpeta, cárgalo aquí:", font=("Helvetica", 9), bootstyle="secondary").pack(side=LEFT)
        
        btn_cargar_fev = tb.Button(inner_fev, text="📄 Cargar y Procesar FEV", bootstyle="info-outline", command=self.cargar_nuevo_fev)
        btn_cargar_fev.pack(side=RIGHT)

        # Estado del sistema
        status_frame = tb.LabelFrame(main_frame, text="Estado del sistema:")
        status_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Frame interno para el padding del texto de log
        inner_status = tb.Frame(status_frame)
        inner_status.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        self.txt_log = tk.Text(inner_status, height=10, font=("Consolas", 9), state="disabled", bg="#f8f9fa", fg="#212529", borderwidth=0)
        self.txt_log.pack(fill=BOTH, expand=YES)
        
        # Agregar scrollbar al log
        scrollbar = tb.Scrollbar(self.txt_log, bootstyle="primary-round")
        scrollbar.pack(side=RIGHT, fill=Y)
        self.txt_log.config(yscrollcommand=scrollbar.set)
        
        # Botón Principal (Grande y azul como el mockup)
        self.btn_actualizar = tb.Button(
            main_frame, 
            text="ACTUALIZAR FACTURA", 
            bootstyle="primary", 
            width=50,
            padding=15,
            command=self.ejecutar_actualizacion
        )
        self.btn_actualizar.pack(pady=10)
        
        # Footer
        footer_text = "Presiona el botón para iniciar el proceso automáticamente."
        tb.Label(main_frame, text=footer_text, font=("Helvetica", 9), bootstyle="secondary").pack()

    def escribir_log(self, mensaje, tipo="info"):
        self.txt_log.config(state="normal")
        tag = "normal"
        if tipo == "success":
            tag = "success"
            self.txt_log.tag_config("success", foreground="green")
        elif tipo == "error":
            tag = "error"
            self.txt_log.tag_config("error", foreground="red")
            
        self.txt_log.insert(tk.END, f"> {mensaje}\n", tag)
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.ultima_ruta_carpeta, title="Seleccionar Carpeta de Factura")
        if carpeta:
            self.ultima_ruta_carpeta = str(Path(carpeta).parent)
            self.ruta_seleccionada.set(carpeta)
            self.escribir_log(f"Carpeta seleccionada: {Path(carpeta).name}")
            self.btn_actualizar.config(state="normal")

    def cargar_nuevo_fev(self):
        ruta_destino = self.ruta_seleccionada.get()
        if not ruta_destino:
            messagebox.showwarning("Atención", "Primero debes seleccionar la carpeta donde quieres poner el nuevo FEV.")
            return
            
        archivo_origen = filedialog.askopenfilename(
            initialdir=self.ultima_ruta_fev,
            title="Seleccionar el nuevo archivo FEV",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if archivo_origen:
            try:
                self.ultima_ruta_fev = str(Path(archivo_origen).parent)
                nombre_archivo = Path(archivo_origen).name
                destino_final = Path(ruta_destino) / nombre_archivo
                
                # Copiar el archivo
                shutil.copy2(archivo_origen, destino_final)
                self.escribir_log(f"Archivo copiado con éxito: {nombre_archivo}", "success")
                
                # Ejecutar actualización automáticamente después de cargar
                self.ejecutar_actualizacion()
                
            except Exception as e:
                self.escribir_log(f"Error al copiar el archivo: {str(e)}", "error")
                messagebox.showerror("Error de copia", str(e))


    def ejecutar_actualizacion(self):
        ruta = self.ruta_seleccionada.get()
        if not ruta:
            messagebox.showwarning("Atención", "Por favor selecciona una carpeta primero.")
            return
            
        self.btn_actualizar.config(state="disabled")
        self.escribir_log("Iniciando proceso...", "info")
        
        try:
            resultado = self.actualizador.procesar_carpeta(ruta)
            
            if resultado.get("exito"):
                for accion in resultado.get("acciones", []):
                    self.escribir_log(accion, "success")
                
                self.escribir_log(f"ÉXITO: {resultado.get('mensaje')}", "success")
                messagebox.showinfo("Éxito", resultado.get("mensaje"))
                
                # Actualizar la ruta si la carpeta se renombró
                if resultado.get("nueva_ruta"):
                    self.ruta_seleccionada.set(resultado.get("nueva_ruta"))
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
