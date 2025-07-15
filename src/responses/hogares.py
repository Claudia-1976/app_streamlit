import csv
from src.utils.constantes import DATASET_HOGARES,DATASET_INDIVIDUALES
from collections import Counter
from src.utils.funciones_csv import abrir_archivo_csv


# SECCION A:
## Sección A punto 7:
def agregar_tipo_hogar():
    """
    Agrega la columna 'TIPO_HOGAR' al archivo dataset_hogares.csv
    basado en la cantidad de personas en la columna 'IX_TOT'.

    """
    data_updated = []

    lector , header = abrir_archivo_csv(DATASET_HOGARES)

    # Verifico si ya existe la columna TIPO_HOGAR en el archivo:
    if "TIPO_HOGAR" in header:
        return print("La columna 'TIPO_HOGAR' ya existe en el archivo.")
            
    # Agregar el encabezado de la nueva columna
    header.append("TIPO_HOGAR")
    data_updated.append(header)

    # Me guardo indice de la col IX_TOT
    ix_tot_index = header.index("IX_TOT")

    # Procesar las filas y agregar la nueva columna
    for fila in lector:
        cantidad_personas = int(fila[ix_tot_index])
        if cantidad_personas == 1:
            tipo_hogar = "Unipersonal"
        elif 2 <= cantidad_personas <= 4:
            tipo_hogar = "Nuclear"
        else:
            tipo_hogar = "Extendido"
        
        fila.append(tipo_hogar)
        data_updated.append(fila)

    # actualización del archivo dataset_hogares con la nueva columna
    abrir_archivo_csv(DATASET_HOGARES, Write=True, data=data_updated)


    print(f"Se agregó la columna 'TIPO_HOGAR' al archivo {DATASET_HOGARES}")

## Sección A punto 8:
def agregar_material_techumbre():
    """
    Agrega la columna 'MATERIAL_TECHUMRE' al archivo dataset_hogares.csv
    basado en los valores de la columna 'IV4'.

    """
    data_updated = []

    lector , header = abrir_archivo_csv(DATASET_HOGARES)
    #print(f"Encabezado original: {header}")

    #Verifico si ya existe la columna MATERIAL_TECHUMBRE en el archivo:
    if "MATERIAL_TECHUMBRE" in header:
        return print("La columna 'MATERIAL_TECHUMBRE' ya existe en el archivo.")
            
    # Agregar el encabezado de la nueva columna
    header.append("MATERIAL_TECHUMBRE")
    data_updated.append(header)

    # Me guardo indice de la col IV4
    iv4_index = header.index("IV4")

    # Procesar las filas y agregar la nueva columna
    for fila in lector:
        if fila[iv4_index] != '':
            valor = int(fila[iv4_index])
            if 1 <= valor <= 4:
                material_techumbre = "Material durable"
            elif 5 <= valor <= 7:
                material_techumbre = "Material precario"
            elif valor == 9:
                material_techumbre = "No aplica"
        else:
            material_techumbre = "Sin informacion"            
        fila.append(material_techumbre)
        data_updated.append(fila)

    # actualización del archivo dataset_hogares con la nueva columna
    abrir_archivo_csv(DATASET_HOGARES, Write=True, data=data_updated)

    print(f"Se agregó la columna 'MATERIAL_TECHUMBRE' al archivo {DATASET_HOGARES}")    

## Sección A punto 9:
def crear_columna_densidad():
    """
    crea una nueva columna denominada 'DENSIDAD_HOGAR' de tipo numerico que indica cuantas personas 
    hay por habitacion en el hogar.
    bajo (menos de 1 persona por habitacion) = 0
    medio (entre 1 y 2 personas por habitacion) = 1
    alto (mas de 2 personas por habitacion) = 2
    """
    
    data_list = []

    reader , header = abrir_archivo_csv(DATASET_HOGARES)

    #Verifico si ya existe la columna DENSIDAD_HOGAR en el archivo:
    if "DENSIDAD_HOGAR" in header:
        return print("La columna 'DENSIDAD_HOGAR' ya existe en el archivo.")
    
    # Agrego columna DENSIDAD_HOGAR al encabezado
    header.append("DENSIDAD_HOGAR")
    data_list.append(header)
    # Me guardo el índice de la columna , recorro el archivo y proceso
    personas_index = header.index("IX_TOT") #personas en el hogar
    numero_habitaciones_index  =header.index("IV2") #numero de habitaciones
    for fila in reader:
        if fila[personas_index] != '' and fila[numero_habitaciones_index] != '':
            densidad = int(fila[personas_index]) / int(fila[numero_habitaciones_index])
            if densidad < 1:
                fila.append(0)
            elif densidad <= 2:
                fila.append(1)   
            else:
                fila.append(2)
        else:
            fila.append(2)        
        data_list.append(fila)
        
    # Actualizo el archivo dataset_hogares.csv con la nueva columna
    abrir_archivo_csv(DATASET_HOGARES, Write=True, data=data_list)
    
    print(f"Se agregó la columna 'DENSIDAD_HOGAR' al archivo {DATASET_HOGARES}")

## Sección A punto 10:
def condicion_habitabilidad():
    """
    Crea una nueva columna llamada 'CONDICION_DE_HABITABILIDAD' que clasifica
    la vivienda como: insuficiente, regular, saludable y buena, evaluando 5 condiciones.
    """
    data_list = []

    reader , header = abrir_archivo_csv(DATASET_HOGARES)
    #Verifico si ya existe la columna CONDICION_DE_HABITABILIDAD en el archivo:
    if "CONDICION_DE_HABITABILIDAD" in header:
        return print("La columna 'CONDICION_DE_HABITABILIDAD' ya existe en el archivo.")

    # Agrego la nueva columna al encabezado
    header.append("CONDICION_DE_HABITABILIDAD")
    data_list.append(header)

    # Índices requeridos
    idx_agua = header.index("IV6")
    idx_origen_agua = header.index("IV7")
    idx_banio = header.index("IV8")
    idx_material = header.index("MATERIAL_TECHUMBRE")
    idx_piso = header.index("IV3")

    for fila in reader:
        puntaje = 0
        if fila[idx_agua] == "1":
            puntaje += 1
        elif fila[idx_agua] == "3":
            puntaje -= 1

        if fila[idx_origen_agua] == "1":
            puntaje += 1
        elif fila[idx_origen_agua] == "3":
            puntaje -= 1

        if fila[idx_banio] == "1":
            puntaje += 1
        else:
            puntaje -= 1

        if fila[idx_material].strip().lower() == "material durable":
            puntaje += 1
        elif fila[idx_material].strip().lower() == "material precario":
            puntaje -= 1

        if fila[idx_piso].strip().lower() == "1":
            puntaje += 1
        elif fila[idx_piso] == "3":
            puntaje -= 1

        # Clasificación final
        if puntaje == 5:
            fila.append("buena")
        elif puntaje == 4:
            fila.append("saludable")
        elif puntaje > 2:
            fila.append("regular")
        else:
            fila.append("insuficiente")

        data_list.append(fila)

    abrir_archivo_csv(DATASET_HOGARES, Write=True, data=data_list)

    print(f"Se agregó la columna 'CONDICION_DE_HABITABILIDAD' al archivo {DATASET_HOGARES}")


# SECCION B:
## Sección B punto 4:
def ranking_aglomerados_universitarios():
    """
    Devuelte los 5 aglomerados con mayor porcentaje de hogares con 
    dos o mas individuos con estudios universitarios o superiores finalizados.
    """


    # estructura de datos para guardar el total de hogares por aglomerado
    total_hogares = {}

    # estructura de datos para guardar el total de hogares por aglomerado con dos o mas universitarios
    total_hogares_con_universitarios={}

    # estructura de datos para guardar el porcentaje de hogares con dos o mas universitarios por aglomerado
    hogares_porcentajes={}
    # calculo el total de hogares por aglomerado a partir del archivo de hogares

    csv_hogares , header = abrir_archivo_csv(DATASET_HOGARES)
    
    aglomerado_index = header.index("AGLOMERADO")
    pondera_index = header.index("PONDERA")

    for row in csv_hogares:
        aglomerado = row[aglomerado_index]
        pondera = int(row[pondera_index])
        
        # si el aglomerado no esta en total_hogares lo agrego
        if aglomerado not in total_hogares:
            total_hogares[aglomerado] = 0
                    
        # sumarizo la cantidad de hogares por aglomerados
        total_hogares[aglomerado] += pondera
    
 
    # recorro  el dataset de individuos
    csv_reader = abrir_archivo_csv(DATASET_INDIVIDUALES, DictReader=True)

    # filtro las personas con estudios universitarios o superiores finalizados
    individuos_universitarios = filter(lambda x: ( int(x["CH12"]) in (7,8) and int(x["CH13"])==1) , csv_reader)

    # contabilizo la cantidad de individuos universitarios por hogar
    hogares_con_univer =  Counter(map(lambda x: (x['CODUSU'], x['NRO_HOGAR'], x['AGLOMERADO'],x['PONDERA']), individuos_universitarios)).most_common()


    # filtro la cantidad de hogares con 2 o mas universitarios
    #hogares_con_univer 0:(CODUSU,NRO_HOGAR,AGLOMERADO), 1:CANTIDADUNIVERSITARIOS

    hogares_mas_2_universitarios =  filter(lambda x: ( int(x[1]) >=2) , hogares_con_univer)

    for hogar in hogares_mas_2_universitarios:
        aglomerado = hogar[0][2]
        pondera = int(hogar[0][3])
        if aglomerado not in total_hogares_con_universitarios:
            total_hogares_con_universitarios[aglomerado]=0
            
        total_hogares_con_universitarios[aglomerado]+=pondera

    
    # tomando los datos recabados calculo el porcentaje por aglomerado
    
    for elem in total_hogares_con_universitarios:
        aglomerado = elem
    
        if aglomerado not in hogares_porcentajes:
            hogares_porcentajes[aglomerado] = 0.0

        # calculo el porcentaje para el aglomerado actual
        hogares_porcentajes[aglomerado] = total_hogares_con_universitarios[aglomerado]/total_hogares[aglomerado]*100

 
    lista_hogares = list(hogares_porcentajes.items())

    # Ordenar la lista por el valor de las tuplas en orden descendente
    lista_hogares_sorted = sorted(lista_hogares, key=lambda item: item[1], reverse=True)

    for elem in lista_hogares_sorted[:5]:
        print(f"""Aglomerado:{elem[0]} - Porcentaje de hogares con dos o mas universitarios:{elem[1]:.2f}%""")

## Sección B punto 5:
def porcentaje_viviendas_ocupadas_por_propietario():
    """
    Informa el porcentaje de viviendas ocupadas por sus propietarios en cada aglomerado
    """

    # estructura de datos para guardar el total de hogares por aglomerado
    total_hogares = {}

    # estructura de datos para guardar el total de hogares por aglomerado ocupados por sus propietarios
    total_hogares_propietarios={}

    # estructura de datos para guardar el porcentaje de hogares ocupados por sus propietarios por aglomerado
    hogares_porcentajes={}
    # calculo el total de hogares por aglomerado a partir del archivo de hogares

    csv_hogares , header = abrir_archivo_csv(DATASET_HOGARES)
            
    aglomerado_index = header.index("AGLOMERADO")
    pondera_index = header.index("PONDERA")

    propietario_index = header.index("II7") # 1,2 valores posibles para propietario

    for row in csv_hogares:
        aglomerado = int(row[aglomerado_index])
        pondera = int(row[pondera_index])
        propietario = row[propietario_index]
        
        
        # si el aglomerado no esta en total_hogares lo agrego
        if aglomerado not in total_hogares:
            total_hogares[aglomerado] = 0
                    
        # sumarizo la cantidad de hogares por aglomerados
        total_hogares[aglomerado] += pondera

        if propietario in ('1','2'):
            #l o tomo solo si es propietario
            if aglomerado not in total_hogares_propietarios:
                total_hogares_propietarios[aglomerado]=0
            total_hogares_propietarios[aglomerado]+= pondera

    for elem in total_hogares_propietarios:
            aglomerado = elem
        
            if aglomerado not in hogares_porcentajes and total_hogares[aglomerado]!= 0:
                hogares_porcentajes[aglomerado] = total_hogares_propietarios[aglomerado]/total_hogares[aglomerado] *100
            else:
                hogares_porcentajes[aglomerado] = 0.0

    lista_hogares = list(hogares_porcentajes.items())

    # Ordenar la lista por el numero de aglomerado
    lista_hogares_sorted = sorted(lista_hogares, key=lambda item: item[0])

        
    for elem in lista_hogares_sorted:
            print(f"""Aglomerado:{elem[0]} - Porcentaje de hogares habitados por sus propietarios:{elem[1]:.2f}%""")


## Sección B punto 6:
def aglomerado_mas_cantidad_hogares_2habitantes_sinbanio():
    """
    Informar el aglomerado con mayor cantidad de viviendas con más de dos ocupantes y sin baño.
    Informar también la cantidad de ellas.
    """


    # estructura de datos para guardar el total de hogares por aglomerado con mas de dos habitantes y sin baño
    total_hogares_con_2habitantes_sinbanio={}

    csv_hogares , header = abrir_archivo_csv(DATASET_HOGARES)
        
    aglomerado_index = header.index("AGLOMERADO")
    pondera_index = header.index("PONDERA")
    tienebanio_index = header.index("IV8")  # 1: SI/ 2: NO
    ocupantes_index = header.index("IX_TOT") # cantidad de miembros del hogar

    for row in csv_hogares:
        aglomerado = row[aglomerado_index]
        pondera = int(row[pondera_index])
        ocupantes = int(row[ocupantes_index])
        tienebanio =row[tienebanio_index]
        if ocupantes >2 and tienebanio =='2':
            # si el aglomerado no esta en total_hogares_con_2habitantes_sinbanio 
            # y cumple las condiciones lo agrego
            if aglomerado not in total_hogares_con_2habitantes_sinbanio:
                total_hogares_con_2habitantes_sinbanio[aglomerado] = 0
            # sumarizo la cantidad de hogares por aglomerados
            total_hogares_con_2habitantes_sinbanio[aglomerado] += pondera


    lista_hogares = list(total_hogares_con_2habitantes_sinbanio.items())

    # Ordenar la lista por el valor de las tuplas en orden descendente
    lista_hogares_sorted = sorted(lista_hogares, key=lambda item: item[1], reverse=True)

    for elem in lista_hogares_sorted[:1]:
        print(f"""El aglomerado con mas hogares que tienen mas de dos ocupantes y sin baño es el {elem[0]} con {elem[1]} hogares""")


## Sección B punto 8:
def regiones_inquilinos():
    """
    Ordena las regiones de forma descendente según el porcentaje de inquilinos
    de cada una.
    """
    
    # Inicializo un diccionario para almacenar los resultados por región
    resultados = {}
    total_hogares = 0
    
    reader, header = abrir_archivo_csv(DATASET_HOGARES)
    
    # Me guardo el índice de la columna REGION y TENENCIA
    region_index = header.index("REGION")
    tenencia_index = header.index("II7")
    ponderacion_index = header.index("PONDERA")
    
    for fila in reader:
        region = fila[region_index]
        tenencia = fila[tenencia_index]
        ponderacion = fila[ponderacion_index]
        # Verifico si la región ya está en el diccionario
        if region not in resultados:
            resultados[region] = 0
        # Verifico si el hogar es inquilino
        if tenencia == "3":
            resultados[region] += int(ponderacion)
        total_hogares += int(ponderacion)

    # Calculo y el porcentaje por región y sobreescribo el diccionario
    for region, dato in resultados.items(): 
        region_porcenteje = dato / total_hogares * 100
        resultados[region] = region_porcenteje
    # ordeno el diccionario por porcentaje de inquilinos de forma descendente
        resultados = dict(sorted(resultados.items(), key=lambda item: item[1], reverse=True))
        
    for region, region_porcenteje in resultados.items():
        print(f"""Región: {region} - Porcentaje de hogares con inquilinos: {region_porcenteje:.2f}%""")

## Sección B punto 11:
def porcentaje_viviendas_precarias_por_aglomerado():
    """
    Esta función calcula el porcentaje de viviendas precarias por aglomerado
    según año ingresado por usuario.
    """
    # Leer el archivo CSV y calcular el total de viviendas y las precarias por aglomerado
    tot_por_aglomerado ={}
    year_selected = input(f"Ingrese año que desea saber los porcentajes de viviendas precarias:")

    reader = abrir_archivo_csv(DATASET_HOGARES, DictReader=True)

    last_trimestre = 0

    for row in reader:
        year=row['ANO4']
        trimestre=int(row['TRIMESTRE'])
        aglomerado=row['AGLOMERADO']
        material=row['MATERIAL_TECHUMBRE']
        ponderacion=int(row['PONDERA'])

        if year == year_selected:
            last_trimestre = max(last_trimestre, trimestre)
            if trimestre == last_trimestre:
                if aglomerado not in tot_por_aglomerado:
                    tot_por_aglomerado[aglomerado] = {"Total": 0, "Precario": 0}
                tot_por_aglomerado[aglomerado]["Total"] += ponderacion
                if material == "Material precario":
                    tot_por_aglomerado[aglomerado]["Precario"] += ponderacion

    if not tot_por_aglomerado:
        print(f"No se encontraron datos para el año {year_selected}.")
        return #para evitar el error de division por cero
    
    # Calcular el porcentaje de viviendas precarias por aglomerado:
    porcentajes= {}
    for aglomerado, data in tot_por_aglomerado.items():
        total = data["Total"]
        precario = data["Precario"]
        if total > 0:
            porcentajes[aglomerado] = (precario / total) * 100
        else:
            porcentajes[aglomerado] = 0

    # Diferenciar entre mayor y menor:
    max_porcentaje = max(porcentajes, key=porcentajes.get)
    min_porcentaje = min(porcentajes, key=porcentajes.get)

    print(f"En el año {year_selected} (último trimestre guardado T{last_trimestre}):")

    print(f"El aglomerado {max_porcentaje} fue el de mayor porcentaje de viviendas de material precario, con un porcentaje de: {porcentajes[max_porcentaje]:.2f}%")
    print(f"mientras que el aglomerado {min_porcentaje} fue el de menor porcentaje de viviendas de material precario, con un porcentaje de: {porcentajes[min_porcentaje]:.2f}%")

## Sección B punto 12:
def hogar_jub_insuficiente():
    """
    Esta función calcula el porcentaje de jubilados en viviendas con habitabilidad insuficiente
    por aglomerado en el último trimestre disponible.
    """ 

    tot_por_aglomerado = {}

    max_anio = 0
    max_trimestre = 0

    reader = abrir_archivo_csv(DATASET_HOGARES, DictReader=True)

    for row in reader:
        anio = int(row['ANO4'])
        trimestre = int(row['TRIMESTRE'])
        if anio > max_anio or (anio == max_anio and trimestre > max_trimestre):
            max_anio = anio
            max_trimestre = trimestre

    reader = abrir_archivo_csv(DATASET_HOGARES, DictReader=True)

    for row in reader:
        aglomerado = int(row['AGLOMERADO'])
        hogar = row['CONDICION_DE_HABITABILIDAD']

        if int(row['ANO4']) == max_anio and int(row['TRIMESTRE']) == max_trimestre:
            if row['V2'] == '1':
                if aglomerado not in tot_por_aglomerado:
                    tot_por_aglomerado[aglomerado] = {'total': 0, 'insuficiente': 0}
                tot_por_aglomerado[aglomerado]['total'] += 1
                if hogar == 'insuficiente':
                    tot_por_aglomerado[aglomerado]['insuficiente'] += 1

    if not tot_por_aglomerado:
        print("No se encontraron datos de jubilados en el último trimestre.")
        return

    print(f"Porcentajes de jubilados en viviendas con habitabilidad insuficiente (último trimestre {max_anio} - T{max_trimestre}):")
    for aglomerado, datos in tot_por_aglomerado.items():
        total = datos["total"]
        insuf = datos["insuficiente"]
        porcentaje = (insuf / total) * 100 if total > 0 else 0
        print(f"Aglomerado {aglomerado}: {porcentaje:.2f}%")