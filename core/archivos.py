import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import shutil
import os
import subprocess

class ApartadoArchivos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.unidad_usb = None
        self.portapapeles = [] # Para la función de Copiar/Pegar
        
        self.frame = ttk.LabelFrame(self, text=" Administrador de Almacenamiento ")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.frame_top = ttk.Frame(self.frame) # estado y navegacion
        self.frame_top.pack(fill="x", padx=10, pady=5)
        self.lbl_usb_status = ttk.Label(self.frame, text="Buscando USB...", font=("Arial", 12, "bold"))
        self.lbl_usb_status.pack(pady=20)
        self.lbl_aviso_expulsion = ttk.Label(self.frame, text="", font=("Arial", 10, "italic"))
        self.lbl_aviso_expulsion.pack(pady=(5, 10))

        # frame para la barra de dirección y botón subir
        self.frame_nav = ttk.Frame(self.frame)
        self.frame_nav.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_subir = ttk.Button(self.frame_nav, text="⬆ Subir", command=self.subir_nivel, state="disabled")
        self.btn_subir.pack(side="left", padx=(0, 5))
        
        self.lbl_ruta = ttk.Label(self.frame_nav, text="Ruta: ---", relief="sunken", anchor="w")
        self.lbl_ruta.pack(side="left", fill="x", expand=True)
        # lista de archivos
        self.tree = ttk.Treeview(self.frame, columns=("tipo", "tamano"), selectmode="browse", height=10)
        self.tree.heading("#0", text="Nombre")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("tamano", text="Tamaño")
        
        self.tree.column("#0", width=300)
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("tamano", width=100, anchor="e")
        
        self.tree.pack(fill="both", expand=True, padx=10)
        #              barra de desplazamiento para la lista
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<Double-1>", self.on_doble_click) # evento doble click para abrir carpetas
        

        # Contenedor de botones (Fila 1)
        self.btn_f1 = ttk.Frame(self.frame)
        self.btn_f1.pack(pady=10)

        ttk.Button(self.btn_f1, text="📄 Copiar", command=self.accion_copiar, width=15).pack(side="left", padx=5)
        ttk.Button(self.btn_f1, text="📋 Pegar", command=self.accion_pegar, width=15).pack(side="left", padx=5)
        ttk.Button(self.btn_f1, text="📦 Mover", command=self.accion_mover, width=15).pack(side="left", padx=5)

        # Contenedor de botones (Fila 2)
        self.btn_f2 = ttk.Frame(self.frame)
        self.btn_f2.pack(pady=10)

        ttk.Button(self.btn_f2, text="🧹 Formatear", command=self.real_formatear, width=15).pack(side="left", padx=5)
        ttk.Button(self.btn_f2, text="⏏️ Expulsar", command=self.expulsar_usb, width=15).pack(side="left", padx=5)

        self.monitorear_usb()

    def monitorear_usb(self):
        try:
            particiones = psutil.disk_partitions()
            encontrado = False
            nueva_unidad = None # variable temporal para detectar cambios
            
            for p in particiones:
                if 'removable' in p.opts or 'usb' in p.device.lower():
                    nueva_unidad = p.mountpoint
                    encontrado = True
                    break
            if encontrado:
                self.lbl_usb_status.config(text=f"✅ USB DETECTADA EN: {nueva_unidad}", foreground="green")
                if self.unidad_usb != nueva_unidad:
                    self.unidad_usb = nueva_unidad
                    self.ruta_actual = nueva_unidad # iniciamos en la raíz del USB
                    self.actualizar_vista()
            else:
                self.unidad_usb = None
                self.ruta_actual = None
                self.lbl_usb_status.config(text="❌ NO SE DETECTA USB", foreground="red")
                self.limpiar_vista()
        except: pass
        self.after(2000, self.monitorear_usb)
    
    
    def actualizar_vista(self):
        self.limpiar_vista()
        if not self.ruta_actual or not os.path.exists(self.ruta_actual):
            return
        self.lbl_ruta.config(text=self.ruta_actual)
        
        if self.unidad_usb and self.ruta_actual != self.unidad_usb:
            self.btn_subir.state(["!disabled"])
        else:
            self.btn_subir.state(["disabled"])

        try:
            contenido = os.listdir(self.ruta_actual)
            # carpetas_prohibidas = ["System Volume Information", "$RECYCLE.BIN", "Recovery", "msdownld.tmp"]
            # contenido = [x for x in contenido if x not in carpetas_prohibidas]
            carpetas = [] # separar carpetas y archivos
            archivos = []
            
            for item in contenido:
                ruta_completa = os.path.join(self.ruta_actual, item)
                if os.path.isdir(ruta_completa):
                    carpetas.append(item)
                else:
                    archivos.append(item)
            
            for c in carpetas:  # insertar en el arbol
                self.tree.insert("", "end", text=f"📂 {c}", values=("Carpeta", ""), open=False, tags=("folder",))
            
            for a in archivos:
                ruta_completa = os.path.join(self.ruta_actual, a)
                try:
                    tamano_kb = round(os.path.getsize(ruta_completa) / 1024, 1)
                except:
                    tamano_kb = "?"
                ext = os.path.splitext(a)[1]
                self.tree.insert("", "end", text=f"📄 {a}", values=(f"Archivo {ext}", f"{tamano_kb} KB"), tags=("file",))
                
        except PermissionError:
            messagebox.showerror("Error", "Permiso denegado para acceder a esta carpeta.")
            self.subir_nivel()
        except Exception as e:
            print(f"Error al listar: {e}")

    def limpiar_vista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_ruta.config(text="")

    def on_doble_click(self, event):
        """Entra a la carpeta seleccionada"""
        item_id = self.tree.selection()
        if not item_id: return     
        item_text = self.tree.item(item_id, "text")
        
        if "📂" in item_text: # verifica si es carpeta por el icono o tag (método simple
            nombre_carpeta = item_text.replace("📂 ", "")
            nueva_ruta = os.path.join(self.ruta_actual, nombre_carpeta)
            if os.path.exists(nueva_ruta):
                self.ruta_actual = nueva_ruta
                self.actualizar_vista()

    def subir_nivel(self):
        if not self.ruta_actual or self.ruta_actual == self.unidad_usb:
            return # No subir más allá de la raíz del USB
            
        carpeta_padre = os.path.dirname(self.ruta_actual)
        self.ruta_actual = carpeta_padre
        self.actualizar_vista()
    
    
    

    def accion_copiar(self):
        # Selecciona archivos o carpetas para poner en el "portapapeles" del programa
        files = filedialog.askopenfilenames(title="Seleccione archivos para copiar")
        if files:
            self.portapapeles = list(files)
            messagebox.showinfo("Copiado", f"{len(self.portapapeles)} elementos listos para pegar.")

    def accion_pegar(self):
        if not self.ruta_actual: return
        if not self.unidad_usb:
            messagebox.showwarning("Error", "No hay USB conectada.")
            return
        if not self.portapapeles:
            messagebox.showwarning("Vacío", "No hay nada copiado en el portapapeles.")
            return

        try:
            for item in self.portapapeles:
                nombre = os.path.basename(item)
                destino = os.path.join(self.ruta_actual, nombre)
                if os.path.isdir(item):
                    if os.path.exists(destino): shutil.rmtree(destino)
                    shutil.copytree(item, destino)
                else:
                    shutil.copy2(item, destino)
            messagebox.showinfo("Éxito", "Elementos pegados en el USB.")
            self.actualizar_vista()
            self.portapapeles = [] # Limpiar portapapeles tras pegar
        except Exception as e:
            messagebox.showerror("Error", f"Error al pegar: {e}")

    def accion_mover(self):
        if not self.ruta_actual: return
        archivo = filedialog.askopenfilename(title="Seleccione archivo para MOVER aquí")
        if archivo:
            try:
                destino = os.path.join(self.ruta_actual, os.path.basename(archivo))
                shutil.move(archivo, destino)
                messagebox.showinfo("Éxito", "Archivo movido aquí.")
                self.actualizar_vista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mover: {e}")

    def real_formatear(self):
        if not self.unidad_usb: return
        if messagebox.askyesno("PELIGRO", f"¿Formatear {self.unidad_usb}?\nSE BORRARÁ TODO."):
            try:
                # Método simple: borrar contenido
                for item in os.listdir(self.unidad_usb):
                    path = os.path.join(self.unidad_usb, item)
                    if os.path.isfile(path): os.remove(path)
                    else: shutil.rmtree(path)
                
                self.ruta_actual = self.unidad_usb # Volver a la raíz
                messagebox.showinfo("Formateado", "La unidad está vacía.")
                self.actualizar_vista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo formatear: {e}")

    def expulsar_usb(self):
        if not self.unidad_usb: return
        try:
            letra = self.unidad_usb.strip(":\\")
            cmd = f"powershell $driveEject = New-Object -ComObject Shell.Application; $driveEject.Namespace(17).ParseName('{letra}:').InvokeVerb('Eject')"
            subprocess.run(cmd, shell=True)
            self.unidad_usb = None
            self.ruta_actual = None
            self.limpiar_vista()
            self.lbl_usb_status.config(text="USB EXPULSADA (Puede retirarla)", foreground="blue")
            self.after(10000, lambda: self.lbl_aviso_expulsion.config(text=""))
            self.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al expulsar: {e}")




# funciones auxiliares globales 
def obtener_unidades_extraibles():
    return [p.mountpoint for p in psutil.disk_partitions() if 'removable' in p.opts]

def listar_archivos(ruta):
    try:
        return os.listdir(ruta) if os.path.exists(ruta) else []
    except: return []
    
    
    
    


