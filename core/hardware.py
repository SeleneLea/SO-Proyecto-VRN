import psutil
import platform

def optener_tipo_disco(unidad):
    return "SSD/HDD (Unidad de Disco)"

def obtener_info_sistema():
    memoria = psutil.virtual_memory()
    
    particiones = psutil.disk_partitions()
    detalles_discos = []
    total_hd_sistema = 0
    
    for p in particiones:
        if 'fixed' in p.opts: # solo discos internos no USBs
            try:
                uso = psutil.disk_usage(p.mountpoint)
                total_hd_sistema += uso.total
                detalles_discos.append({
                    "unidad": p.device,
                    "total_gb": round(uso.total / (1024 ** 3), 2),
                    "libre_gb": round(uso.free / (1024 ** 3), 2),
                })
            except:
                continue
    
    info = {
        "procesador": platform.processor(),
        "ram_total_gb": round(memoria.total / (1024 ** 3), 2),
        "ram_disponible_gb": round(memoria.available / (1024 ** 3), 2),
        "detalles_unidades": detalles_discos,
        "unidades_usb": [p.device for p in particiones if 'removable' in p.opts],
    }
    return info




def prueba_sistema():
    datos = obtener_info_sistema()
    print("--- INFORMACIÓN DEL SISTEMA ---")
    print(f"Procesador: {datos['procesador']}")
    print(f"RAM Total: {datos['ram_total_gb']} GB")
    print(f"RAM Disponible: {datos['ram_disponible_gb']} GB")
    print("\nUnidades de Disco Encontradas:")
    for d in datos['detalles_unidades']:
        print(f"  - {d['unidad']} | Tamaño: {d['total_gb']} GB | Libre: {d['libre_gb']} GB") 
    
    print(f"\nUSBs detectados: {datos['unidades_usb']}")


if __name__ == "__main__":
    prueba_sistema()
