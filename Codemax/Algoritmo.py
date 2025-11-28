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
            costos_local.append([0.0] * len(demandas_local))
        else:
            # Agregar fict_col con demanda = diferencia
            diff = sum_of - sum_de
            demandas_local.append(diff)
            for r in range(len(costos_local)):
                if len(costos_local[r]) < len(demandas_local) - 1:
                    costos_local[r].extend(
                        [0.0] * (len(demandas_local) - 1 - len(costos_local[r]))
                    )
                costos_local[r].append(0.0)

    n_cols = len(demandas_local)
    for r in range(len(costos_local)):
        if len(costos_local[r]) < n_cols:
            costos_local[r].extend([0.0] * (n_cols - len(costos_local[r])))
        elif len(costos_local[r]) > n_cols:
            costos_local[r] = costos_local[r][:n_cols]

    asignaciones: List[Tuple[int, int, float, float]] = []
    coste_total = 0.0

    # Estructuras de control
    filas_activas = set(i for i, v in enumerate(ofertas_local) if v > eps)
    cols_activas = set(j for j, v in enumerate(demandas_local) if v > eps)

    while filas_activas and cols_activas:
        # Si queda una sola fila/columna, asignar lo restante y terminar
        if len(filas_activas) == 1 or len(cols_activas) == 1:
            if len(filas_activas) == 1:
                i = next(iter(filas_activas))
                for j in sorted(cols_activas):
                    if ofertas_local[i] <= eps or demandas_local[j] <= eps:
                        continue
                    cant = min(ofertas_local[i], demandas_local[j])
                    asignaciones.append((i, j, cant, costos_local[i][j]))
                    coste_total += cant * costos_local[i][j]
                    ofertas_local[i] -= cant
                    demandas_local[j] -= cant
                    if demandas_local[j] <= eps:
                        cols_activas.discard(j)
                filas_activas.discard(i)
            else:
                j = next(iter(cols_activas))
                for i in sorted(filas_activas):
                    if ofertas_local[i] <= eps or demandas_local[j] <= eps:
                        continue
                    cant = min(ofertas_local[i], demandas_local[j])
                    asignaciones.append((i, j, cant, costos_local[i][j]))
                    coste_total += cant * costos_local[i][j]
                    ofertas_local[i] -= cant
                    demandas_local[j] -= cant
                    if ofertas_local[i] <= eps:
                        filas_activas.discard(i)
                cols_activas.discard(j)

            filas_activas = set(i for i in filas_activas if ofertas_local[i] > eps)
            cols_activas = set(j for j in cols_activas if demandas_local[j] > eps)
            continue  # Volver a comprobar condicion del while

        # 1) Construir matriz por lotes y encontrar si hay celdas asignables
        asignable = False
        for i in list(filas_activas):
            if i < 0 or i >= len(ofertas_local) or ofertas_local[i] <= eps:
                filas_activas.discard(i)
                continue
            for j in list(cols_activas):
                if j < 0 or j >= len(demandas_local) or demandas_local[j] <= eps:
                    cols_activas.discard(j)
                    continue
                # Proteccion dimensional
                if i >= len(costos_local) or j >= len(costos_local[i]):
                    continue
                cantidad_asignable = min(ofertas_local[i], demandas_local[j])
                if cantidad_asignable > eps:
                    asignable = True
                    break
            if asignable:
                break
        if not asignable:
            break

        # 2) Seleccionar todos las celdas con lotes minimos
        seleccionadas = []
        filas_buscar = set(filas_activas)
        cols_buscar = set(cols_activas)
        while True:
            lote_min = None
            for i in list(filas_buscar):
                if ofertas_local[i]<=eps:
                    filas_buscar.discard(i)
                    continue
                for j in list(cols_buscar):
                    if demandas_local[j]<=eps:
                        cols_buscar.discard(j)
                        continue
                    if i >= len(costos_local)or j>=len(costos_local[i]):
                        continue
                    cantidad_asignable=min(ofertas_local[i],demandas_local[j])
                    if cantidad_asignable<=eps:
                        continue
                    lote=costos_local[i][j]*cantidad_asignable
                    if lote_min is None or lote<lote_min:
                        lote_min=lote
            if lote_min is None:
                break

            encontrada = False
            idxf = -1
            idxc = -1
            # Criterio de desempate: menor coste unitario, luego menor (i,j)
            for i in list(filas_buscar):
                if ofertas_local[i] <= eps:
                    filas_buscar.discard(i)
                    continue
                for j in list(cols_buscar):
                    if demandas_local[j] <= eps:
                        cols_buscar.discard(j)
                        continue
                    if i >= len(costos_local) or j >= len(costos_local[i]):
                        continue
                    cantidad_asignable = min(ofertas_local[i], demandas_local[j])
                    if cantidad_asignable <= eps:
                        continue
                    lote = costos_local[i][j] * cantidad_asignable
                    if abs(lote - lote_min) <= 1e-12:
                        # Candidato valido; aplicar desempate
                        if not encontrada:
                            idxf, idxc = i, j
                            encontrada = True
                        else:
                            # Desempate
                            if costos_local[i][j] < costos_local[idxf][idxc] or (
                                costos_local[i][j] == costos_local[idxf][idxc]
                                and (i, j) < (idxf, idxc)
                            ):
                                idxf, idxc = i, j
            if not encontrada:
                break
            cantidad = min(ofertas_local[idxf], demandas_local[idxc])
            seleccionadas.append((idxf, idxc, cantidad, costos_local[idxf][idxc]))

            filas_buscar.discard(idxf)
            cols_buscar.discard(idxc)
            filas_activas.discard(idxf)
            cols_activas.discard(idxc)

        # 3) Actualizar ofertas/demandas
        for isel, jsel, cant, cunit in seleccionadas:
            ofertas_local[isel] -= cant
            demandas_local[jsel] -= cant
            asignaciones.append((isel, jsel, cant, cunit))
            coste_total += cant * cunit
            if ofertas_local[isel] <= eps:
                filas_activas.discard(isel)
            if demandas_local[jsel] <= eps:
                cols_activas.discard(jsel)

        # 4) Reconstruir matriz por lotes con filas/columnas validas
        filas_activas = set(
            i for i in range(len(ofertas_local)) if ofertas_local[i] > eps
        )
        cols_activas = set(
            j for j in range(len(demandas_local)) if demandas_local[j] > eps
        )

    return asignaciones, coste_total
