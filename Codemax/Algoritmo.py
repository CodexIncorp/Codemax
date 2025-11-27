from typing import List, Tuple


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
        - Balancea auto. agregando oferta/demanda ficticia si suma(ofertas) != suma(demandas)
        - Algoritmo CODEMAX
    """

    m = len(ofertas)
    n = len(demandas)
    costos_local = [row[:] for row in costos]
    ofertas_local = ofertas[:]
    demandas_local = demandas[:]

    sum_of = sum(ofertas_local)
    sum_de = sum(demandas_local)
    eps = 1e-9

    # Balanceo
    if abs(sum_of - sum_de) > eps:
        if sum_of < sum_de:
            # Agregar fict_row con oferta = diferencia
            diff = sum_de - sum_of
            ofertas_local.append(diff)
            costos_local.append([0.0] * n)
            m += 1
        else:
            # Agregar fict_col con demanda = diferencia
            diff = sum_of - sum_de
            demandas_local.append(diff)
            for r in range(m):
                if len(costos_local[r]) < n:
                    costos_local[r].extend([0.0] * (n - len(costos_local[r])))
                costos_local[r].append(0.0)
            n += 1
    for r in range(len(costos_local)):
        if len(costos_local[r]) < n:
            costos_local[r].extend([0.0] * (n - len(costos_local[r])))
        elif len(costos_local[r]) > n:
            costos_local[r] = costos_local[r][:n]

    # Estructuras de control
    filas_activas = set(i for i in range(len(ofertas_local)) if ofertas_local[i] > eps)
    cols_activas = set(j for j in range(len(demandas_local)) if demandas_local[j] > eps)

    asignaciones = []
    coste_total = 0.0

    while filas_activas and cols_activas:
        encontrado = False
        val = 0.0
        idxf = 0
        idxc = 0
        for i in list(filas_activas):
            if i < 0 or i >= len(ofertas_local):
                filas_activas.discard(i)
                continue
            if ofertas_local[i] <= eps:
                filas_activas.discard(i)
                continue
            for j in list(cols_activas):
                if j < 0 or j >= len(demandas_local):
                    cols_activas.discard(j)
                    continue
                if demandas_local[j] <= eps:
                    cols_activas.discard(j)
                    continue
                if i >= len(costos_local) or j >= len(costos_local[i]):
                    continue
                cantidad_asignable = min(ofertas_local[i], demandas_local[j])
                if cantidad_asignable <= eps:
                    continue
                lote = costos_local[i][j] * cantidad_asignable

                if not encontrado:
                    val = lote
                    idxf = i
                    idxc = j
                    encontrado = True
                else:
                    if (
                        lote < val
                        or (
                            abs(lote - val) <= 1e-12
                            and costos_local[i][j] < costos_local[idxf][idxc]
                        )
                        or (
                            abs(lote - val) <= 1e-12
                            and costos_local[i][j] == costos_local[idxf][idxc]
                            and (i, j) < (idxf, idxc)
                        )
                    ):
                        val = lote
                        idxf = i
                        idxc = j
        if not encontrado:
            break
        cantidad = min(ofertas_local[idxf], demandas_local[idxc])
        asignaciones.append((idxf, idxc, cantidad, costos_local[idxf][idxc]))
        coste_total += cantidad * costos_local[idxf][idxc]

        ofertas_local[idxf] -= cantidad
        demandas_local[idxc] -= cantidad

        if ofertas_local[idxf] <= eps:
            filas_activas.discard(idxf)
        if demandas_local[idxc] <= eps:
            cols_activas.discard(idxc)

    return asignaciones, coste_total
