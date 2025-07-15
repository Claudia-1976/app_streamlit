import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.constantes import DATASET_INDIVIDUALES, DATASET_HOGARES, NOMBRE_APP


st.set_page_config(page_title=NOMBRE_APP+' '+'Inicio',page_icon="🏠")
st.title(NOMBRE_APP)
st.header('Descripcion', divider="orange")
st.write("""
    Esta aplicación permite visualizar y analizar los datos de la Encuesta Permanente de Hogares (EPH).
    La EPH es un relevamiento continuo realizado por el INDEC para obtener información sobre las condiciones demográficas, sociales y económicas de la población.
    """)
st.divider()
