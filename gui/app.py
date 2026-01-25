import customtkinter as ctk
from core.hardware import obtener_info_sistema

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto Sistemas Operativos I")
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1) # cuadricula 1 fila 2 columnas
        self.grid_rowconfigure(0, weight=1) 
        
        # MENU
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nswe" )
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SISTEMAS\nOPERATIVOS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_hardware = ctk.CTkButton(self.sidebar_frame, text="Hardware", command=self.mostrar_hardware)
        self.btn_hardware.grid(row=1, column=0, padx=20, pady=10)
        self.btn_procesos = ctk.CTkButton(self.sidebar_frame, text="Procesos", command=self.mostrar_procesos)
        self.btn_procesos.grid(row=2, column=0, padx=20, pady=10)
        self.btn_archivos = ctk.CTkButton(self.sidebar_frame, text="Archivos (USB)", command=self.mostrar_archivos)
        self.btn_archivos.grid(row=3, column=0, padx=20, pady=10)
        
        # contenedor de vistas
        self.main_view = ctk.CTkFrame(self, corner_radius=10)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nswe")
        
        self.mostrar_hardware()
    
    def limpiar_pantalla(self): # antes de cambiar de seccion
        for widget in self.main_view.winfo_children():
            widget.destroy()
    
    def mostrar_hardware(self):
        self.limpiar_pantalla()
        datos = obtener_info_sistema()
        
        label_titulo = ctk.CTkLabel(self.main_view, text="Caracteristicas del Equipo", font=ctk.CTkFont(size=26, weight="bold"))
        label_titulo.pack(pady=(30, 20))
        
        frame_info = ctk.CTkFrame(self.main_view, fg_color="transparent")
        frame_info.pack(fill="both", expand=True, padx=50, pady=10)
        
        texto_base = (
            f"● Procesaor: {datos['procesador']}\n\n"
            f"● Memoria RAM Total: {datos['ram_total_gb']} GB\n"
            f"● Memoria RAM Disponible: {datos['ram_disponible_gb']} GB\n\n"
            f"● Almacenamiento Total: {datos['detalles_unidades']} GB\n"
        )
        label_base = ctk.CTkLabel(frame_info, text=texto_base, justify="left", wraplength=700, font=ctk.CTkFont(size=15))
        label_base.pack(anchor="w", pady=10)

        label_discos_titulo = ctk.CTkLabel(frame_info, text="Detalles de Unidades:", font=ctk.CTkFont(size=16, weight="bold"))
        label_discos_titulo.pack(anchor="w", pady=(10, 5))
        
        for d in datos['detalles_unidades']:
            texto_disco = f"   → Unidad {d['unidad']} | Capacidad: {d['total_gb']} GB | Disponible: {d['libre_gb']} GB"
            lbl_disco = ctk.CTkLabel(frame_info, text=texto_disco, font=ctk.CTkFont(size=14))
            lbl_disco.pack(anchor="w", padx=20)
        
        if datos['unidades_usb']: # muestra si hay USBs conectados
            label_usb = ctk.CTkLabel(frame_info, text=f"\nUSBs detectadas: {', '.join(datos['unidades_usb'])}", font=ctk.CTkFont(size=14, slant="italic"), text_color="green")
            label_usb.pack(anchor="w", pady=10)

    def mostrar_procesos(self):
        self.limpiar_pantalla()
        label = ctk.CTkLabel(self.main_view, text="Administrador de Procesos", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20)
        # aqui va el formulario para insertar P1, P2... y los botones  FIFO, SJF, RR
    
    def mostrar_archivos(self):
        self.limpiar_pantalla()
        label = ctk.CTkLabel(self.main_view, text="Administrador de Archivos (USB)", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20)
        # aqui va la logica para detectar la unidad F: y listar archivos
    
    
    