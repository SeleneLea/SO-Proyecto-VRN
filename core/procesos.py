import pandas as pd
from collections import deque
import copy

def calcular_promedios(tiempos):
    total_espera = sum(t['espera'] for t in tiempos)
    total_respuesta = sum(t['respuesta'] for t in tiempos)
    n = len(tiempos)
    return {
        'promedio_espera': round(total_espera / n, 2),
        'promedio_respuesta': round(total_respuesta / n, 2)
    }

def calcular_tiempos_estandar(lista_procesos):
    tiempo_actual = 0
    tr_anterior = 0
    resultados = []
    
    for p in lista_procesos:
        inicio = max(tiempo_actual, p['t_llegada']) #evita tiempos negativos
        fin = inicio + p['t_rafaga']       
        t_espera = inicio - p['t_llegada']
        t_respuesta = fin - p['t_llegada']
        #t_respuesta = p['t_rafaga'] + tr_anterior
        
        resultados.append({
            'id': p['id'],
            'inicio': inicio,
            'fin': fin,
            't_espera': t_espera,
            't_respuesta': t_respuesta
        })
        
        tr_anterior = t_respuesta
        tiempo_actual = fin 
    return resultados

def algoritmo_fifo(proceso):
    procesos_ordenados = sorted(proceso, key=lambda x: x['t_llegada'])
    return calcular_tiempos_estandar(procesos_ordenados)

def algoritmo_sjf(proceso):
    pendientes = copy.deepcopy(proceso)
    procesos_ejecutados = []
    tiempo_actual = 0
    
    while pendientes:
        # filtro
        disponibles = [p for p in pendientes if p['t_llegada'] <= tiempo_actual]
        
        if not disponibles:
            # si nadie ha llagado saltamos al t de llegada del siguiente
            tiempo_actual = min(p['t_llegada'] for p in pendientes)
            continue
        
        # elige el de menor rafaga
        proceso_elegido = min(disponibles, key=lambda x: (x['t_rafaga'], x['t_llegada']))
        pendientes.remove(proceso_elegido)
        procesos_ejecutados.append(proceso_elegido) 

        tiempo_actual += proceso_elegido['t_rafaga']

    return calcular_tiempos_estandar(procesos_ejecutados)


def algoritmo_rr(proceso, q):
    cola = deque()
    pendientes = sorted(proceso, key=lambda x: x['t_llegada'])
    tiempo_actual = pendientes[0]['t_llegada'] if pendientes else 0
    gantt = []
    rafaga_restante = {p['id']: p['t_rafaga'] for p in proceso}
    fin_proceso = {}
    
    while pendientes and pendientes[0]['t_llegada'] <= tiempo_actual:
        cola.append(pendientes.pop(0))
        
    while cola:   # mientras haya procesos en la cola
        p = cola.popleft()
        inicio = tiempo_actual
        ejecucion = min(q, rafaga_restante[p['id']])
        rafaga_restante[p['id']] -= ejecucion
        tiempo_actual += ejecucion
        
        gantt.append({
            'id': p['id'], 
            'inicio': inicio, 
            'fin': tiempo_actual
            })
        
        # Llegó alguien mientras el CPU estaba ocupado?
        while pendientes and pendientes[0]['t_llegada'] <= tiempo_actual:
            cola.append(pendientes.pop(0))
        
        if rafaga_restante[p['id']] > 0:
            cola.append(p)
        else:
            fin_proceso[p['id']] = tiempo_actual
        
    #calculo final
    tiempos = []
    for p in proceso:
        t_respuesta = fin_proceso[p['id']]
        t_espera = (t_respuesta - p['t_llegada']) - p['t_rafaga']
        
        tiempos.append({
            'id': p['id'],
            't_espera': t_espera,
            't_respuesta': t_respuesta
        })
        
    return {
        'gantt': gantt,
        'tiempos': tiempos
    }


def leer_txt(ruta_archivo):
    procesos = []
    try:
        with open(ruta_archivo, 'r') as f:
            for linea in f:
                # separar por comas o espacios
                partes = linea.strip().replace(',', ' ').split()
                if len(partes) >= 3:
                    procesos.append({
                        'id': partes[0],
                        't_llegada': int(partes[1]),
                        't_rafaga': int(partes[2])
                    })
        return procesos
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []





def dibujar_gantt_terminal(gantt):
    fila_proceso = "|"
    fila_tiempos = "0"
    
    for bloques in gantt:
        id_p = bloques['id']
        duracion = bloques['fin'] - bloques['inicio']
        espacio = " " * (duracion + 1) #ajustamos el espacio
        fila_proceso += f"{id_p}{espacio}|"
        fila_tiempos += f"{' ' * (len(id_p) + duracion)}{bloques['fin']}"
    
    print("\nDIAGRAMA DE GANTT:")
    print("-" * len(fila_proceso))
    print(fila_proceso)
    print("-" * len(fila_proceso))
    print(fila_tiempos)

if __name__ == "__main__":
    datos_ejercicio = [
        {'id': 'P1', 't_llegada': 0, 't_rafaga': 10},
        {'id': 'P2', 't_llegada': 2, 't_rafaga': 12},
        {'id': 'P3', 't_llegada': 4, 't_rafaga': 5},
        {'id': 'P4', 't_llegada': 3, 't_rafaga': 6},
        {'id': 'P5', 't_llegada': 1, 't_rafaga': 24}
    ]
    # --- PRUEBA FIFO ---
    res_fifo = algoritmo_fifo(datos_ejercicio)
    print("\n--- FIFO ---")
    dibujar_gantt_terminal(res_fifo) # FIFO/SJF la lista ya tiene inicio/fin

    # --- PRUEBA SJF ---
    res_sjf = algoritmo_sjf(datos_ejercicio)
    print("\n--- SJF ---")
    dibujar_gantt_terminal(res_sjf)

    # --- PRUEBA ROUND ROBIN ---
    res_rr = algoritmo_rr(datos_ejercicio, 4)
    print("\n--- ROUND ROBIN (Q=4) ---")
    dibujar_gantt_terminal(res_rr['gantt']) # en RR usamos la llave 'gantt'

    def imprimir_resultados(nombre, resultados):
        print(f"\n--- RESULTADOS {nombre} ---")
        # Si es RR, los resultados vienen dentro de una llave 'tiempos'
        lista = resultados if isinstance(resultados, list) else resultados['tiempos']
        
        suma_espera = 0
        suma_respuesta = 0
        
        for r in lista:
            print(f"Proceso {r['id']} | Espera = {r['t_espera']} | Respuesta = {r['t_respuesta']}")
            suma_espera += r['t_espera']
            suma_respuesta += r['t_respuesta']
        
        n = len(lista)
        print(f"Promedio Espera: {round(suma_espera / n, 2)}")
        print(f"Promedio Respuesta: {round(suma_respuesta / n, 2)}")

    # probar FIFO
    res_fifo = algoritmo_fifo(datos_ejercicio)
    imprimir_resultados("FIFO", res_fifo)

    # probar SJF
    res_sjf = algoritmo_sjf(datos_ejercicio)
    imprimir_resultados("SJF", res_sjf)
    
    # probar RR con q=4
    res_rr = algoritmo_rr(datos_ejercicio, 4)
    imprimir_resultados("ROUND ROBIN (q=4)", res_rr)

