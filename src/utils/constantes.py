from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent.parent # Path al directorio raiz del proyecto

PATH_FOLDER = ROOT_FOLDER / 'files' / 'data_in' # Path a la carpeta de trimestres

DATASET_INDIVIDUALES = ROOT_FOLDER / 'files' / 'data_out' / 'dataset_individuales.csv' # Carpeta donde se va a guardar el dataset de individuos

DATASET_HOGARES = ROOT_FOLDER / 'files' / 'data_out' / 'dataset_hogares.csv' # Carpeta donde se va a guardar el dataset de hogares

PATH_FOLDER_MISC = ROOT_FOLDER / 'files' / 'misc' # Carpeta donde se guardan archivos misceláneos

ID_AGLOMERADOS = {
    "02" : "Gran La Plata","03" : "Bahía Blanca-Cerri","04" : "Gran Rosario",
    "05" : "Gran Santa Fe","06" : "Gran Paraná","07" : "Posadas","08" : "Gran Resistencia", "09" : "Comodoro Rivadavia-Rada Tilly",
    "10" : "Gran Mendoza", "12" : "Corrientes","13" : "Gran Córdoba",
    "14" : "Concordia","15" : "Formosa","17" : "Neuquén-Plottier",
    "18" : "Santiago del Estero-La Banda","19" : "Jujuy-Palpalá","20" : "Río Gallegos",
    "22" : "Gran Catamarca","23" : "Gran Salta","25" : "La Rioja","26" : "Gran San Luis",
    "27" : "Gran San Juan","29" : "Gran Tucumán-Tafí Viejo","30" : "Santa Rosa-Toay",
    "31" : "Ushuaia-Río Grande","32" : "Ciudad Autónoma de Buenos Aires","33" : "Partidos del Gran Buenos Aires",
    "34" : "Mar del Plata","36" : "Río Cuarto","38" : "San Nicolás-Villa Constitución",
    "91" : "Rawson-Trelew","93" : "Viedma-Carmen de Patagones",
    }

ID_REGIMEN_TENENCIA = {
    1: "Propietario de la vivienda y el terreno",
    2: "Propietario de la vivienda solamente",
    3: "Inquilino / arrendatario de la vivienda",
    4: "Ocupante por pago de impuestos / expensas",
    5: "Ocupante en relación de dependencia",
    6: "Ocupante gratuito (con permiso)",
    7: "Ocupante de hecho (sin permiso)",
    8: "Está en sucesión",
    9: "Otro"
}

NOMBRE_APP = "DATArg"
# print(f'Path al directorio raiz del proyecto: {ROOT_FOLDER}')
# print(f'Path a la carpeta de trimestres añadidos: {PATH_FOLDER}')
# print(f'Carpeta donde se va a guardar el dataset de individuos: {DATASET_INDIVIDUALES}')
# print(f'Carpeta donde se va a guardar el dataset de hogares: {DATASET_HOGARES}')