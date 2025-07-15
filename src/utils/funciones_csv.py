import csv
from pathlib import Path


def abrir_archivo_csv(path, DictReader=False, Write=False, data=None):
    """
    Abrir un archivo CSV y devolver su contenido como una lista de diccionarios o una lista de listas.

    Parámetros:
    - path: ruta del archivo
    - DictReader: si es True, usa DictReader para devolver una lista de diccionarios;
    - Write: si es True, escribe los datos en el archivo CSV.
    - data: datos a escribir en el archivo CSV (opcional, solo si Write es True).
    
    Retorna:
    - Una lista de diccionarios si DictReader es True, o una lista de listas y el encabezado si es False.
    - Si Write es True, escribe los datos en el archivo CSV.
    """

    if Write & (data != None):
        with path.open("w", newline='', encoding="utf-8") as f:
           writer = csv.writer(f)
           writer.writerows(data)

    if DictReader:
        with open(path, mode="r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f, delimiter=",")
            return list(reader)
    else:
        with open(path, mode="r", encoding="utf-8", newline='') as f:
            reader = csv.reader(f, delimiter=",")
            header = next(reader)
            return list(reader), header