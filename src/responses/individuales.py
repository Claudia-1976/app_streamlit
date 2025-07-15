import csv
from src.utils.constantes import DATASET_INDIVIDUALES,DATASET_HOGARES, ID_AGLOMERADOS
from src.utils.funciones_csv import abrir_archivo_csv

# SECCION A:
## Sección A punto 3:
def traducir_genero(): 
    """
    Agrega la columna 'CH04_str' y traduce el valor de la columna 'CH04' 
    (1 = Masculino / 2 = Femenino) en el archivo dataset_individuales.csv.
    """
    
    data_list = []
    
    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
    
    # VErifico la existencia de la columna NIVEL_ED_str en el archivo:
    if "CH04_str" in header:
        return print("La columna 'CH04_str' ya existe en el archivo.")
    # Agrego la columna CH04_str al encabezado
    header.append("CH04_str")
    data_list.append(header)
    # Me guardo el índice de la columna CH04, recorro el archivo y proceso
    ch04_index = header.index("CH04")
    for fila in reader:
        if fila[ch04_index] == "1":
            fila.append("Masculino")
        elif fila[ch04_index] == "2":
            fila.append("Femenino")
        data_list.append(fila)
            
    # Actualizo el archivo dataset_individuales.csv con la nueva columna
    
    abrir_archivo_csv(DATASET_INDIVIDUALES, Write=True, data=data_list)

    print(f"Se agregó la columna 'CH04_str' al archivo {DATASET_INDIVIDUALES}")

## Sección A punto 4:
def traducir_nivel_ed():
    
    data_list = []

    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
    
    # Verifico la existencia de la columna NIVEL_ED_str en el archivo:
    if "NIVEL_ED_str" in header:
        return print("La columna 'NIVEL_ED_str' ya existe en el archivo.")
    # Agrego la columna NIVEL_ED_str al encabezado
    header.append("NIVEL_ED_str")
    data_list.append(header)
    # Me guardo el índice de la columna NIVEL_ED, recorro el archivo y proceso
    nivel_ed_index = header.index("NIVEL_ED")
    for fila in reader:
        if str(fila[nivel_ed_index]) == "1":
            fila.append("Primario incompleto")
        elif str(fila[nivel_ed_index]) == "2":
            fila.append("Primario completo")
        elif str(fila[nivel_ed_index]) == "3":
            fila.append("Secundario incompleto")   
        elif str(fila[nivel_ed_index]) == "4":
            fila.append("Secundario completo")
        elif "5" <= str(fila[nivel_ed_index]) <= "6":
            fila.append("Superior o universitario")
        elif str(fila[nivel_ed_index]) == "7" or str(fila[nivel_ed_index]) == "9":
            fila.append("Sin información")        
        data_list.append(fila)
            
    # Actualizo el archivo dataset_individuales.csv con la nueva columna
    abrir_archivo_csv(DATASET_INDIVIDUALES, Write=True, data=data_list)

    print(f"Se agregó la columna 'NIVEL_ED_str' al archivo {DATASET_INDIVIDUALES}")
    

## Sección A punto 5:
def crear_columna_condicion_laboral():
    """
    Crea una nueva columna denominada 'CONDICION_LABORAL' de formato texto con la siguiente especificacion:
    Ocupado autónomo: ESTADO = 1 Y CAT_OCUP es 1 o 2
    Ocupado dependiente:  ESTADO = 1 Y CAT_OCUP es 3 o 4 o 9
    Desocupado : ESTADO = 2
    Inactivo: ESTADO = 3
    Fuera de categoría/sin información : ESTADO = 4
    """
    
    data_list = []

    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)

    # Verifico la existencia de la columna CONDICION_LABORAL en el archivo:
    if "CONDICION_LABORAL" in header:
        return print("La columna 'CONDICION_LABORAL' ya existe en el archivo.")
    
    # Agrego columna CONDICION_LABORAL al encabezado
    header.append("CONDICION_LABORAL")
    data_list.append(header)
    
    # Me guardo el índice de la columna CONDICION_LABORAL, recorro el archivo y proceso
    estado_index = header.index("ESTADO")
    cat_ocup_index  =header.index("CAT_OCUP")
    for fila in reader:

        if fila[estado_index] == "4":
            fila.append("Fuera de categoría/sin información")
        elif fila[estado_index] == "3":
            fila.append("Inactivo")
        elif fila[estado_index] == "1" and fila[cat_ocup_index] in("3","4","9") :
            fila.append("Ocupado dependiente")   
        elif fila[estado_index] == "1" and fila[cat_ocup_index] in("1","2") :
            fila.append("Ocupado autónomo")
        else:
            fila.append("No aplica")        
        data_list.append(fila)
            
    # Actualizo el archivo dataset_individuales.csv con la nueva columna
    abrir_archivo_csv(DATASET_INDIVIDUALES, Write=True, data=data_list)

    print(f"Se agregó la columna 'CONDICION_LABORAL' al archivo {DATASET_INDIVIDUALES}")

## Sección A punto 6:
def crear_columna_universitario():
    """
    Crea una nueva columna denominada 'UNIVERSITARIO' de tipo numerica que indica si una persona de edad
    ha completado como mínimo el nivel universitario tiene el valor
    1: Sí
    0: No
    2: no aplica
    """
    
    data_list = []

    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
        
    # Verifico la existencia de la columna UNIVERSITARIO en el archivo:
    if "UNIVERSITARIO" in header:
        return print("La columna 'UNIVERSITARIO' ya existe en el archivo.")
       
    # Agrego columna UNIVERSITARIO al encabezado
    header.append("UNIVERSITARIO")
    data_list.append(header)
        
    # Me guardo el índice de la columna CONDICION_LABORAL, recorro el archivo y proceso
    edad_index = header.index("CH06") # años cumplidos.
    nivel_educativo_index  =header.index("CH12") # nivel mas alto que cursa o curso
    finalizo_nivel_index = header.index("CH13") # finalizo el nivel mas alto que cursa o curso
    for fila in reader:

        if int(fila[edad_index]) >= 21:
            if fila[nivel_educativo_index] == 8:
                fila.append(1)
            elif fila[nivel_educativo_index] == 7 and fila[finalizo_nivel_index] == 1:
                fila.append(1)   
            else:
                fila.append(2)
        else:
            fila.append(2)        
        data_list.append(fila)
            
    # Actualizo el archivo dataset_individuales.csv con la nueva columna
    abrir_archivo_csv(DATASET_INDIVIDUALES, Write=True, data=data_list)

    print(f"Se agregó la columna 'UNIVERSITARIO' al archivo {DATASET_INDIVIDUALES}")

#SECCION B:
## Sección B punto 1:
def analfabetismo():
    """
    Informar, año tras año, el porcentaje de personas mayores a 6 años capaces e incapaces de leer y escribir.
    Importante: Esto toma en cuenta únicamente la información del último trimestre de cada año.
    """
    
    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)

    INDEX_ANO4 = header.index("ANO4")              # Año del Trimestre
    INDEX_TRIMESTRE = header.index("TRIMESTRE")    # Numero del Trimestre
    INDEX_PONDERA = header.index("PONDERA")        # Pondera de gente
    INDEX_CH6 = header.index("CH06")               # Edad de la gente
    INDEX_CH9 = header.index("CH09")               # Sabe leer y escribir; 1 = SI / 2 = NO / 3 = Menor de 2 años

    año_actual = ""
    trimestre_actual = ""

    alfabetas = 0
    analfabetas = 0
    tot_personas_de_este_año = 0    #  Porcentaje = [(Valor Final) * 100] / (Valor inicial) #

    variables_cargadas = False

    for row in reader:

        # Cargamos los datos de la primera linea del dataset
        if not variables_cargadas:
            año_actual = row[INDEX_ANO4]
            trimestre_actual = row[INDEX_TRIMESTRE]
            if int(row[INDEX_CH6]) > 6 and row[INDEX_CH9] != '3':
                tot_personas_de_este_año = tot_personas_de_este_año + int(row[INDEX_PONDERA])
                if row[INDEX_CH9] == '1':
                    alfabetas = alfabetas + int(row[INDEX_PONDERA])
                elif row[INDEX_CH9] == '2':
                    analfabetas = analfabetas + int(row[INDEX_PONDERA])
            variables_cargadas = True
    
        else:

            if año_actual == row[INDEX_ANO4]:
                if trimestre_actual == row[INDEX_TRIMESTRE]:
                    if int(row[INDEX_CH6]) > 6 and row[INDEX_CH9] != '3':
                        tot_personas_de_este_año = tot_personas_de_este_año + int(row[INDEX_PONDERA])
                        if row[INDEX_CH9] == '1':
                            alfabetas = alfabetas + int(row[INDEX_PONDERA])

                        elif row[INDEX_CH9] == '2':
                            analfabetas = analfabetas + int(row[INDEX_PONDERA])

                else:
                    # Si el año es el mismo pero el trimestre cambia, reseteamos los valores
                    trimestre_actual = row[INDEX_TRIMESTRE]
                    tot_personas_de_este_año = 0
                    alfabetas = 0
                    analfabetas = 0
            else:
                print(f"Año {año_actual} (Trimestre {trimestre_actual}):")
                print(f"  Porcentaje de alfabetas: {(alfabetas*100/tot_personas_de_este_año):.3f}%")
                print(f"  Porcentaje de analfabetas: {(analfabetas*100/tot_personas_de_este_año):.3f}%")
                tot_personas_de_este_año = 0
                alfabetas = 0
                analfabetas = 0
                año_actual = row[INDEX_ANO4]
                trimestre_actual = row[INDEX_TRIMESTRE]
                if int(row[INDEX_CH6]) > 6 and row[INDEX_CH9] != '3':
                    tot_personas_de_este_año = tot_personas_de_este_año + int(row[INDEX_PONDERA])
                    if row[INDEX_CH9] == '1':
                        alfabetas = alfabetas + int(row[INDEX_PONDERA])
                    elif row[INDEX_CH9] == '2':
                        analfabetas = analfabetas + int(row[INDEX_PONDERA])
        
    print(f"Año {año_actual} (Trimestre {trimestre_actual}):")
    print(f"  Porcentaje de alfabetas: {float(alfabetas*100/tot_personas_de_este_año):.3f}%")
    print(f"  Porcentaje de analfabetas: {float(analfabetas*100/tot_personas_de_este_año):.3f}%")

## Sección B punto 2:
def estudios_de_extranjeros_str():
    """
    informar el porcentaje de personas no nacidas en Argentina que hayan cursado un nivel universitario o superior.
    Segun el trimestre y año ingresado por el usuario
    """

    años = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
    trimestres = ['1','2','3','4']
    boolean_de_control = True
    boolean_de_control2 = True

    print("Favor de introducir los siguientes datos de busqueda:")

    while boolean_de_control != False:
        año_input = input("Ingresar año de busqueda (2016-2024). Presionar 0 para salir:")
        if año_input == '0':
            print("Saliendo del programa...")
            return
        if año_input in años:
            boolean_de_control = False
        else:
            print("Año ingresado no valido. Intente de vuelta")
    
    while boolean_de_control2 != False:
        trimes_input = input("Ingresar trimestre de busqueda (1/2/3/4). Presionar 0 para salir:")
        if trimes_input == '0':
            print("Saliendo del programa...")
            return
        if trimes_input in trimestres:
            boolean_de_control2 = False
        else:
            print("Año ingresado no valido. Intente de vuelta")


    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)


    INDEX_ANO4 = header.index("ANO4")               # Año del Trimestre
    INDEX_TRIMESTRE = header.index("TRIMESTRE")     # Numero del Trimestre
    INDEX_PONDERA = header.index("PONDERA")         # Pondera de gente

    #INDEX_NIVEL_ED = header.index("NIVEL_ED")           # Estudios: 5 = Superior universitario incompleto // 6 = Superior universitario completo
    INDEX_NIVEL_ED_STR = header.index("NIVEL_ED_str")    # Estudios: 5 a 6: "Superior o universitario"

    INDEX_CH15 = header.index("CH15")                    # Lugar de Nacimiento  4- En un país limítrofe // 5. En otro país (especificar)

    tot_extranjeros = 0
    tot_extranjeros_con_estudio = 0

    for row in reader:
        if (row[INDEX_ANO4] == año_input) and (row[INDEX_TRIMESTRE] == trimes_input):
            if (row[INDEX_CH15] == '4') or (row[INDEX_CH15] == '5'):
                tot_extranjeros = tot_extranjeros + int(row[INDEX_PONDERA])
                if row[INDEX_NIVEL_ED_STR] == "Superior o universitario":
                    tot_extranjeros_con_estudio = tot_extranjeros_con_estudio + int(row[INDEX_PONDERA])

    if tot_extranjeros > 0:
        print(f"Busqueda en el año {año_input} y trimestre {trimes_input}:")
        print(f"De {tot_extranjeros} personas no nacidas en Argentina, {tot_extranjeros_con_estudio} tienen estudios superiores, por lo que el {float(tot_extranjeros_con_estudio*100/tot_extranjeros):.2f}% de ellas cursaron un nivel universitario o superior")
    else:
        print("No hay datos registrados para ese trimestre ó año")

## Sección B punto 3:
def menor_desocupacion():

    desocupacion_por_trimestre = {}

    lector = abrir_archivo_csv(DATASET_INDIVIDUALES, DictReader=True)

    for row in lector:
        # Salteo las filas donde ESTADO != 2 (desocupado)
        if row["ESTADO"] != "2":
            continue

        clave = (row["ANO4"], row["TRIMESTRE"])
        pondera = int(row["PONDERA"])

        # Sumar la ponderada al diccionario con los datos de desocupados
        if clave not in desocupacion_por_trimestre:
            desocupacion_por_trimestre[clave] = 0
        desocupacion_por_trimestre[clave] += pondera

    menor_clave = None
    menor_valor = float('inf')  # Inicializamos con un valor casi infinito positivo

    for clave, valor in desocupacion_por_trimestre.items():
        if valor < menor_valor:
            menor_valor = valor
            menor_clave = clave
    
    if menor_clave is None:
        print("No se encontraron datos de desocupación.")
    else:
        print(f"El año {menor_clave[0]} y trimestre {menor_clave[1]} tuvieron la menor desocupación de: {menor_valor} personas")

## Sección B punto 7:
def porcentaje_educacion_superior():
    """
    Calcula el porcentaje de personas que han cursado al menos el nivel
    universitario o superior en cada aglomerado.
    """
    
    # Inicializo un diccionario para almacenar los resultados por aglomerado
    resultados = {}
    total_individuos = 0
    
    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
        
    # Me guardo el índice de la columna AGLOMERADO, NIVEL_ED_str y PONDERA
    aglomerado_index = header.index("AGLOMERADO")
    nivel_ed_str_index = header.index("NIVEL_ED_str")
    ponderacion_index = header.index("PONDERA")
    
    for fila in reader:
        aglomerado = fila[aglomerado_index]
        nivel_ed_str = fila[nivel_ed_str_index]
        ponderacion = fila[ponderacion_index]
        # Verifico si el aglomerado ya está en el diccionario
        if aglomerado not in resultados:
            resultados[aglomerado] = 0
        # Verifico si la persona ha cursado al menos nivel universitario o superior
        if nivel_ed_str == "Superior o universitario":
            resultados[aglomerado] += int(ponderacion)
        total_individuos += int(ponderacion)

    # Calculo y muestro el porcentaje por aglomerado
    for aglomerado, dato in resultados.items(): 
        aglomerado_porcenteje = dato / total_individuos * 100
        
        print(f"""Aglomerado: {aglomerado} - Porcentaje de personas con educación superior: {aglomerado_porcenteje:.2f}%""")


## Sección B punto 9:
def aglomerado_nivel_estudios():
    """
    Muestra la cantidad de personas mayores de edad según su nivel de estudios alcanzados,
    ordenado por año y trimestre.
    """
    
    # Selecciono el aglomerado
    print("Aglomerados disponibles:")
    for key, value in ID_AGLOMERADOS.items():
        print(f"{key}: {value}")
    aglomerado = input("Ingrese el código del aglomerado (2 dígitos): ")
    if aglomerado not in ID_AGLOMERADOS.keys():
        print("El aglomerado ingresado no es válido.")
        return
    
    # Inicializo un diccionario para almacenar los resultados por año y trimestre
    resultados = {}
    tabla = {}
    
    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
        
    # Me guardo los indices de las columnas que necesito
    aglomerado_index = header.index("AGLOMERADO")
    edad_index = header.index("CH06")
    nivel_estudios_index = header.index("NIVEL_ED_str")
    ponderacion_index = header.index("PONDERA")
    anio_index = header.index("ANO4")
    trimestre_index = header.index("TRIMESTRE")

    # Recorro el archivo y voy guardando los resultados en el diccionario
    for fila in reader:
        aglomerado_actual = fila[aglomerado_index]
        edad = int(fila[edad_index])
        nivel_estudios = fila[nivel_estudios_index]
        ponderacion = int(fila[ponderacion_index])
        anio = fila[anio_index]
        trimestre = fila[trimestre_index]
        tabla_index = str(anio + '_' + trimestre)
        
        # Verifico el aglomerado y si la persona es mayor de edad
        if int(aglomerado_actual) == int(aglomerado) and edad >= 18:
            # Verifico si nivel de estudios esta entre los resultados
            if nivel_estudios not in resultados:
                resultados[nivel_estudios] = 0
            resultados[nivel_estudios] += ponderacion
            tabla[tabla_index] = resultados[nivel_estudios]
    # Ordeno el diccionario de niveles de estudios por cantidad de personas
    resultados = dict(sorted(resultados.items(), key=lambda item: item[1], reverse=True))

    # Ordeno el la tabla general por año y trimestre
    tabla = dict(sorted(tabla.items(), key=lambda item: (item[0].split('_')[0], item[0].split('_')[1])))
    
    # Muestro los resultados
    print(f"Resultados para el aglomerado {aglomerado}: {ID_AGLOMERADOS[aglomerado]}")
    print("Cantidad de personas mayores de edad según su nivel de estudios alcanzados:")
    for periodo in tabla.items():
        anio_titulo = periodo[0].split('_')[0]
        trimestre_titulo = periodo[0].split('_')[1]
        print()
        print(f"Año: {anio_titulo} - Trimestre: {trimestre_titulo}")
        for nivel_estudios, cantidad in resultados.items():
            if nivel_estudios != "Sin información":
                print(f"{nivel_estudios.ljust(30)}: {cantidad}")

## Sección B punto 10:
def porcentajes_secundario_incompleto():
    """
    Compara el porcentaje de personas con secundario incompleto entre dos aglomerados
    ingresados por teclado.
    """

    #Selecciono el aglomerado
    print("Aglomerados disponibles:")
    for key, value in ID_AGLOMERADOS.items():
        print(f"{key}: {value}")
    print()    
    aglomerado_a_input = input("Ingrese el ID del primer aglomerado (2 dígitos): ")
    aglomerado_b_input = input("Ingrese el ID del segundo aglomerado (2 dígitos): ")
    # Verifico que los aglomerados ingresados sean válidos
    if aglomerado_a_input not in ID_AGLOMERADOS or aglomerado_b_input not in ID_AGLOMERADOS:
        print("Uno o más aglomerados ingresados no son válidos.")
        return

    aglomerado_a = int(aglomerado_a_input)
    aglomerado_b = int(aglomerado_b_input)

    results = {aglomerado_a: {}, aglomerado_b: {}}

    reader = abrir_archivo_csv(DATASET_INDIVIDUALES, DictReader=True)
        
    for row in reader:
        aglomerado = int(row["AGLOMERADO"])
        year = row["ANO4"]
        trimestre = row["TRIMESTRE"]
        age = int(row["CH06"])
        nivel_estudios = row["NIVEL_ED_str"]
        ponderacion = int(row["PONDERA"])
        
        if aglomerado in results and age >= 18:
            if year not in results[aglomerado]:
                results[aglomerado][year] = {}

            if trimestre not in results[aglomerado][year]:
                results[aglomerado][year][trimestre] = {"Total": 0, "Incompleto":0}
            
            results[aglomerado][year][trimestre]["Total"] += ponderacion

            if nivel_estudios == "Secundario incompleto":
                results[aglomerado][year][trimestre]["Incompleto"] += ponderacion

    # Calcular porcentajes
    porcentajes= {}
    for aglomerado, data in results.items():
        for year, trimestres in data.items():
            for trimestre, values in trimestres.items():
                if (year, trimestre) not in porcentajes:
                    porcentajes[(year, trimestre)] = {aglomerado_a: 0, aglomerado_b: 0}
                total = values["Total"]
                incompleto = values["Incompleto"]
                if total > 0:
                    porcentaje = (incompleto / total) * 100
                    porcentajes[(year,trimestre)][aglomerado] = porcentaje

    # Imprimir resultados en formato tabla
    print(f"{'Año':<5} | {'Trimestre':<10} | {'Aglomerado '}{aglomerado_a_input:<2} | {'Aglomerado '}{aglomerado_b_input:<2}")
    print("-" * 60)
    for (year, trimestre), values in porcentajes.items():
        porcentaje_a =values.get(aglomerado_a,0)
        porcentaje_b = values.get(aglomerado_b,0)
        print(f"{year:<5} | {trimestre:<10} | {porcentaje_a:<3.2f} %{' '*6} | {porcentaje_b:<3.2f} %{' '*6}")

## Sección B punto 13:
def universitario_hogar_insu():
    """
    Esta función calcula la cantidad de personas con educación universitaria en viviendas con
    habitabilidad insuficiente en un año solicitado por el usuario.
    """ 
    
    total = 0
    cod_hogar = []
    input_anio = input("Ingrese el año que desea consultar: ")
    if not input_anio.isdigit():
        print(f"El año ingresado deber ser un número.")
        return
    anio = int(input_anio)

    max_trimestre = 0
    anio_encontrado = False

    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES)
    anio_index = header.index("ANO4")
    tri_index = header.index("TRIMESTRE")

    for row in reader:
        if int(row[anio_index]) == anio: 
            anio_encontrado = True
            if int(row[tri_index]) > max_trimestre:
                max_trimestre = int(row[tri_index])

    if not anio_encontrado:
        print(f"No se encontraron datos para el año {anio}.")
        return

    reader , header = abrir_archivo_csv(DATASET_INDIVIDUALES) 
    hogar_index = header.index("CODUSU")
    nivel_estudios_index = header.index("CH12")
    anio_index = header.index("ANO4")
    tri_index = header.index("TRIMESTRE")
    
    for row in reader:
        if int(row[anio_index]) == anio and int(row[tri_index]) == max_trimestre:
            try:
                if int(row[nivel_estudios_index]) >= 7 and int(row[nivel_estudios_index]) < 9:
                    cod_hogar.append(row[hogar_index])
            except ValueError:
                continue

    reader , header = abrir_archivo_csv(DATASET_HOGARES)
    hogar_index = header.index("CODUSU")
    condicion_index = header.index("CONDICION_DE_HABITABILIDAD")

    for row in reader:
        if row[hogar_index] in cod_hogar and row[condicion_index] == 'insuficiente':
            total += 1
    
    print(f"Total de personas con educación universitaria en viviendas con habitabilidad insuficiente en {anio} trimestre {max_trimestre}: {total}")