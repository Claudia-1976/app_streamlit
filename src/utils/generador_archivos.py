import csv
from src.utils.constantes import PATH_FOLDER, DATASET_INDIVIDUALES, DATASET_HOGARES
from src.responses.hogares import (
    agregar_tipo_hogar,
    agregar_material_techumbre,
    crear_columna_densidad,
    condicion_habitabilidad
)
from src.responses.individuales import (
    traducir_genero,
    traducir_nivel_ed,
    crear_columna_condicion_laboral,
    crear_columna_universitario
)

def generate_data_out(palabra_clave):
    """
    Genera un archivo CSV ordenado con los datos de los archivos que contienen la palabra clave en su nombre.
    Los archivos procesados se encuentran en la carpeta especificada por PATH_FOLDER."""

    datos = []
    for archivo in PATH_FOLDER.iterdir():
        if archivo.is_file() and palabra_clave in archivo.name.lower():
            with archivo.open("r", newline='', encoding="utf-8") as f:
                lector = csv.DictReader(f, delimiter=';')
                header = lector.fieldnames  # Guardar encabezado solo una vez
                for fila in lector:
                    datos.append(fila)

    if not datos:
        print(f"No se encontraron archivos con la palabra clave '{palabra_clave}'.")
        return
    
    # Definir el path de salida según la palabra clave
    if palabra_clave == "individual":
        salida = DATASET_INDIVIDUALES
    elif palabra_clave == "hogar":
        salida = DATASET_HOGARES

    # Ordenar los datos por año y trimestre
    datos_ordenados = sorted(datos,key=lambda fila: (int(fila["ANO4"]), int(fila["TRIMESTRE"])))

    with salida.open("w", newline='', encoding="utf-8") as aux:
        escritor = csv.DictWriter(aux, fieldnames=header)
        escritor.writeheader()
        escritor.writerows(datos_ordenados)

    print(f"{salida.name} generado en {salida.parent}")

def creacion_de_columnas():
    """
    Crea las columnas necesarias en los datasets de individuos y hogares.
    """
    try:
        # Generar columnas en el dataset de hogares
        agregar_tipo_hogar()
        agregar_material_techumbre()
        agregar_material_techumbre()
        crear_columna_densidad()
        condicion_habitabilidad()
        # Generar columnas en el dataset de individuos:
        traducir_genero()
        traducir_nivel_ed()
        crear_columna_condicion_laboral()
        crear_columna_universitario()
    except Exception as e:
        print(f"Error al crear columnas: {e}")