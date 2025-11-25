from typing import List, Tuple, Dict


def resolver_transporte(
    costos: List[List[float]], ofertas: List[float], demandas: List[float]
) -> Tuple[List[Tuple[int, int, float, float]], float]:
    """
    Entrada:
        - costos: matriz m x n de costes unitarios
        - ofertas: lista de longitud m
        - demandas: lista de longitud n
    Salida:
        - asignaciones: lista de tuplas (i, j, cantidad asignada, coste unitario)
        - coste_total: suma(cantidad_asignada * coste_unitario)
    Comportamiento:
        - Balancea auto. añadiendo oferta/demanda ficticia si suma(ofertas) != suma(demandas)
        - Algoritmo CODEMAX
    """

    m = len(ofertas)
    n = len(demandas)
    sum_of = sum(ofertas)
    sum_de = sum(demandas)

    costos_local = [row[:] for row in costos]
    ofertas_local = ofertas[:]
    demandas_local = demandas[:]

    # Balanceo
    fict_row = False
    fict_col = False
    if abs(sum_of - sum_de) > 1e-9:
        if sum_of < sum_de:
            # Agregar fict_row con oferta = diferencia
            diff = sum_de - sum_of
            ofertas_local.append(diff)
            costos_local.append([0.0] * n)
            m += 1
            fict_row = True
        else:
            # Agregar fict_col con demanda = diferencia
            diff = sum_of - sum_de
            demandas_local.append(diff)
            for r in range(m):
                costos_local[r].append(0.0)
            n += 1
            fict_col = True

    # Estructuras de control
    filas_activas = set(range(m))
    cols_activas = set(range(n))

    asignaciones = []
    coste_total = 0.0

    while filas_activas and cols_activas:
        minimo = None
        for i in filas_activas:
            for j in cols_activas:
                if ofertas_local[i] <= 0 or demandas_local[j] <= 0:
                    continue
                c = costos_local[i][j]
                if minimo is None or c < minimo[0]:
                    minimo = (c, i, j)
        if minimo is None:
            break
        coste_unit, io, jd = minimo
        cantidad = min(ofertas_local[io], demandas_local[jd])
        asignaciones.append((io, jd, cantidad, coste_unit))
        coste_total += cantidad * coste_unit
        ofertas_local[io] -= cantidad
        demandas_local[jd] -= cantidad

        # Eliminar filas/columnas satisfechas
        eps = 1e-9
        if ofertas_local[io] <= eps:
            filas_activas.discard(io)
        if demandas_local[jd] <= eps:
            cols_activas.discard(jd)

    return asignaciones, coste_total
