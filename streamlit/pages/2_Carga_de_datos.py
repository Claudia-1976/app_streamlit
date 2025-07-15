
import streamlit as st
from st_flexible_callout_elements import flexible_warning,flexible_success
import sys

sys.path.append('..')

from src.utils.funciones_streamlit import obtener_rango_temporal, actualizar_y_mostrar
from src.utils.funciones_archivos import archivos_faltantes
from src.utils.constantes import DATASET_INDIVIDUALES, DATASET_HOGARES, NOMBRE_APP


st.set_page_config(page_title=NOMBRE_APP+' '+'Carga de datos',page_icon="📊")

st.header('Carga de datos')
st.subheader("Información actual del sistema:",divider="orange")


# Crear contenedores dinámicos para la información
info_individuales = st.empty()
info_hogares = st.empty()
# Mostrar el rango de información de los datasets
info_individuales.info(obtener_rango_temporal(DATASET_INDIVIDUALES, "individuales"))
info_hogares.info(obtener_rango_temporal(DATASET_HOGARES, "hogares"))

st.divider()
#Verificar si todos los periodos son válidos
periodos_novalidos  = archivos_faltantes()

periodos_novalidos = sorted(periodos_novalidos, key=lambda item: int(item[0]), reverse=False)

if  len(periodos_novalidos)==0:
    flexible_success("<strong>Chequeo exitoso</strong>. <br>Para todos los periodos existen los archivos de <strong>hogares</strong> e <strong>individuos</strong> correspondientes.",line_height=1.5, border_radius=12, padding=25)
else:
    str_periodos=""
    for p in periodos_novalidos:
        str_periodos =str_periodos+ " - <strong>Año 20"+p[0] + " -  Trimestre " + p[1] + "</strong> - " + p[2] +"<br>"
        
    flexible_warning("Se encontraron inconsistencias en los siguientes periodos:<br>" + str_periodos,line_height=1.5, border_radius=12, padding=25)


st.divider()
st.write("Si los dataset no fueron creados o si cargó nuevos archivos puede actualizar el dataset haciendo click en el botón de abajo:")

# Botón para actualizar el dataset
st.button("🔁 Actualizar dataset", on_click=lambda: actualizar_y_mostrar(info_individuales, info_hogares))