import sys
sys.path.append('..')

import pandas as pd
import numpy as np
import itertools

from pathlib import Path
from src.utils.constantes import PATH_FOLDER, PATH_FOLDER_MISC, ID_AGLOMERADOS, ID_REGIMEN_TENENCIA, DATASET_INDIVIDUALES
from src.responses.individuales import traducir_nivel_ed


def check_periodo (anio, trimestre):
    """
    Dado un año y un trimestre devuelve True si tanto el archivo de hogares como el de individuos
    existen para ese trimestre
    """
    hogar = 0
    individual = 0
    for archivo in  PATH_FOLDER.glob("*_hogar_?" + str(trimestre)+ str(anio)+".txt"):
        hogar= 1

    for archivo in  PATH_FOLDER.glob("*_individual_?" + str(trimestre)+ str(anio)+".txt"):
        individual= 1

    return hogar == individual

def check_archivo_faltante (anio, trimestre):
    """
    Dado un año y un trimestre devuelve vacio si ambos archivos existen. 
    En caso contrario devuelve el nombre del archivo faltante.
    """
    hogar = 0
    individual = 0
    resultado = ""
    for archivo in  PATH_FOLDER.glob("*_hogar_?" + str(trimestre)+ str(anio)+".txt"):
        hogar= 1

    for archivo in  PATH_FOLDER.glob("*_individual_?" + str(trimestre)+ str(anio)+".txt"):
        individual= 1

    if  hogar == individual:
        if (hogar==0) and (individual== 0):
            resultado="Ambos archivos faltantes."
    else:
        if (hogar==0):
            resultado="Archivo hogares faltante."
        if (individual==0):
            resultado="Archivo individuos faltante."
    return resultado

def periodos_disponibles():
    """
    Devuelve una lista ordenada de Tuplas con todos las combinaciones de año-trimestre 
    existentes.
    """
    #estructura de datos para guardar los años
    años_trimestres = set()
    
    for archivo in PATH_FOLDER.glob("*.txt"):

        #tomo los ultimos 4 sin tomar la extesion
        partes_nombre= archivo.name[:-4].split('_')
        periodo = partes_nombre[2]
        años_trimestres.add(periodo)

    año_trimestre_separado =list( map(lambda x:  (x[2:] ,x[1:2]) , años_trimestres))

    años_trimestre_ordenado = sorted(año_trimestre_separado, key=lambda item: (int(item[0]),int(item[1])), reverse=True)
    return años_trimestre_ordenado


def periodos_validos():
    """
    Devuelve una lista de Tuplas con todos las combinaciones de año-trimestre 
    que correspondan a periodos validos.
    """
    periodos = periodos_disponibles()

    return list(filter(lambda x: check_periodo(x[0],x[1]) , periodos))

def periodos_no_validos():
    """
    Devuelve una lista de Tuplas con todos las combinaciones de año-trimestre 
    que correspondan a periodos no validos.
    """
    periodos = periodos_disponibles()
    return list(filter(lambda x: not check_periodo(x[0],x[1]) , periodos))

def archivos_faltantes():
    """
    Devuelve una lista de Tuplas con todos las combinaciones de año-trimestre-archivo faltante
    que correspondan a periodos no validos.
    """
    periodos = periodos_disponibles()
    return list(map(lambda x: (x[0],x[1], check_archivo_faltante(x[0],x[1])), filter(lambda x: not check_archivo_faltante(x[0],x[1])=="" , periodos)))


def promedios_canasta_basica_por_trimestre(anio,trimestre):
    """
    Dado un año-trimestre devuelve la linea de pobreza promedio y la linea de indigencia promedio 
    que correspondan a periodos dado.
    """
    df = pd.read_csv(PATH_FOLDER_MISC / 'valores-canasta-basica-alimentos-canasta-basica-total-mensual-2016.csv')
    df['anio'] =  df.apply(lambda row: int(pd.to_datetime(row['indice_tiempo']).year), axis=1)
    df['trimestre'] =  df.apply(lambda row: int((pd.to_datetime(row['indice_tiempo']).month )- 1) // 3 + 1, axis=1)
    df_filtrado =  df[lambda df: (df['anio'] == anio) & (df['trimestre'] == trimestre)]  
    datos_calculados=df_filtrado[['linea_pobreza','linea_indigencia']].mean()
    return datos_calculados


def leer_archivo_año_trimestre(anio,trimestre,tipoarchivo):
    """
    tipoarchivo:
        0:hogar
        1:individuos
    Dado un año-trimestre devuelve un dataFrame con los valores del archivo
    del tipo solicitado para ese año /trimestre
    """
    if tipoarchivo == 0:
        str_buscar ="*_hogar_?" + str(trimestre)+ str(anio)[2:]+".txt"
    if tipoarchivo == 1:
        str_buscar ="*_individual_?" + str(trimestre)+ str(anio)[2:]+".txt"
    
    rutas =PATH_FOLDER.glob(str_buscar)
    df = pd.DataFrame() # Inicialización por defecto
    try:
        ruta_archivo = [Path(path) for path in rutas][0]
        df = pd.read_csv(ruta_archivo, sep=';',low_memory=False)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        print("No se cargo el archivo solicitado")
    except AttributeError as fnf_atri:
        print(fnf_atri)        
    except IndexError as fnf_index:
        print("No existe informacion para el periodo seleccionado")
    return df

def filtrar_hogares_por_anio(hogares, anio):
    """
    Filtra el DataFrame de hogares por año.
    """
    if anio != "Todos":
        hogares_filtrado = hogares[hogares["ANO4"] == anio]
    else:
        hogares_filtrado = hogares
    return hogares_filtrado

def cantidad_viviendas_por_año(hogares, anio):
    """
    Devuelve la cantidad de viviendas según el año seleccionado.
    Si anio es "Todos", usa todos los datos.
    """
    if "PONDERA" in hogares.columns:
        hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
        return hogares_filtrado["PONDERA"].sum()
    else:
        return "error"

def cantidad_viviendas_por_tipo(hogares, anio):
    """
    Retorna un DataFrame con las proporciones por tipo de vivienda en determinado anio.
    """
    hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
    if "TIPO_HOGAR" not in hogares_filtrado.columns:
        return
    else:
        # Agrupo por tipo de hogar y sumo las ponderaciones
        return hogares_filtrado.groupby("TIPO_HOGAR")["PONDERA"].sum()

def material_pisos_interiores(hogares):
    """
    Retorna un DataFrame con la cantidad de viviendas por material en los pisos interiores.
    Agrupa por material de piso interior (Columna: IV3), donde:
    1: "mosaico / baldosa / madera / cerámica / alfombra"
    2: "cemento / ladrillo fijo"
    3: "ladrillo suelto / tierra"
    """
    if "IV3" not in hogares.columns:
        return "error"
    else:
    # agrupo por material de piso interior (Columna IV3) y lo transformo a un dataframe con reset_index
        return hogares.groupby(["AGLOMERADO", "IV3"])["PONDERA"].sum().reset_index()

def mapeo_aglomerados(df):
    """Mapea los ID de aglomerados a sus respectivos nombres."""
    # transformo los ID de aglomerados a enteros
    id_aglomerados_int = {int(k): v for k, v in ID_AGLOMERADOS.items()}
    if "AGLOMERADO" not in df.columns:
        return "error"
    else:
        # mapeo los ID de aglomerados a nombres
        df["NOMBRE_AGLOMERADO"] = df["AGLOMERADO"].map(id_aglomerados_int)
        return df

def material_pisos_interiores_aglomerados(hogares, anio):
    """
    Retorna un DataFrame con la cantidad de viviendas por material predominante en los pisos interiores.
    """
    # filtro los hogares por el año seleccionado:
    hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
    # agrupo por aglomerado y material de piso interior
    hogares_material = material_pisos_interiores(hogares_filtrado)
    # busco el material predominante por aglomerado:
    ## para eso busco los index de los maximos de PONDERA por aglomerado con idxmax
    ## y luego filtro el dataframe original por esos index
    columnas_necesarias = ["AGLOMERADO", "IV3", "PONDERA"]
    if not all(col in hogares_material.columns for col in columnas_necesarias):
        return
    else:
        hogares_material = hogares_material.loc[hogares_material.groupby("AGLOMERADO")["PONDERA"].idxmax()]
        
        # diccionario para mapear los ID de pisos interiores a nombres:
        id_pisos_interiores = {1: "mosaico / baldosa / madera / cerámica / alfombra",
                            2: "cemento / ladrillo fijo",
                            3: "ladrillo suelto / tierra",
                            4: "otro material"}
        # mapeo los ID de pisos interiores a nombres
        hogares_material["NOMBRE_PISO_INTERIOR"] = hogares_material["IV3"].map(id_pisos_interiores)
        # mapeo los ID de aglomerados a nombres
        hogares_material = mapeo_aglomerados(hogares_material)
        # cambio el orden de las columnas:
        nuevo_orden = ["AGLOMERADO", "NOMBRE_AGLOMERADO", "NOMBRE_PISO_INTERIOR", "PONDERA"]
        hogares_material = hogares_material[nuevo_orden]
        return hogares_material

def viviendas_con_banio_aglomerados(hogares, anio):
    """
    Retorna un DataFrame con la proporción de viviendas que disponen de baño dentro del hogar
    por aglomerado en el año seleccionado.
    """
    columnas_necesarias = ["AGLOMERADO", "IV8", "PONDERA"]
    # filtro los hogares por el año seleccionado:
    hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
    if not all(col in hogares_filtrado.columns for col in columnas_necesarias):
        return
    else:
        # calculo la cantidad total de viviendas por aglomerado
        total_viviendas = hogares_filtrado.groupby("AGLOMERADO")["PONDERA"].sum()
        # calculo la cantidad de viviendas con baño (IV8 == 1)
        viviendas_con_banio = hogares_filtrado[hogares_filtrado["IV8"]== 1].groupby("AGLOMERADO")["PONDERA"].sum()
        # calculo la proporción
        tabla_proporcion = (viviendas_con_banio / total_viviendas * 100).reset_index()
        # renombro las columnas
        tabla_proporcion.columns = ["AGLOMERADO", "PROPORCION_BANIO"]
        # mapeo los ID de aglomerados a nombres:
        tabla_proporcion = mapeo_aglomerados(tabla_proporcion)
        # cambio el orden de las columnas:
        nuevo_orden = ["AGLOMERADO", "NOMBRE_AGLOMERADO", "PROPORCION_BANIO"]
        tabla_proporcion = tabla_proporcion[nuevo_orden]
        return tabla_proporcion

def mapear_regimen_tenencia(df):
    """Mapea los ID de régimen de tenencia a sus respectivos nombres."""
    df["NOMBRE_REGIMEN"] = df["II7"].map(ID_REGIMEN_TENENCIA)
    return df

def regimen_tenencia_viviendas(hogares):
    """
    Retorna un DataFrame con la cantidad de viviendas por régimen de tenencia de la vivienda.
    Agrupa por régimen de tenencia (Columna: II7), donde:
    1 = Propietario de la vivienda y el terreno
    2 = Propietario de la vivienda solamente
    3 = Inquilino / arrendatario de la vivienda
    4 = Ocupante por pago de impuestos  / expensas
    5 = Ocupante en relación de dependencia
    6 = Ocupante gratuito (con permiso)
    7 = Ocupante de hecho (sin permiso)
    8 = Está en sucesión
    9 = Otro
    """
    regimenes = list(ID_REGIMEN_TENENCIA.keys())
    # filtro el df para previnir errores de opciones como nulos o diferentes de 1,2,3,4,5,6,7,8,9
    hogares = hogares[hogares["II7"].notnull() & (hogares["II7"].isin(regimenes))]
    
    # agrupo por régimen de tenencia (Columna II7) y lo transformo a un dataframe con reset_index
    hogares_rt = hogares.groupby(["ANO4","TRIMESTRE","AGLOMERADO","II7"])["PONDERA"].sum().reset_index()
    
    # Obtengo todos los valores únicos
    anios = hogares_rt['ANO4'].unique()
    trimestres = hogares_rt['TRIMESTRE'].unique()
    aglomerados = hogares_rt['AGLOMERADO'].unique()
    
    # Creo un DataFrame con todas las combinaciones de año, trimestre y aglomerado
    combinaciones = list(itertools.product(anios, trimestres, aglomerados, regimenes))
    df_combinaciones = pd.DataFrame(combinaciones, columns=['ANO4', 'TRIMESTRE', 'AGLOMERADO', 'II7'])    
    
    # Uno con el DataFrame original para asegurar que todos los regímenes estén presentes
    hogares_rt = df_combinaciones.merge(
        hogares_rt, 
        on=['ANO4', 'TRIMESTRE', 'AGLOMERADO', 'II7'], 
        how='left'
    )
    
    # Relleno los valores NaN con 0
    hogares_rt['PONDERA'] = hogares_rt['PONDERA'].fillna(0)
    
    # Mapeo los ID de régimen de tenencia a nombres
    hogares_rt = mapear_regimen_tenencia(hogares_rt)

    return hogares_rt


def regimen_tenencia_viviendas_aglomerados(hogares, anio, aglomerado, regimenes_seleccionados="Todos"):
    """
    Retorna un DataFrame con la cantidad de viviendas por régimen de tenencia de la vivienda
    para un aglomerado específico en un año determinado.
    """
    columnas_necesarias = ["ANO4", "TRIMESTRE", "AGLOMERADO", "II7", "PONDERA"]
    if not all(col in hogares.columns for col in columnas_necesarias):
        return
    # filtro los hogares por el año seleccionado:
    hogares_anio = filtrar_hogares_por_anio(hogares, anio)

    # filtro por aglomerado:
    hogares_aglomerado = hogares_anio[hogares_anio["AGLOMERADO"] == aglomerado]

    # agrupo por régimen de tenencia:
    hogares_rt = regimen_tenencia_viviendas(hogares_aglomerado)

    if anio != "Todos":
        # Agrupo por trimestre y régimen
        hogares_rt = hogares_rt.groupby(['TRIMESTRE','II7','NOMBRE_REGIMEN'])['PONDERA'].sum().reset_index()
        # Calculo el total por trimestre
        total_por_trimestre = hogares_rt.groupby('TRIMESTRE')['PONDERA'].sum()
        # Calculo la proporción
        hogares_rt['PROPORCION'] = hogares_rt.apply(
            lambda x: (x['PONDERA'] / total_por_trimestre[x['TRIMESTRE']]) * 100, 
            axis=1 # para aplicar la función fila por fila
        ).round(2)
    else:
        # Agrupo por año y régimen
        hogares_rt = hogares_rt.groupby(['ANO4','II7','NOMBRE_REGIMEN'])['PONDERA'].sum().reset_index()
        # Calculo el total por año
        total_por_anio = hogares_rt.groupby('ANO4')['PONDERA'].sum()
        # Calculo la proporción
        hogares_rt['PROPORCION'] = hogares_rt.apply(
            lambda x: (x['PONDERA'] / total_por_anio[x['ANO4']]) * 100, 
            axis=1
        ).round(2)

    # Filtrar por regímenes de tenencia seleccionados
    if regimenes_seleccionados != "Todos":
        hogares_rt = hogares_rt[hogares_rt['II7'].isin(regimenes_seleccionados)]
    return hogares_rt

def viviendas_en_villa_emergencia(hogares, anio):
    """
    Retorna un DataFrame con la cantidad de viviendas en villas de emergencia por aglomerado
    en el año seleccionado.
    Un hogar se considera en villa de emergencia si la columna IV12_3 es igual a 1.
    """
    columnas_necesarias = ["AGLOMERADO", "IV12_3", "PONDERA"]
    if not all(col in hogares.columns for col in columnas_necesarias):
        return

    # filtro los hogares por el año seleccionado:
    hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
    
    # total de viviendas por aglomerado
    total_viviendas_aglomerado = hogares_filtrado.groupby("AGLOMERADO")["PONDERA"].sum().reset_index()
    
    # filtro las viviendas en villas de emergencia (IV12_3 == 1)
    total_villa_emergencia = hogares_filtrado[hogares_filtrado["IV12_3"] == 1]

    # agrupo por aglomerado y sumo las ponderaciones
    hogares_ve = total_villa_emergencia.groupby("AGLOMERADO")["PONDERA"].sum().reset_index()
    hogares_ve = hogares_ve.rename(columns={"PONDERA": "CANTIDAD"})

    # Calculo el porcentaje de viviendas en villas de emergencia
    hogares_ve["PORCENTAJE"] = (hogares_ve["CANTIDAD"] / total_viviendas_aglomerado["PONDERA"] * 100).round(2)

    # mapeo los ID de aglomerados a nombres
    hogares_ve = mapeo_aglomerados(hogares_ve)
    # cambio el orden de las columnas
    nuevo_orden = ["AGLOMERADO", "NOMBRE_AGLOMERADO", "CANTIDAD", "PORCENTAJE"]
    hogares_ve = hogares_ve[nuevo_orden]

    return hogares_ve.sort_values(by="PORCENTAJE", ascending=True)

def porcentaje_condicion_habitabilidad(hogares,anio):
    """
    Retorna un DataFrame con el porcentaje de hogares en condiciones de habitabilidad
    por aglomerado en el año seleccionado.
    Opciones de la columna CONDICION_DE_HABITABILIDAD:
    insuficiente, regular, saludables y buena.
    """
    columnas_necesarias = ["ANO4", "AGLOMERADO", "CONDICION_DE_HABITABILIDAD", "PONDERA"]
    if not all(col in hogares.columns for col in columnas_necesarias):
        return

    # filtro los hogares por el año seleccionado:
    hogares_filtrado = filtrar_hogares_por_anio(hogares, anio)
    
    # total de viviendas por aglomerado
    total_viviendas_aglomerado = hogares_filtrado.groupby("AGLOMERADO")["PONDERA"].sum().reset_index()
    
    # agrupo por condición de habitabilidad y aglomerado
    condicion_habitabilidad = hogares_filtrado.groupby(["AGLOMERADO", "CONDICION_DE_HABITABILIDAD"])["PONDERA"].sum().reset_index()

    
    # Calculo la proporción
    condicion_habitabilidad['PORCENTAJE'] = condicion_habitabilidad.apply(
        lambda x: (x['PONDERA'] / total_viviendas_aglomerado[total_viviendas_aglomerado['AGLOMERADO'] == x['AGLOMERADO']]['PONDERA'].values[0]) * 100,
        axis=1
    ).round(2)

    # mapeo los ID de aglomerados a nombres
    condicion_habitabilidad = mapeo_aglomerados(condicion_habitabilidad)

    # renombrar las columnas:
    condicion_habitabilidad = condicion_habitabilidad.rename(columns={"PONDERA": "CANTIDAD"})
    # cambio el orden de las columnas
    nuevo_orden = ["AGLOMERADO", "NOMBRE_AGLOMERADO", "CONDICION_DE_HABITABILIDAD", "CANTIDAD", "PORCENTAJE"]
    condicion_habitabilidad = condicion_habitabilidad[nuevo_orden]
    return condicion_habitabilidad

def obtener_pea(df_individuos):
    """
    Obtiene la Población Económicamente Activa (PEA) del DataFrame de individuos.
    La PEA incluye a las personas que están ocupadas o desocupadas.
    """
    df_individuos = df_individuos.copy()
    df_individuos['ESTADO'] = df_individuos['ESTADO'].astype(str).str.strip()
    pea = int(df_individuos[df_individuos['ESTADO'].isin(['1', '2'])]['PONDERA'].sum())
    return pea

def obtener_desocupados(df_individuos):
    """
    Obtiene la cantidad de personas desocupadas del DataFrame de individuos.
    """
    df_individuos = df_individuos.copy()
    df_individuos['ESTADO'] = df_individuos['ESTADO'].astype(str).str.strip()
    desocupados = int(df_individuos[df_individuos['ESTADO'] == '2']['PONDERA'].sum())
    return desocupados

def obtener_ocupados(df_individuos):
    """
    Obtiene la cantidad de personas desocupadas del DataFrame de individuos.
    """
    df_individuos = df_individuos.copy()
    df_individuos['ESTADO'] = df_individuos['ESTADO'].astype(str).str.strip()
    ocupados = int(df_individuos[df_individuos['ESTADO'] == '1']['PONDERA'].sum())
    return ocupados

def clasificar_empleo(df_individuos):
    """
    Clasifica el empleo de los individuos en el DataFrame.
    """
    df_individuos = df_individuos.copy()
    df_individuos['PP04A'] = pd.to_numeric(df_individuos['PP04A'], errors='coerce').astype('Int64')
    # Clasificación de empleo
    empleo_estatal = int(df_individuos[df_individuos['PP04A'] == 1]['PONDERA'].sum())
    empleo_privado = int(df_individuos[df_individuos['PP04A'] == 2]['PONDERA'].sum())
    otro_tipo = int(df_individuos[df_individuos['PP04A'] == 3]['PONDERA'].sum())
    
    return empleo_estatal, empleo_privado, otro_tipo

def tasa_empleo_desempleo(df_individuos, categoria):
    """
    Calcula la tasa laboral del DataFrame de individuos.
    La tasa laboral es la suma de ocupados y desocupados sobre la PEA.
    """
    pea = obtener_pea(df_individuos)
    # Segun la categoría, calcular la tasa correspondiente
    if categoria == 'Empleo':
        # Filtrar individuos ocupados
        ocupados = obtener_ocupados(df_individuos)
        # Calcular la tasa de empleo
        if pea > 0:
            tasa_empleo = round((ocupados / pea) * 100, 2)
        else:
            tasa_empleo = 0
        return tasa_empleo
    if categoria == 'Desempleo':
        # Filtrar individuos desocupados
        desocupados = obtener_desocupados(df_individuos)
        # Calcular la tasa de desempleo
        if pea > 0:
            tasa_desempleo = round((desocupados / pea) * 100, 2)
        else:
            tasa_desempleo = 0
        return tasa_desempleo
    
# P5 Punto 1.5.1
def cantidad_desocupados_estudios(anio, trimestre):
    """
    1.5.1 Para las personas desocupadas, informar la cantidad de ellas según sus estudios
    alcanzados. Se debe informar para un año y trimestre elegido por el usuario.
    """
    # Llamo a la funcion traducir_nivel_ed para agregar la columna Nivel_ed_str
    traducir_nivel_ed()
    #Declaro el dataframe
    df_individuos = df_individuos = pd.read_csv(DATASET_INDIVIDUALES, encoding='utf-8', low_memory=False)
    # Filtro por año y trimestre que indico el usuario
    df_individuos = df_individuos[(df_individuos['ANO4'] == anio) & (df_individuos['TRIMESTRE'] == trimestre)] 
    
    # Filtrar los individuos que están desocupados y sumando 'PONDERA'
    df_desocupados = df_individuos[df_individuos['ESTADO'] == 2]
    resultado = df_desocupados.groupby('NIVEL_ED_str')['PONDERA'].sum().reset_index()
    # Renombrar columnas para más claridad
    resultado.rename(columns={'NIVEL_ED_str': 'Nivel educativo', 'PONDERA': 'Cantidad personas'}, inplace=True) 
    return resultado

#Parte 2 (P5) 1.5.2 y 1.5.3
def evolucion_laboral(categoria, aglomerado=None):
    """
    Informar la evolución de empleo o desempleo a lo largo del tiempo. Se
    debe poder filtrar por aglomerado y en caso de no elegir ninguno se debe calcular para todo
    el país.
    """
    # estructura para guardar la informacion y luego mostrar
    evolucion = {
        'Periodo': [],
        'Tasa' : []
    }
    #Obtengo los periodos disponibles
    periodos_disp = periodos_disponibles()
    periodos = [(f"20{a.zfill(2)}", t) for a, t in periodos_disp]
    # Iterar sobre los periodos disponibles
    for anio, trimestre in periodos:
        # Leer el archivo de datos de individuos
        df_individuos = leer_archivo_año_trimestre(anio, trimestre, 1)
        # Filtrar por aglomerado si se especifica
        if aglomerado is not None:
            aglomerado = int(aglomerado)
            df_individuos['AGLOMERADO'] = df_individuos['AGLOMERADO'].astype(int)
            df_individuos = df_individuos[df_individuos['AGLOMERADO'] == aglomerado].copy()
        else:
            df_individuos = df_individuos.copy()
        # Calculos según categoria
        if categoria == 'Empleo':    
            # Calcular tasa de empleo
            tasa_empleo = tasa_empleo_desempleo(df_individuos, categoria)
            # Agregar al resultado
            evolucion['Periodo'].append(f"{anio}/{trimestre}")
            evolucion['Tasa'].append(tasa_empleo)
        if categoria == 'Desempleo':
            # Calcular la tasa de desempleo
            tasa_desempleo = tasa_empleo_desempleo(df_individuos, categoria)
            # Agregar al resultado
            evolucion['Periodo'].append(f"{anio}/{trimestre}")
            evolucion['Tasa'].append(tasa_desempleo)
    # Convertir a DataFrame
    df_evolucion = pd.DataFrame(evolucion)
    # Ordenar por periodo de forma ascendente para armar un grafico que muestre la evolucion
    return df_evolucion.sort_values(by='Periodo', ascending=True)

# Parte 2 (P5) 1.5.5
def variacion_laboral(categoria):
    """
    1.5.5 Se debe obtener por aglomerado el porcentaje de la tasa de empleo y 
    desempleo. Esta información se requiere conocer para el año y trimestre más 
    antiguo del cual se contenga información y para el año y trimestre más actual 
    del cual se cuenta información.
    A partir de dicha información se debe visualizar un mapa que por aglomerado muestre con
    el color de un punto/marca si el porcentaje aumentó o disminuyó. El usuario elegirá si desea
    ver tasa de empleo o desempleo:
    """
    # Estructura para almacenar los resultados
    datos = {
        'AGLOMERADO': [],
        'Nombre': [],
        'Tasa Inicio': [],
        'Tasa Fin': [],
        'Variación': [],
        }
    #Busco el primer y último periodo de datos disponibles
    periodos_disp = periodos_disponibles()
    periodos = [(f"20{a.zfill(2)}", t) for a, t in periodos_disp]
    periodos_ordenados = sorted(periodos, key=lambda x: (x[0], x[1]))
    periodo_inicio = periodos_ordenados[0]
    df_inicio = leer_archivo_año_trimestre(periodo_inicio[0], periodo_inicio[1], 1)
    periodo_fin = periodos_ordenados[-1]
    df_fin = leer_archivo_año_trimestre(periodo_fin[0], periodo_fin[1], 1)

    # recorro por aglomerados tanto en inicio como en fin
    for aglomerado in ID_AGLOMERADOS.keys():
        # Filtrar por aglomerado
        df_inicio['AGLOMERADO'] = df_inicio['AGLOMERADO'].astype(int)
        df_fin['AGLOMERADO'] = df_fin['AGLOMERADO'].astype(int)
        df_aglomerado_inicio = df_inicio[df_inicio['AGLOMERADO'] == int(aglomerado)]
        df_aglomerado_fin = df_fin[df_fin['AGLOMERADO'] == int(aglomerado)]
        
        # Calculo las tasas de empleo o desempleo para el periodo de inicio y fin
        tasa_inicio = tasa_empleo_desempleo(df_aglomerado_inicio, categoria)
        tasa_fin = tasa_empleo_desempleo(df_aglomerado_fin, categoria)
        variacion_tasa = ((tasa_fin - tasa_inicio) / tasa_inicio) * 100 if tasa_inicio != 0 else 0
        # guardo los datos en el dataframe
        datos['AGLOMERADO'].append(str(aglomerado))
        datos['Nombre'].append(ID_AGLOMERADOS[aglomerado])
        datos['Tasa Inicio'].append(tasa_inicio)
        datos['Tasa Fin'].append(tasa_fin)
        datos['Variación'].append(round(variacion_tasa, 2))
    # Convertir a DataFrame
    df_variacion = pd.DataFrame(datos)
    return df_variacion


# Parte 2 (P5) 1.5.4
def ocupacion_por_aglomerado():
    """
    1.5.4 Informar para cada aglomerado el total de personas ocupadas, el porcentaje con
    empleo estatal, el porcentaje con empleo privado y el porcentaje de otro tipo. Considerar la
    ocupación principal.
    """
    ocupacion = {
        'AGLOMERADO': [],
        'Total Ocupados': [],
        'Empleo Estatal': [],
        'Empleo Privado': [],
        'Otro Tipo': []
        }
    
    # Leer el archivo de individuos
    df_individuos = pd.read_csv(DATASET_INDIVIDUALES, encoding='utf-8', low_memory=False)
    # Asegurarse de que la columna 'AGLOMERADO' sea de tipo string
    df_individuos['AGLOMERADO'] = df_individuos['AGLOMERADO'].astype(int)
    # Agrupar por aglomerado y calcular el total de ocupados
    for aglomerado in df_individuos['AGLOMERADO'].unique():
        df_aglomerados = df_individuos[df_individuos['AGLOMERADO'] == aglomerado]
        # Obtener el total de ocupados en el aglomerado
        total_ocupados = obtener_ocupados(df_aglomerados)
        if total_ocupados > 0:
            # Clasificar el empleo en estatal, privado y otro tipo
            empleo_estatal, empleo_privado, otro_tipo = clasificar_empleo(df_aglomerados)
            # Calcular los porcentajes
            ocupacion['AGLOMERADO'].append(aglomerado)
            ocupacion['Total Ocupados'].append(total_ocupados)
            ocupacion['Empleo Estatal'].append(round((empleo_estatal / total_ocupados) * 100, 2))
            ocupacion['Empleo Privado'].append(round((empleo_privado / total_ocupados) * 100, 2))
            ocupacion['Otro Tipo'].append(round((otro_tipo / total_ocupados) * 100, 2))
    return pd.DataFrame(ocupacion)

def hogares_segun_ingresos(anio,trimestre):
    """
    Dado un año y trimestre devuelve un dataframe con la cantidad de hogares por debajo de la linea de indigencia, 
    la cantidad de hogares por debajo de la linea de pobreza y la cantidad de hogares por sobre la linea de pobreza.
    De no existir informacion devuelve un dataframe vacio
    """
    hogares = {}
    try:
        promedios_canasta= promedios_canasta_basica_por_trimestre(anio,trimestre)
        df = leer_archivo_año_trimestre(anio,trimestre,0)

        if not df.empty:
            cantidad_hogares_total = df['PONDERA'].sum()

            #filtro hogares con 4 miembros y con ingresos totales por debajo de la linea de pobreza, pero por sobre la linea de indigencia
            hogares_bajo_lineapobreza =  df[ (df['IX_TOT'] == 4)  & (df['ITF'] <= promedios_canasta['linea_pobreza'] ) & (df['ITF'] > promedios_canasta['linea_indigencia'] ) ] 
            cantidad_hogares_pobreza = hogares_bajo_lineapobreza['PONDERA'].sum()

            #filtro hogares con 4 miembros y con ingresos totales por debajo de la linea de indigencia
            hogares_bajo_lineaindigencia =  df[ (df['IX_TOT'] == 4)  & (df['ITF'] <= promedios_canasta['linea_indigencia'] ) ] 
            cantidad_hogares_indigencia = hogares_bajo_lineaindigencia['PONDERA'].sum()
            cantidad_hogares_sobre_linea_pobreza = cantidad_hogares_total -cantidad_hogares_pobreza-cantidad_hogares_indigencia

            hogares = {
                'categorias': ['Hogares sobre la linea de pobreza', 'Hogares bajo la linea de pobreza', 'Hogares bajo la linea de indigencia'],
                'cantidad':[cantidad_hogares_sobre_linea_pobreza,cantidad_hogares_pobreza,cantidad_hogares_indigencia],
                '%':[
                    round((cantidad_hogares_sobre_linea_pobreza/ cantidad_hogares_total)*100,2)
                    ,round((cantidad_hogares_pobreza/ cantidad_hogares_total)*100,2)
                    ,round((cantidad_hogares_indigencia/ cantidad_hogares_total)*100,2)
                    ]
                                        
            }
    except Exception as e:
        print(f'la excepción fue {e}')
        print(f'La excepción es  {type(e).__name__}')       

    finally:
        resultado = pd.DataFrame.from_dict(hogares)
    return resultado
    
def asignar_grupos_edad(df, periodo, columna_edad, nombre_columna_resultado="grupos_de_edades"):
    """
    Asigna rangos de edad de 10 en 10 en una nueva columna del DataFrame.

    Parámetros:
        df: DataFrame original
        columna_edad: str - nombre de la columna que contiene las edades (ej. "CH06")
        nombre_columna_resultado: str - nombre de la columna resultante (por defecto "grupos_de_edades")

    Devuelve:
        El DataFrame con la nueva columna de grupos de edad ordenada.
    """

    df_filtrado = df[(df["ANO4"] == int(periodo[0])+2000) & (df["TRIMESTRE"] == int(periodo[1]))]
    df_filtrado = df_filtrado[df_filtrado["CH06"] != -1]    # Excluir filas donde CH06 es -1, ya que no son válidas para el análisis
    
    # Calcular el mínimo del grupo (ej: 20, 30, ...)
    grupo_min = (df_filtrado[columna_edad] // 10) * 10

    # Crear columna como "20-29", "30-39", ...
    df_filtrado[nombre_columna_resultado] = grupo_min.astype(str) + "-" + (grupo_min + 9).astype(str)

    # Ordenar los grupos correctamente
    categorias_ordenadas = sorted(grupo_min.unique())
    categorias_ordenadas = [f"{x}-{x+9}" for x in categorias_ordenadas]

    df_filtrado[nombre_columna_resultado] = pd.Categorical(
        df_filtrado[nombre_columna_resultado],
        categories=categorias_ordenadas,
        ordered=True
    )

    return df_filtrado

def clasificar_tramo(edad):
    if edad <= 14:
        return "Niños (0-14)"
    elif edad <= 64:
        return "Activos (15-64)"
    else:
        return "Jubilados (65+)"
    
def total_personas_nivel_educativo(anio):
    """
    Devuelve un DataFrame con la cantidad de personas por nivel educativo alcanzado (CH12),
    para un año determinado. Suma la columna PONDERA para obtener la cantidad.
    """
    niveles_educativos = {
        1: "Jardín / Preescolar",
        2: "Primario",
        3: "EGB",
        4: "Secundario",
        5: "Polimodal",
        6: "Terciario",
        7: "Universitario",
        8: "Posgrado Univ.",
        9: "Educación especial"
    }

    df_total = pd.DataFrame()

    for trimestre in range(1, 5):
        try:
            df = leer_archivo_año_trimestre(anio, trimestre,1)
            if not df.empty and "CH12" in df.columns:
                df_filtrado = df[df["CH12"].isin(niveles_educativos.keys())].copy()
                df_filtrado["Nivel Educativo"] = df_filtrado["CH12"].map(niveles_educativos)
                df_total = pd.concat([df_total, df_filtrado], ignore_index=True)
        except Exception as e:
            print(f"Error al procesar trimestre {trimestre}: {e}")

    if df_total.empty or "Nivel Educativo" not in df_total.columns:
        return pd.DataFrame(columns=["Nivel Educativo", "Total"])
    
    df_total["Codigo"] = df_total["CH12"]

    resultado = df_total.groupby(["Codigo", "Nivel Educativo"])["PONDERA"].sum().reset_index()
    resultado = resultado.rename(columns={"PONDERA": "Total"})
    resultado = resultado.sort_values(by="Codigo").reset_index(drop=True)
    resultado = resultado[["Nivel Educativo", "Total"]]

    return resultado

def periodos_disponibles_completo():
    """
    Devuelve una lista ordenada de Tuplas con (anio_completo, trimestre) como enteros.
    """
    años_trimestres = set()

    for archivo in PATH_FOLDER.glob("*.txt"):
        partes_nombre = archivo.name[:-4].split('_')
        periodo = partes_nombre[2]  # ejemplo: T122
        if len(periodo) == 4 and periodo.startswith("T"):
            trimestre = int(periodo[1])
            anio = int("20" + periodo[2:])
            años_trimestres.add((anio, trimestre))

    return sorted(list(años_trimestres), reverse=True)


def check_periodo_completo(anio, trimestre):
    """
    Verifica si existen archivos hogar e individuos para el periodo dado (anio int).
    """
    anio_corto = str(anio)[2:]

    hogar = any(PATH_FOLDER.glob(f"*_hogar_?{trimestre}{anio_corto}.txt"))
    indiv = any(PATH_FOLDER.glob(f"*_individual_?{trimestre}{anio_corto}.txt"))

    return hogar and indiv


def periodos_validos_completo():
    """
    Devuelve solo los periodos completos (hogar e individuos) como (anio, trimestre).
    """
    return list(filter(lambda x: check_periodo_completo(x[0], x[1]), periodos_disponibles_completo()))


def leer_archivo_individuos(anio, trimestre):
    """
    Lee el archivo de individuos dado un año (int) y trimestre.
    """
    anio_corto = str(anio)[2:]
    busqueda = f"*_individual_?{trimestre}{anio_corto}.txt"
    rutas = list(PATH_FOLDER.glob(busqueda))

    if not rutas:
        print(f"No se encontró archivo: {busqueda}")
        return pd.DataFrame()

    return pd.read_csv(rutas[0], sep=';', low_memory=False)


def nivel_educativo_mas_comun_por_edad():
    """
    Devuelve un DataFrame con el nivel educativo más común para
    personas agrupadas por rango etario.
    """
    niveles_educativos = {
        1: "Jardín / Preescolar",
        2: "Primario",
        3: "EGB",
        4: "Secundario",
        5: "Polimodal",
        6: "Terciario",
        7: "Universitario",
        8: "Posgrado Univ.",
        9: "Educación especial"
    }

    intervalos = [
        (20, 29, "20-29"),
        (30, 39, "30-39"),
        (40, 49, "40-49"),
        (50, 59, "50-59"),
        (60, 120, "60+")
    ]

    df_total = pd.DataFrame()

    for anio, trimestre in periodos_validos_completo():
        try:
            df = leer_archivo_individuos(anio, trimestre)
            if not df.empty and {"CH06", "CH12", "PONDERA"}.issubset(df.columns):
                df = df.copy()
                df = df[df["CH06"].notna() & df["CH12"].notna()]

                df["CH06"] = pd.to_numeric(df["CH06"], errors="coerce")
                df["CH12"] = pd.to_numeric(df["CH12"], errors="coerce")

                df = df[df["CH06"].between(20, 120)]
                df = df[df["CH12"].isin(niveles_educativos.keys())]

                def asignar_rango(edad):
                    for inf, sup, etiqueta in intervalos:
                        if inf <= edad <= sup:
                            return etiqueta
                    return None

                df["Rango Etario"] = df["CH06"].apply(asignar_rango)
                df["Nivel Educativo"] = df["CH12"].map(niveles_educativos)

                df_total = pd.concat([df_total, df], ignore_index=True)
        except Exception as e:
            print(f"Error en {anio}-{trimestre}: {e}")

    if df_total.empty:
        return pd.DataFrame(columns=["Rango Etario", "Nivel Educativo", "Personas"])
    
    agrupado = df_total.groupby(["Rango Etario", "Nivel Educativo"])["PONDERA"].sum().reset_index()
    agrupado = agrupado.rename(columns={"PONDERA": "Personas"})

    idx_max = agrupado.groupby("Rango Etario")["Personas"].idxmax()
    resultado = agrupado.loc[idx_max].reset_index(drop=True)

    return resultado

from collections import Counter

def ranking_aglomerados_universitarios():
    """
    Devuelve un DataFrame con los 5 aglomerados con mayor porcentaje de hogares
    con dos o más individuos con estudios universitarios o superiores finalizados,
    usando el par de archivos más recientes.
    """
    periodos = periodos_validos_completo()
    if not periodos:
        return pd.DataFrame()

    anio, trimestre = periodos[0]

    hogares = leer_archivo_año_trimestre(anio, trimestre, 0)
    individuos = leer_archivo_individuos(anio, trimestre)

    if hogares.empty or individuos.empty:
        return pd.DataFrame()

    total_hogares = hogares.groupby("AGLOMERADO")["PONDERA"].sum().to_dict()

    filtro = (individuos["CH12"].astype(float).isin([7, 8])) & (individuos["CH13"].astype(float) == 1)
    univ = individuos[filtro]

    univ["ID_HOGAR"] = univ["CODUSU"].astype(str) + "-" + univ["NRO_HOGAR"].astype(str)

    contador = Counter(univ["ID_HOGAR"])
    hogares_con_2plus = [hogar for hogar, cant in contador.items() if cant >= 2]

    info_hogar = univ.drop_duplicates(subset="ID_HOGAR")[["ID_HOGAR", "AGLOMERADO", "PONDERA"]]
    info_filtrada = info_hogar[info_hogar["ID_HOGAR"].isin(hogares_con_2plus)]

    total_2plus = info_filtrada.groupby("AGLOMERADO")["PONDERA"].sum()

    resultado = []
    for aglo in total_2plus.index:
        if aglo in total_hogares:
            porcentaje = (total_2plus[aglo] / total_hogares[aglo]) * 100
            resultado.append((aglo, porcentaje))

    df_resultado = pd.DataFrame(resultado, columns=["AGLOMERADO", "Porcentaje"])
    df_resultado = df_resultado.sort_values(by="Porcentaje", ascending=False).head(5)

    df_resultado = mapeo_aglomerados(df_resultado)
    df_resultado = df_resultado[["AGLOMERADO", "NOMBRE_AGLOMERADO", "Porcentaje"]]

    return df_resultado.reset_index(drop=True)

def porcentaje_alfabetismo_por_anio():
    """
    Devuelve un DataFrame con el porcentaje de personas mayores a 6 años
    que saben leer y escribir, agrupado por año.
    """
    df_total = pd.DataFrame()

    for anio, trimestre in periodos_validos_completo():
        try:
            df = leer_archivo_individuos(anio, trimestre)
            if df.empty or not {"CH06", "CH09", "PONDERA"}.issubset(df.columns):
                continue

            df = df[df["CH06"].notna() & df["CH09"].notna()]
            df["CH06"] = pd.to_numeric(df["CH06"], errors="coerce")
            df["CH09"] = pd.to_numeric(df["CH09"], errors="coerce")

            df = df[df["CH06"] > 6]             
            df = df[df["CH09"].isin([1, 2])]     

            df["AÑO"] = anio
            df_total = pd.concat([df_total, df], ignore_index=True)

        except Exception as e:
            print(f"Error en {anio}-{trimestre}: {e}")

    if df_total.empty:
        return pd.DataFrame(columns=["AÑO", "Sabe Leer y Escribir", "Porcentaje"])

    agrupado = df_total.groupby(["AÑO", "CH09"])["PONDERA"].sum().reset_index()

    alfabetismo_map = {1: "Sabe", 2: "No sabe"}
    agrupado["Sabe Leer y Escribir"] = agrupado["CH09"].map(alfabetismo_map)

    total_por_año = agrupado.groupby("AÑO")["PONDERA"].transform("sum")
    agrupado["Porcentaje"] = (agrupado["PONDERA"] / total_por_año * 100).round(2)

    return agrupado[["AÑO", "Sabe Leer y Escribir", "Porcentaje"]].sort_values(by=["AÑO", "Sabe Leer y Escribir"])


def alfabetismo_formato_barras():
    """
    Devuelve un DataFrame con columnas 'Sabe' y 'No sabe' por año,
    para graficar como barras dobles.
    """
    df = porcentaje_alfabetismo_por_anio()
    if df.empty:
        return pd.DataFrame()

    df_pivot = df.pivot(index="AÑO", columns="Sabe Leer y Escribir", values="Porcentaje").fillna(0)

    for col in ["Sabe", "No sabe"]:
        if col not in df_pivot.columns:
            df_pivot[col] = 0

    df_pivot = df_pivot[["Sabe", "No sabe"]]

    return df_pivot


def hogares_segun_ingresos(anio,trimestre,linea_pobreza,linea_indigencia,integrantes = 4):
    """
    Dado un año y trimestre devuelve un dataframe con la cantidad de hogares por debajo de la linea de indigencia, 
    la cantidad de hogares por debajo de la linea de pobreza y la cantidad de hogares por sobre la linea de pobreza.
    De no existir informacion devuelve un dataframe vacio.
    :Año: año requerido
    :trimestre : trimestre requerido
    :linea_pobreza: linea de pobreza promedio para el año/trimestre seleccionado
    :linea_indigencia:linea de indigencia promedio para el año/trimestre seleccionado
    :integrantes: parametro que indica la cantidad de integrantes por hogar tomado. El valor por defecto es 4 
    """

    hogares = {}
    try:
        
        df = leer_archivo_año_trimestre(anio,trimestre,0)

        if not df.empty:
            # filtro hogares con la cantidad de miembros deseados
            base_hogares= df[df['IX_TOT'] == integrantes]
            cantidad_hogares_total = base_hogares['PONDERA'].sum()
            # filtro hogares con 4 miembros y con ingresos totales por debajo de la linea de pobreza, pero por sobre la linea de indigencia
            hogares_bajo_lineapobreza =  base_hogares[(df['ITF'] <= linea_pobreza ) ] 
            cantidad_hogares_pobreza = hogares_bajo_lineapobreza['PONDERA'].sum()
            # filtro hogares con 4 miembros y con ingresos totales por debajo de la linea de indigencia
            hogares_bajo_lineaindigencia =  base_hogares[ (df['ITF'] <= linea_indigencia) ] 
            cantidad_hogares_indigencia = hogares_bajo_lineaindigencia['PONDERA'].sum()
            hogares = {
                'categorias': ['Hogares bajo la linea de pobreza', 'Hogares bajo la linea de indigencia'],
                'cantidad':[cantidad_hogares_pobreza,cantidad_hogares_indigencia],
                '%':[
                     round((cantidad_hogares_pobreza/ cantidad_hogares_total)*100,2)
                    ,round((cantidad_hogares_indigencia/ cantidad_hogares_total)*100,2)
                    ]
                                        
            }
    except Exception as e:
        print(f'la excepción fue {e}')
        print(f'La excepción es  {type(e).__name__}')       

    finally:
        resultado = pd.DataFrame.from_dict(hogares)
    return resultado


def hogares_segun_ingresos_por_aglomerado(anio,trimestre,linea_pobreza,linea_indigencia,integrantes = 4):
    """
    Dado un año y trimestre devuelve un dataframe con la cantidad de hogares por debajo de la linea de indigencia, 
    la cantidad de hogares por debajo de la linea de pobreza y la cantidad de hogares por sobre la linea de pobreza
    agrupado por aglomerado.
    De no existir informacion devuelve un dataframe vacio.
    :anio: año requerido
    :trimestre : trimestre requerido
    :linea_pobreza: linea de pobreza promedio para el año/trimestre seleccionado
    :linea_indigencia:linea de indigencia promedio para el año/trimestre seleccionado
    :integrantes: parametro que indica la cantidad de integrantes por hogar tomado. El valor por defecto es 4 
    """

    try:
        df = leer_archivo_año_trimestre(anio,trimestre,0)
        df_indigencia = df[(df['ITF'] <= linea_indigencia )].groupby(["AGLOMERADO"])["PONDERA"].sum()
        df_pobreza = df[(df['ITF'] <= linea_pobreza )].groupby(["AGLOMERADO"])["PONDERA"].sum()
        df_result = pd.merge(df_indigencia, df_pobreza, on='AGLOMERADO',how='outer').reset_index()
    except Exception as e:
        df_result= pd.DataFrame.from_dict({})
    return df_result