import customtkinter as ctk
import tkinter as tk
from core.hardware import obtener_info_sistema
from core.hardware import obtener_ram_disponible
from tkinter import filedialog, messagebox
from core.procesos import algoritmo_fifo, algoritmo_sjf, algoritmo_rr, leer_txt
from core.memoria import AdminMemoria
# from core.memoria import obtener_tamano_proceso_real
from core.archivos import ApartadoArchivos, obtener_unidades_extraibles, listar_archivos



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
        self.btn_memoria = ctk.CTkButton(self.sidebar_frame, text="Memoria RAM", command=self.mostrar_memoria)
        self.btn_memoria.grid(row=4, column=0, padx=20, pady=10)
        
        # contenedor de vistas
        self.main_view = ctk.CTkFrame(self, corner_radius=10)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nswe")
        
        self.mostrar_hardware()
    
    def limpiar_pantalla(self): # antes de cambiar de seccion
        for widget in self.main_view.winfo_children():
            widget.destroy()
    
    
    
    #-------------------------------------------------------------------
    #---------------                          ---------------------------    
    # -------------- HARDWARE CARACTERISTICAS ---------------------------
    #---------------                          ---------------------------    
    #--------------------------------------------------------------------   
    
    
    def mostrar_hardware(self):
        self.limpiar_pantalla()
        info = obtener_info_sistema()
        
        self.frame_hardware = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.frame_hardware.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(self.frame_hardware, text="Caractetisticas del Equipo", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10,25))

        ctk.CTkLabel(self.frame_hardware, text="Procesador", font=ctk.CTkFont(size=18, weight="bold")).pack (anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.frame_hardware, text=info["procesador"], wraplength=700, justify="left").pack(anchor="w", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(self.frame_hardware, text="Memoria RAM",font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.frame_hardware, text=f"Total: {info['ram_total_gb']} GB").pack(anchor="w", padx=20)
        self.label_ram_disponible = ctk.CTkLabel(self.frame_hardware, text="Disponible: -- GB", font=ctk.CTkFont(size=15, weight="bold"))
        self.label_ram_disponible.pack(anchor="w", padx=20, pady=(0, 20))
        
        self.actualizar_ram()
        
        ctk.CTkLabel(self.frame_hardware, text="Almacenamiento", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 5))
        for d in info['detalles_unidades']:
            ctk.CTkLabel(self.frame_hardware, text=f"→ {d['unidad']} | Capacidad: {d['total_gb']} GB | Libre: {d['libre_gb']} GB", justify="left").pack(anchor="w", padx=20) 
            
        
    def actualizar_ram(self):
        ram = obtener_ram_disponible()
        self.label_ram_disponible.configure(text=f"Disponible: {ram} GB")
        self.after(1000, self.actualizar_ram) # 1000=1seg
        
        
        
    #-----------------------------------------------------------
    #---------------                 ---------------------------    
    # -------------- ADM DE PROCESOS ---------------------------
    #---------------                 ---------------------------    
    #-----------------------------------------------------------          
    
    def mostrar_procesos(self):
        self.limpiar_pantalla()
        if not hasattr(self, 'lista_procesos_memoria'):
            self.lista_procesos_memoria = []
        
        label_titulo = ctk.CTkLabel(self.main_view, text="Administrador de Procesos", font=ctk.CTkFont(size=24, weight="bold"))
        label_titulo.pack(pady=10)
        
        # secc import
        frame_top = ctk.CTkFrame(self.main_view)
        frame_top.pack(fill="x", padx=20, pady=10)
        
        btn_importar = ctk.CTkButton(frame_top, text="Importar .txt", width=100, command=self.importar_archivo_procesos, fg_color="#2c3e50")
        btn_importar.pack(side="left", padx=10)
        
        # button para limpiar
        ctk.CTkButton(frame_top, text="Volver a Empezar", fg_color="#60a759", hover_color="#6dab55", 
                    command=self.limpiar_datos).pack(side="left", padx=10)

        #self.label_status = ctk.CTkLabel(frame_top, text=f"{len(self.lista_procesos_memoria)} procesos en lista")
        #self.label_status.pack(side="left", padx=10)
        self.label_status = ctk.CTkLabel(frame_top, text="No hay procesos cargados")
        self.label_status.pack(side="left", padx=10)
        # secc import
        
        # formulario
        frame_form = ctk.CTkFrame(self.main_view)
        frame_form.pack(fill="x", padx=20, pady=10)
        self.entry_id = ctk.CTkEntry(frame_form, placeholder_text="ID (P1)", width=60)
        self.entry_id.grid(row=0, column=0, padx=5, pady=10)
        self.entry_llegada = ctk.CTkEntry(frame_form, placeholder_text="T. Llegada", width=80)
        self.entry_llegada.grid(row=0, column=1, padx=5, pady=10)
        self.entry_rafaga = ctk.CTkEntry(frame_form, placeholder_text="T. Rafaga", width=80)
        self.entry_rafaga.grid(row=0, column=2, padx=5, pady=10)
        btn_agregar = ctk.CTkButton(frame_form, text="+", fg_color="#2c3e50", width=40, command=self.agregar_proceso_manual)
        btn_agregar.grid(row=0, column=3, padx=5, pady=10)
        
        # algoritmos
        frame_btns = ctk.CTkFrame(self.main_view, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(frame_btns, text="Ejecutar FIFO", fg_color="#395bae", hover_color="#26438b", width=100, command=lambda: self.ejecutar_y_mostrar("FIFO")).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Ejecutar SJF", fg_color="#395bae", hover_color="#26438b", width=100, command=lambda: self.ejecutar_y_mostrar("SJF")).pack(side="left", padx=5)
        self.entry_q = ctk.CTkEntry(frame_btns, placeholder_text="Q", width=50)
        self.entry_q.pack(side="left", padx=(20,5))
        ctk.CTkButton(frame_btns, text="Ejecutar RR", fg_color="#395bae", hover_color="#26438b", width=100, command=lambda: self.ejecutar_y_mostrar("RR")).pack(side="left", padx=5)
        
    def importar_archivo_procesos(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if ruta:
            procesos = leer_txt(ruta)
            if procesos:
                self.lista_procesos_memoria = procesos
                self.label_status.configure(text=f"{len(procesos)} procesos cargados desde archivo")
            else:
                messagebox.showerror("Error", "El archivo no tiene el formato correcto")
    
    def agregar_proceso_manual(self):
        try:
            p = {
                'id': self.entry_id.get(),
                't_llegada': int(self.entry_llegada.get()),
                't_rafaga': int(self.entry_rafaga.get())
            }
            self.lista_procesos_memoria.append(p)
            self.label_status.configure(text=f"{len(self.lista_procesos_memoria)} procesos en la lista")
            self.entry_id.delete(0, 'end') # limpia campos
            self.entry_llegada.delete(0, 'end')
            self.entry_rafaga.delete(0, 'end')
        except ValueError:
            messagebox.showwarning("Atención", "Llegada y Ráfaga deben ser números")
    
    def ejecutar_y_mostrar(self, algoritmo):
        if not self.lista_procesos_memoria:
            messagebox.showwarning("Vacío", "No hay procesos para procesar")
            return
        # ejjecutar la logica segun el boton
        if algoritmo == "FIFO":
            resultado = algoritmo_fifo(self.lista_procesos_memoria)
            datos_gantt = resultado # FIFO/SJF devuelven la lista con inicio/fin
            tabla_datos = resultado
        elif algoritmo == "SJF":
            resultado = algoritmo_sjf(self.lista_procesos_memoria.copy())
            datos_gantt = resultado
            tabla_datos = resultado
        elif algoritmo == "RR":
            q = int(self.entry_q.get() if self.entry_q.get() else 2)
            resultado = algoritmo_rr(self.lista_procesos_memoria, q)
            datos_gantt = resultado['gantt']
            tabla_datos = resultado['tiempos']

        self.mostrar_resultados_visuales(tabla_datos, datos_gantt)
    
    def limpiar_datos(self):
        self.lista_procesos_memoria = []
        self.limpiar_pantalla()
        self.mostrar_procesos()
    
    def mostrar_resultados_visuales(self, tabla, gantt):
        # contenedor para resultados
        if hasattr(self, 'frame_resultados'):
            self.frame_resultados.destroy() # elimina si ya existe
            
        self.frame_resultados = ctk.CTkScrollableFrame(self.main_view, height=450)
        self.frame_resultados.pack(fill="both", expand=True, padx=20, pady=10)

            # cuadro datos inciales
        ctk.CTkLabel(self.frame_resultados, text="Datos de Entrada", font=("bold", 18)).pack(pady=(10, 5))
        f_entrada = ctk.CTkFrame(self.frame_resultados)
        f_entrada.pack(fill="x", padx=40)
        
        # titulos de columnas
        for i, txt in enumerate(["Proceso", "Tiempo Llegada", "Ráfaga de CPU"]):
            ctk.CTkLabel(f_entrada, text=txt, width=150, fg_color="#34495e", text_color="white").grid(row=0, column=i, padx=1, pady=1)

        # filas da tos
        for idx, p in enumerate(self.lista_procesos_memoria):
            ctk.CTkLabel(f_entrada, text=p['id'], width=150).grid(row=idx+1, column=0)
            ctk.CTkLabel(f_entrada, text=str(p['t_llegada']), width=150).grid(row=idx+1, column=1)
            ctk.CTkLabel(f_entrada, text=str(p['t_rafaga']), width=150).grid(row=idx+1, column=2)

        # diagrama GANTT
        ctk.CTkLabel(self.frame_resultados, text="\nDiagrama de Gantt", font=("bold", 18)).pack()      
        gantt_container = ctk.CTkFrame(self.frame_resultados, fg_color="transparent")
        gantt_container.pack(pady=15)
        
        fila_p = ctk.CTkFrame(gantt_container, fg_color="transparent")
        fila_p.pack()
        fila_t = ctk.CTkFrame(gantt_container, fg_color="transparent")
        fila_t.pack(fill="x")

        ctk.CTkLabel(fila_t, text="0", width=25, font=("bold", 12)).pack(side="left")        # escala y dibujo del Gantt

        for bloque in gantt:
            # multiplicamos la duracion para que el bloque sea visible proporcionalmente
            ancho_visual = max(bloque['fin'] - bloque['inicio'], 2) * 12 
            
            btn_bloque = ctk.CTkButton(fila_p, text=bloque['id'], width=ancho_visual, height=35, 
                                    corner_radius=0, state="disabled", fg_color="#2980b9", 
                                    text_color_disabled="white") # Bloque de Proceso 
            btn_bloque.pack(side="left", padx=0.5)
            
            # label de tiempo final
            ctk.CTkLabel(fila_t, text=str(bloque['fin']), width=ancho_visual, anchor="e").pack(side="left")

        # tabla TE y TR
        ctk.CTkLabel(self.frame_resultados, text="\nTabla de Resultados", font=("bold", 18)).pack(pady=(10, 5))
        f_res = ctk.CTkFrame(self.frame_resultados)
        f_res.pack(fill="x", padx=40)

        for i, txt in enumerate(["Proceso", "Espera (TE)", "Respuesta (TR)"]):
            ctk.CTkLabel(f_res, text=txt, width=150, fg_color="#27ae60", text_color="white").grid(row=0, column=i, padx=1, pady=1)

        for idx, r in enumerate(tabla):
            ctk.CTkLabel(f_res, text=r['id'], width=150).grid(row=idx+1, column=0)
            ctk.CTkLabel(f_res, text=str(r['t_espera']), width=150).grid(row=idx+1, column=1)
            ctk.CTkLabel(f_res, text=str(r['t_respuesta']), width=150).grid(row=idx+1, column=2)

        # proemedios TE y TR
        te_prom = sum(p['t_espera'] for p in tabla) / len(tabla)
        tr_prom = sum(p['t_respuesta'] for p in tabla) / len(tabla)
        
        frame_prom = ctk.CTkFrame(self.frame_resultados, fg_color="transparent")
        frame_prom.pack(pady=20)
        
        lbl_prom = ctk.CTkLabel(frame_prom, 
                                text=f"TEProm = {round(te_prom, 2)}   |   TRProm = {round(tr_prom, 2)}", 
                                font=("bold", 16), text_color="#d35400")
        lbl_prom.pack()
    
    def volver_empezar(lista_procesos, frame_tabla, canvas_gantt):
        lista_procesos.clear()
        for widget in frame_tabla.winfo_children():
            widget.destroy()
        if canvas_gantt:
            canvas_gantt.get_tk_widget().destroy()
        print("Sistema reiniciado")
    
    
    
    
    
    #-----------------------------------------------------------
    #---------------                 ---------------------------    
    # -------------- ADM DE ARCHIVOS ---------------------------
    #---------------                 ---------------------------    
    #-----------------------------------------------------------   
    
    
    def mostrar_archivos(self):
        self.limpiar_pantalla()
        
        self.vista_archivos = ApartadoArchivos(self.main_view)
        self.vista_archivos.pack(fill="both", expand=True, padx=20, pady=20)

    def actualizar_lista_archivos(self):
        self.lista_visual.delete(0, tk.END)
        if self.unidad_actual:
            archivos = listar_archivos(self.unidad_actual)
            for arc in archivos:
                self.lista_visual.insert(tk.END, f"  📁 {arc}" if os.path.isdir(os.path.join(self.unidad_actual, arc)) else f"  📄 {arc}")
    
    
    

    #------------------------------------------------------------
    #---------------                  ---------------------------    
    # --------------  ADM DE MEMORIA  ---------------------------
    #---------------                  ---------------------------    
    #------------------------------------------------------------   
    
    
    def mostrar_memoria(self):
        self.limpiar_pantalla()
        if not hasattr(self, 'mem_admin'):
            from core.memoria import AdminMemoria
            self.mem_admin = AdminMemoria()

        ctk.CTkLabel(self.main_view, text="MONITOR DE SISTEMA (GB)", font=("Consolas", 24, "bold")).pack(pady=10)

        # Frame principal con dos columnas
        self.frame_mon = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.frame_mon.pack(fill="both", expand=True, padx=20)

        # Columna izquierda: Estadísticas y lista de procesos
        frame_izq = ctk.CTkFrame(self.frame_mon, fg_color="transparent")
        frame_izq.pack(side="left", fill="both", expand=True, padx=10)

        self.lbl_stats = ctk.CTkLabel(frame_izq, text="", justify="left", font=("Consolas", 16))
        self.lbl_stats.pack(anchor="nw", pady=10)

        # Frame scrollable para la lista de procesos con botones
        ctk.CTkLabel(frame_izq, text="Procesos Activos:", font=("Consolas", 14, "bold")).pack(anchor="w", pady=(20, 5))
        self.frame_procesos_list = ctk.CTkScrollableFrame(frame_izq, height=300, fg_color="#2b2b2b")
        self.frame_procesos_list.pack(fill="both", expand=True, pady=5)

        # Columna derecha: Canvas de memoria
        self.canvas_m = ctk.CTkCanvas(self.frame_mon, bg="#1a1a1a", highlightthickness=0, width=350, height=520)
        self.canvas_m.pack(side="right", pady=10, padx=10)
        
        # Llamamos al loop de actualización
        self.actualizar_monitor_loop()

    def actualizar_monitor_loop(self):
        if not hasattr(self, 'canvas_m') or not self.canvas_m.winfo_exists():
            if hasattr(self, 'monitor_update_id'):
                self.monitor_update_id = None
            return

        self.mem_admin.actualizar_estado_real()
        m = self.mem_admin.obtener_metricas()
        
        # Contar procesos activos (excluyendo MONITOR y LIBRE)
        procesos_activos = sum(1 for b in m['MAPA'] if b['estado'] == 'ocupado')
        
        self.lbl_stats.configure(text=f"RAM TOTAL: {m['TOTAL_GB']} GB\n\n"
                                        f"PROCESOS: {procesos_activos}\n\n"
                                        f"MAX AVAIL: {m['MAX_AVAIL']} GB\n"
                                        f"MEM AVAIL: {m['MEM_AVAIL']} GB")

        # Actualizar lista de procesos con botones
        for widget in self.frame_procesos_list.winfo_children():
            widget.destroy()
        
        for bloque in m['MAPA']:
            if bloque['estado'] == 'ocupado':
                frame_proc = ctk.CTkFrame(self.frame_procesos_list, fg_color="#3a3a3a")
                frame_proc.pack(fill="x", pady=2, padx=5)
                
                # Nombre y memoria
                lbl_info = ctk.CTkLabel(frame_proc, 
                                    text=f"{bloque.get('nombre_corto', bloque['id'])}: {bloque['tamano']} GB",
                                    font=("Consolas", 12),
                                    anchor="w")
                lbl_info.pack(side="left", fill="x", expand=True, padx=10, pady=5)
                
                # Botón para terminar proceso
                es_protegido = bloque.get('protegido', False)
                btn_kill = ctk.CTkButton(frame_proc, 
                                        text="✕",
                                        width=30,
                                        height=25,
                                        fg_color="#e74c3c" if not es_protegido else "#95a5a6",
                                        hover_color="#c0392b" if not es_protegido else "#7f8c8d",
                                        command=lambda pids=bloque.get('pids', []), protegido=es_protegido, nombre=bloque.get('nombre_corto', ''): self.terminar_proceso(pids, protegido, nombre))
                btn_kill.pack(side="right", padx=5)

        self.canvas_m.delete("all")
        y_p = 0 # Empezamos desde el borde superior absoluto
        c_h = 520 
        ancho = 220
        
        for b in m['MAPA']:
            # Proporción exacta
            alto_px = (b['tamano'] / m['TOTAL_GB']) * c_h
            
            # Colores según tu diagrama
            if b['estado'] == 'sistema': col = "#E67E22" # Naranja (Monitor)
            elif b['estado'] == 'ocupado': col = "#3498DB" # Azul (Procesos P)
            else: col = "#27AE60" # Verde (Libre)

            # Dibujo del bloque
            self.canvas_m.create_rectangle(50, y_p, 50 + ancho, y_p + alto_px, 
                                        fill=col, outline="white", width=1)
            
            # Texto centrado - ajustar tamaño de fuente si hay muchos bloques
            if alto_px > 8:
                # Mostrar nombre real del proceso o ID si es sistema/libre
                texto_display = b.get('nombre_corto', b['id'])
                # Tamaño de fuente dinámico según altura del bloque
                font_size = max(7, min(9, int(alto_px / 4)))
                self.canvas_m.create_text(50 + ancho/2, y_p + alto_px/2, 
                                        text=texto_display, fill="white", font=("Arial", font_size, "bold"))
                self.canvas_m.create_text(50 + ancho + 40, y_p + alto_px/2, 
                                        text=f"{b['tamano']}G", fill="white", font=("Arial", 8))
            
            y_p += alto_px # El siguiente bloque se pega al final de este

        self.monitor_update_id = self.after(1000, self.actualizar_monitor_loop)
    
    def terminar_proceso(self, pids, protegido=False, nombre=''):
        """Termina todos los PIDs de un proceso agrupado"""
        import psutil
        from tkinter import messagebox
        
        if not pids:
            return
        
        # Si es un proceso protegido (Explorer), mostrar advertencia especial
        if protegido:
            respuesta = messagebox.askyesno(
                "Proceso Protegido", 
                f"'{nombre}' es el Explorador de Windows.\n\n"
                "Cerrar este proceso cerrará todas las ventanas de carpetas pero el shell se reiniciará automáticamente.\n\n"
                "¿Desea continuar?")
            if not respuesta:
                return
        
        terminados = 0
        errores = 0
        
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.terminate()  # Intenta cerrar normalmente
                terminados += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                errores += 1
                continue
        
        if terminados > 0:
            messagebox.showinfo("Proceso Terminado", 
                                f"Se terminaron {terminados} proceso(s) correctamente.")
        if errores > 0:
            messagebox.showwarning("Advertencia", f"No se pudieron terminar {errores} proceso(s). Puede que requieran permisos de administrador.")
    

