import streamlit as st
import sys
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

sys.path.append('..')

from src.utils.constantes import NOMBRE_APP, ID_AGLOMERADOS, PATH_FOLDER_MISC
from src.utils.funciones_streamlit import cargar_coordenadas, cargar_selector_anios, cargar_selector_trimestre, cargar_selector_aglomerados
from src.utils.funciones_archivos import cantidad_desocupados_estudios, evolucion_laboral, ocupacion_por_aglomerado, variacion_laboral

# Encabezado General
st.set_page_config(page_title=NOMBRE_APP+' '+'Actividad y Empleo',page_icon='🏠')
st.header('Actividad y empleo', anchor=False, divider='orange')
container = st.container(border=True)
container.text('En esta sección se presenta información sobre actividad y empleo basada en los datos de la EPH.', help=None)


# Punto 1.5.1
st.subheader('Cantidad de personas desocupadas según sus estudios alcanzados.', anchor=False, divider=None)
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
            sel_anios = cargar_selector_anios()
    with col2:
            sel_trimestre = cargar_selector_trimestre()
if sel_anios is not None and sel_trimestre is not None:
    data_desocupados = cantidad_desocupados_estudios(sel_anios, sel_trimestre)
    if not data_desocupados.empty:
        data_desocupados.rename(columns={'NIVEL_ED_str': 'Nivel educativo', 'ESTADO': 'Cantidad desocupados'}, inplace=True)
        # Mostrar la inforacion
        st.write(data_desocupados)
    else:
        st.error ("No se encontraron datos para el año/trimestre seleccionado.")
else:
    st.warning('Por favor, selecciona un año y trimestre.')

# Punto 1.5.2
st.subheader('Evolución de la tasa de desempleo a lo largo del tiempo, ' \
    'para todo el país y por aglomerado.', anchor=False, divider=None)
with st.container(border=True):
    aglomerado_desempleo = cargar_selector_aglomerados(clave='Desempleo')
    evolucion_des = evolucion_laboral('Desempleo', aglomerado_desempleo)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(evolucion_des['Periodo'], evolucion_des['Tasa'], marker='o', color='skyblue', linewidth=2)
    ax.set_title(f'Evolución de la Tasa de Desempleo para {ID_AGLOMERADOS[aglomerado_desempleo] if aglomerado_desempleo else 'Argentina (todo el país)'}')
    ax.set_xlabel('Periodo')
    ax.set_ylabel('Tasa de Desempleo (%)')
    ax.grid(axis='y')
    fig.subplots_adjust(left=0.20, right=1.0, top=0.9, bottom=0.3)
    st.pyplot(fig, clear_figure=True)

# Punto 1.5.3
st.subheader('Evolución de la tasa de empleo a lo largo del tiempo, ' \
    'para todo el país y por aglomerado.', anchor=False, divider=None)
with st.container(border=True):
    aglomerado_empleo = cargar_selector_aglomerados(clave='Empleo')
    evolucion_emp = evolucion_laboral('Empleo', aglomerado_empleo)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(evolucion_emp['Periodo'], evolucion_emp['Tasa'], marker='o', color='skyblue', linewidth=2)
    ax.set_title(f'Evolución de la Tasa de Empleo para {ID_AGLOMERADOS[aglomerado_empleo] if aglomerado_empleo else 'Argentina (todo el país)'}')
    ax.set_xlabel('Periodo')
    ax.set_ylabel('Tasa de Empleo (%)')
    ax.grid(axis='y')
    fig.subplots_adjust(left=0.20, right=1.0, top=0.9, bottom=0.3)
    st.pyplot(fig, clear_figure=True)

# Punto 1.5.4
st.subheader('Total de personas ocupadas por aglomerado y porcentaje según ' \
    'sector laboral.', anchor=False, divider=None)
with st.container(border=True):
    if 'ocupacion_data' not in st.session_state:
        df = ocupacion_por_aglomerado()
        df['AGLOMERADO'] = df['AGLOMERADO'].astype(str).str.zfill(2)
        df['NOMBRE_AGLOMERADO'] = df['AGLOMERADO'].map(ID_AGLOMERADOS)
        st.session_state['ocupacion_data'] = df

    ocupacion_data = st.session_state['ocupacion_data']
    # Convertir el campo 'AGLOMERADO' a string y rellenar con ceros a la izquierda
    ocupacion_data['AGLOMERADO'] = ocupacion_data['AGLOMERADO'].astype(str).str.zfill(2)
    # Recupero el nombre del aglomerado usando el diccionario ID_AGLOMERADOS
    ocupacion_data['NOMBRE_AGLOMERADO'] = ocupacion_data['AGLOMERADO'].map(ID_AGLOMERADOS)
    fig, ax = plt.subplots(figsize=(10, 16))

    plt.barh(ocupacion_data['NOMBRE_AGLOMERADO'], ocupacion_data['Empleo Estatal'], 
             label='Estatal')
    plt.barh(ocupacion_data['NOMBRE_AGLOMERADO'], ocupacion_data['Empleo Privado'], 
             left=ocupacion_data['Empleo Estatal'], label='Privado')
    plt.barh(ocupacion_data['NOMBRE_AGLOMERADO'], ocupacion_data['Otro Tipo'],
             left=ocupacion_data['Empleo Estatal'] + ocupacion_data['Empleo Privado'], 
             label='Otro')
    
    for i, (estatales, privados, otros, total) in enumerate(zip(
            ocupacion_data['Empleo Estatal'],
            ocupacion_data['Empleo Privado'],
            ocupacion_data['Otro Tipo'],
            ocupacion_data['Total Ocupados'])):
            total_barra = estatales + privados + otros
            texto = f'Total: {total:,}'.replace(',', '.')
            ax.text(total_barra / 2, i, texto, ha='center', va='center', 
                               fontsize=9, color='black', weight='bold')
            
    plt.xlabel('Porcentaje (%)')
    plt.ylabel('Aglomerado')
    plt.title('Distribución del tipo de empleo por aglomerado')
    plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    plt.subplots_adjust(left=0.3, right=0.95, top=0.99, bottom=0.05)
    plt.tick_params(axis='y', labelsize=10)
    plt.gca().set_yticklabels(ocupacion_data['NOMBRE_AGLOMERADO'], ha='right')
    st.pyplot(plt)

# Punto 1.5.5
st.subheader('Variación porcentual de la tasa de empleo o desempleo por aglomerado.'
             , anchor=False, divider=None)
st.text('Esta información muestra la variación entre el año y trimestre más ' \
                'antiguo y más actual.', help=None)
with st.container(border=True):
    categoria = st.selectbox('Elegí la tasa a comparar', ['Empleo', 'Desempleo'])
    # Cargar la variación de la tasa laboral según la categoría seleccionada
    df_variacion = variacion_laboral(categoria)
    # CArgo las coordenadas de los aglomerados desde el archivo JSON
    if 'coordenadas' not in st.session_state:
        coordenadas = cargar_coordenadas()
        st.session_state['coordenadas'] = coordenadas
    coordenadas = st.session_state['coordenadas']

    # Asigno las coordenadas y colo segun variacion para el uso del mapa
    df_variacion['lat'] = df_variacion['AGLOMERADO'].map(lambda x: coordenadas[str(x)]['coordenadas'][0])
    df_variacion['lon'] = df_variacion['AGLOMERADO'].map(lambda x: coordenadas[str(x)]['coordenadas'][1])
    
    # Asigno el color segun variacion para el uso del mapa
    if categoria == 'Empleo':
        df_variacion['color'] = df_variacion['Variación'].apply(lambda x: 'Aumento' if x > 0 else 'Disminución')
        color_mapa = {'Aumento': 'green', 'Disminución': 'red'}   
    else:  # desempleo
        df_variacion['color'] = df_variacion['Variación'].apply(lambda x: 'Aumento' if x > 0 else 'Disminución')
        color_mapa = {'Aumento': 'red', 'Disminución': 'green'}
    # Crear mapa con colores según variación
    fig = px.scatter_mapbox(
        df_variacion,
        lat='lat',
        lon='lon',
        color= 'color',
        hover_name = 'Nombre',
        hover_data={'Tasa Inicio': True, 'Tasa Fin': True, 
                    'Variación': True, 'color': False, 'lat': False, 
                    'lon': False},
        size_max=35,
        color_discrete_map= color_mapa,
        zoom=4,
        height=600
    )

    # Configurar layout y mostrar
    fig.update_layout(
        mapbox_style='open-street-map',
        margin={'r':0,'t':0,'l':0,'b':0}
    )

    st.plotly_chart(fig, use_container_width=True)