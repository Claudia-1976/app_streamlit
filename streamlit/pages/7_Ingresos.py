import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

from src.utils.constantes import NOMBRE_APP
from src.utils.funciones_streamlit import cargar_selector_trimestre
from src.utils.funciones_streamlit import cargar_selector_anios
from src.utils.funciones_streamlit import tabla_con_estilo
from src.utils.funciones_streamlit import cargar_coordenadas
from src.utils.funciones_archivos import hogares_segun_ingresos
from src.utils.funciones_archivos import hogares_segun_ingresos_por_aglomerado
from src.utils.funciones_archivos import promedios_canasta_basica_por_trimestre

st.header("Ingresos",divider="orange")

container = st.container(border=True)
container.text('En esta sección se presenta información sobre el nivel de ingreso de los hogares y su relacion con los indices de pobreza e indigencia.', help=None)

st.subheader("Clasificación de hogares segun su nivel de ingresos")
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
            sel_anios = cargar_selector_anios()
    with col2:
            sel_trimestre = cargar_selector_trimestre()



attr = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
)


tiles = 'https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png'



# Muestra la opción seleccionada
if sel_anios is not None and sel_trimestre is not None:

    lineapobreza=0
    lineaindigencia=0
    promedios_canasta= promedios_canasta_basica_por_trimestre(sel_anios,sel_trimestre)
    lineapobreza =promedios_canasta['linea_pobreza']
    lineaindigencia=promedios_canasta['linea_indigencia']
    a, b = st.columns(2)
    with a:
        st.metric(label="Línea Pobreza", value='{:.2f}'.format(lineapobreza),  border=True)
    with b:
        st.metric(label="Línea Indigencia", value='{:.2f}'.format(lineaindigencia),  border=True)


    # parametrizo la cantidad de integrantes por hogar a considerar
    integrantes = st.slider("Seleccione la cantidad de integrantes por hogar", 1, 10, 4,1)

    hogares = hogares_segun_ingresos(sel_anios,sel_trimestre,lineapobreza, lineaindigencia,integrantes=integrantes)

    if not hogares.empty:   
              # muestra la tabla con estilos predefinidos
              st.table(tabla_con_estilo(hogares))
              
              fig, ax = plt.subplots(figsize=(12, 8))
              ax.bar(hogares['categorias'],hogares['cantidad'],0.80,color=["skyblue", "limegreen", "red"])
              ax.bar_label(ax.containers[0], fmt=lambda x: f"{x:.0f}", label_type='edge')
              ax.set_title(f"Cantidad de hogares segun ingresos - Año {str(sel_anios)} Trimestre {str(sel_trimestre)}", fontsize=18)
              ax.set_xlabel("Categorias", fontsize=12)
              ax.set_ylabel("Cantidad de hogares", fontsize=16)
              
              plt.xticks(rotation=0) # Asegura que las etiquetas del eje x estén horizontales para mejor legibilidad
              plt.xticks(fontsize=10)
              plt.yticks(rotation=25)
              st.pyplot(fig)
              
              #leo el archivo de coordenadas para dibujar en el mapa
              coordenadas = cargar_coordenadas()
              
              df_mapa= hogares_segun_ingresos_por_aglomerado(sel_anios,sel_trimestre,lineapobreza, lineaindigencia,integrantes=integrantes)

              df_mapa['coordenadas']=df_mapa['AGLOMERADO'].map(lambda x: coordenadas[f"{x:02}"]['coordenadas'])
              df_mapa['nombre']=df_mapa['AGLOMERADO'].map(lambda x: coordenadas[f"{x:02}"]['nombre'])
              mapa = folium.Map(
                   location=(-34.9206, -57.9547)
                   ,control_scale=True
                   ,zoom_start=6
                   ,tiles=tiles
                   ,name='es'
                  ,attr=attr
               )
              # agrego un punto por aglomerado
              for m in df_mapa.itertuples():
                texto= "<h4> <b>" + m.nombre +"</h4></b>"+ "<br><b>Hogares Indigentes: &nbsp: </b>"+str(m.PONDERA_x)+ "<br><b>Hogares pobres : </b>"+ str(m.PONDERA_y)
                popup = folium.Popup(texto, max_width=2650)
                folium.Marker(
                     m.coordenadas,
                     popup=popup, 
                     icon=folium.Icon(color='blue', icon='info-sign') # Icono 
                ).add_to(mapa)
              st_folium(mapa,width=2250)

    else:
        st.error ("No se encontraron datos para el trimestre " + str(sel_trimestre) + " del año " + str(sel_anios),icon="🚨")        

        
else:
    st.warning ("Por favor seleccione un año y un trimestre.", icon="⚠️")        