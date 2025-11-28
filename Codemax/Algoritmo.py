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

    # Estructuras de control
    filas_activas = set(i for i, v in enumerate(ofertas_local) if v > eps)
    cols_activas = set(j for j, v in enumerate(demandas_local) if v > eps)

    asignaciones: List[Tuple[int, int, float, float]] = []
    coste_total = 0.0

    while filas_activas and cols_activas:
        lote_min = None
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
                if cantidad_asignable <= eps:
                    continue
                lote = costos_local[i][j] * cantidad_asignable
                if lote_min is None or lote < lote_min:
                    lote_min = lote
        if lote_min is None:
            break

        seleccionadas = []
        filas_buscar = set(filas_activas)
        cols_buscar = set(cols_activas)
        while True:
            encontrado = False
            val = 0.0
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
                        if not encontrado:
                            idxf, idxc = i, j
                            encontrado = True
                        else:
                            # Desempate
                            if costos_local[i][j] < costos_local[idxf][idxc] or (
                                costos_local[i][j] == costos_local[idxf][idxc]
                                and (i, j) < (idxf, idxc)
                            ):
                                idxf, idxc = i, j
            if not encontrado:
                break
            cantidad = min(ofertas_local[idxf], demandas_local[idxc])
            seleccionadas.append((idxf, idxc, cantidad, costos_local[idxf][idxc]))

            filas_buscar.discard(idxf)
            cols_buscar.discard(idxc)
            filas_activas.discard(idxf)
            cols_activas.discard(idxc)

        for isel, jsel, cant, cunit in seleccionadas:
            ofertas_local[isel] -= cant
            demandas_local[jsel] -= cant
            asignaciones.append((isel, jsel, cant, cunit))
            coste_total += cant * cunit
            if ofertas_local[isel] <= eps:
                filas_activas.discard(isel)
            if demandas_local[jsel] <= eps:
                cols_activas.discard(jsel)

    return asignaciones, coste_total
