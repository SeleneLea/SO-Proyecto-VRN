import psutil
import win32gui
import win32process
import ctypes

# Mapeo de nombres técnicos a nombres amigables
NOMBRES_AMIGABLES = {
    'msedgewebview': 'Edge WebView',
    'msedge': 'Microsoft Edge',
    'chrome': 'Google Chrome',
    'firefox': 'Mozilla Firefox',
    'code': 'VS Code',
    'explorer': 'Explorador',
    'discord': 'Discord',
    'spotify': 'Spotify',
    'teams': 'Microsoft Teams',
    'outlook': 'Outlook',
    'excel': 'Excel',
    'word': 'Word',
    'powerpnt': 'PowerPoint',
    'notepad': 'Bloc de Notas',
    'whatsapp': 'WhatsApp',
    'telegram': 'Telegram',
    'slack': 'Slack',
    'zoom': 'Zoom',
    'obs64': 'OBS Studio',
    'steam': 'Steam',
    'epicgameslauncher': 'Epic Games',
    'python': 'Python',
    'pycharm64': 'PyCharm',
    'idea64': 'IntelliJ IDEA',
    'vlc': 'VLC Media Player',
    'winrar': 'WinRAR',
    '7zfm': '7-Zip',
    'gimp': 'GIMP',
    'photoshop': 'Photoshop',
    'illustrator': 'Illustrator',
    'whatsapp root': 'WhatsApp',
    'systeminfocp': 'SysInfo',
    'phoneexperienc': 'Phone Link',
    'memcompressio': 'Mem Compress',
    'systemsetting': 'Config',
}

def obtener_procesos_con_ventanas():
    """
    Detecta programas con ventanas activas usando pywin32.
    Retorna un diccionario con PID -> nombre amigable del proceso.
    """
    procesos_ventanas = {}
    
    def callback(hwnd, extra):
        """Callback para enumerar todas las ventanas."""
        try:
            # Obtener PID del proceso que posee la ventana
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Filtrar ventanas invisibles/minimizadas
            if not win32gui.IsWindowVisible(hwnd):
                return True
            
            # Obtener el nombre de la ventana
            window_text = win32gui.GetWindowText(hwnd)
            
            # Solo registrar si tiene título visible (ventana real, no oculta)
            if window_text and window_text.strip():
                if pid not in procesos_ventanas:
                    try:
                        proc = psutil.Process(pid)
                        nombre = proc.name()
                        procesos_ventanas[pid] = nombre
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except:
            pass
        
        return True
    
    # Enumerar todas las ventanas
    win32gui.EnumWindows(callback, None)
    return procesos_ventanas

def es_proceso_primer_plano(nombre):

    """
    Detecta si un proceso es potencialmente de primer plano basándose en su nombre.
    Filtra procesos típicos de segundo plano y servicios.
    """
    nombre_lower = nombre.lower()
    
    # Procesos que SIEMPRE son de segundo plano aunque consuman memoria
    segundo_plano = [
        'applicationframehost',
        'backgroundtaskhost',
        'conhost',
        'csrss',
        'dashost',
        'lsass',
        'services',
        'smss',
        'spoolsv',
        'wininit',
        'winlogon',
        'audiodg',
        'dllhost',
        'securityhealthservice',
        'sg_service',
        'unsecapp',
        'sqlservr',           # SQL Server
        'sqlwriter',          # SQL Writer
        'mssql',              # SQL Server Service
        'systemsettingsbroker',
        'startmenuexperiencehost',
        'memcompression',
        'registry',
        'vmmem',              # WSL memoria
        'sysinfocap',
        'phoneexperience',    # Sincronización de teléfono
        'systeminformation',
        'textinputhost',      # Teclado táctil
        'lockapp',            # Pantalla de bloqueo
    ]
    
    return not any(bg in nombre_lower for bg in segundo_plano)

class AdminMemoria:
    def __init__(self):
        self.bloques = []
        self.total_gb = 0
        self.procesos_activos = {}  # Diccionario con PIDs de procesos activos
        self.actualizar_estado_real()

    def actualizar_estado_real(self):
        """
        Actualiza el estado de la memoria basándose en ventanas detectadas por pywin32.
        pywin32: Detecta qué programas están abiertos (ventanas activas).
        psutil: Solo proporciona el peso en RAM de cada programa.
        """
        # Obtener RAM total del sistema (solo psutil)
        mem = psutil.virtual_memory()
        self.total_gb = round(mem.total / (1024**3), 2)
        
        # MONITOR: Bloque fijo inicial (sistema operativo)
        uso_sistema = 1.5 
        
        # Detectar procesos con ventanas abiertas usando pywin32
        procesos_con_ventanas = obtener_procesos_con_ventanas()
        
        # Agrupar procesos por nombre
        procesos_agrupados = {}  # Diccionario para agrupar por nombre
        procesos_pids = {}  # Guardar PIDs para poder terminarlos después
        
        # Lista negra: procesos críticos del sistema que no son "aplicaciones"
        ignore = ['svchost.exe', 'searchhost.exe', 'runtimebroker.exe', 
                    'shellexperiencehost.exe', 'taskhostw.exe', 
                    'msmpeng.exe', 'system', 'registry', 'dwm.exe', 
                    'ctfmon.exe', 'sihost.exe', 'fontdrvhost.exe',
                    'searchapp.exe',  # Búsqueda de Windows
                    'textinputhost.exe']  # Teclado táctil
        
        # Solo procesar PIDs que tienen ventanas abiertas (detectados por pywin32)
        for pid, nombre_proceso in procesos_con_ventanas.items():
            try:
                # Validar que tenga nombre
                if not nombre_proceso or nombre_proceso.strip() == '':
                    continue
                
                name_lower = nombre_proceso.lower()
                
                # FILTRO 1: Evitar procesos del sistema
                if name_lower in ignore:
                    continue
                
                # FILTRO 2: Solo procesos de primer plano (basado en nombre)
                # Si tiene ventana abierta (detectada por pywin32), asumimos que es relevante
                if not es_proceso_primer_plano(nombre_proceso):
                    continue
                
                # Obtener peso del proceso usando psutil (SOLO para datos)
                try:
                    proc = psutil.Process(pid)
                    p_gb = round(proc.memory_info().rss / (1024**3), 2)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
                # FILTRO 3: Consumo mínimo más permisivo (0.05 GB = 50 MB)
                # Permite herramientas pequeñas con ventanas
                if p_gb <= 0.05:
                    continue
                
                # Agrupar por nombre de proceso
                nombre_base = nombre_proceso.replace('.exe', '').replace('.EXE', '').strip()
                
                # Validar que el nombre base no esté vacío
                if not nombre_base:
                    continue
                
                # FILTRO ESPECIAL EXPLORER: Solo mostrar si tiene ventanas de carpetas abiertas
                if nombre_base.lower() == 'explorer' and p_gb < 0.2:
                    continue
                
                if nombre_base not in procesos_agrupados:
                    procesos_agrupados[nombre_base] = 0
                    procesos_pids[nombre_base] = []
                
                procesos_agrupados[nombre_base] += p_gb
                procesos_pids[nombre_base].append(pid)
                    
            except Exception as e:
                continue
        
        # Guardar PIDs de procesos activos
        self.procesos_activos = {nombre: pids for nombre, pids in procesos_pids.items()}
        
        # Convertir a lista ordenada por consumo (de mayor a menor)
        procesos_reales = []
        contador = 1
        
        for nombre, memoria_total in sorted(procesos_agrupados.items(), 
                                            key=lambda x: x[1], reverse=True):
            memoria_redondeada = round(memoria_total, 2)
            
            # Buscar nombre amigable en el diccionario
            nombre_lower = nombre.lower()
            nombre_amigable = NOMBRES_AMIGABLES.get(nombre_lower, nombre)
            
            # Acortar si es necesario
            nombre_corto = nombre_amigable[:14] if len(nombre_amigable) > 14 else nombre_amigable
            
            # Marcar si es Explorer (protegido - no se puede cerrar completamente)
            es_explorer = nombre.lower() == 'explorer'
            
            procesos_reales.append({
                'id': f"P{contador}",
                'tamano': memoria_redondeada,
                'estado': 'ocupado',
                'nombre': nombre_amigable,
                'nombre_corto': nombre_corto,
                'pids': procesos_pids.get(nombre, []),
                'protegido': es_explorer  # No se puede terminar el shell de Windows
            })
            contador += 1

        # Reconstrucción del mapa de memoria
        nuevo_mapa = [{'id': 'MONITOR', 'tamano': uso_sistema, 'estado': 'sistema'}]
        nuevo_mapa.extend(procesos_reales)
        
        consumo_total = sum(b['tamano'] for b in nuevo_mapa)
        libre_gb = round(self.total_gb - consumo_total, 2)
        
        # El espacio libre se ajusta dinámicamente
        # Cuando cierras un proceso, su memoria pasa a LIBRE
        if libre_gb > 0:
            nuevo_mapa.append({'id': 'LIBRE', 'tamano': libre_gb, 'estado': 'libre'})
            
        self.bloques = nuevo_mapa

    def obtener_metricas(self):
        libres = [b['tamano'] for b in self.bloques if b['estado'] == 'libre']
        val_libre = sum(libres)
        return {
            'TOTAL_GB': self.total_gb,
            'MEM_AVAIL': round(val_libre, 2),
            'MAX_AVAIL': round(max(libres), 2) if libres else 0,
            'MAPA': self.bloques
        }
    

