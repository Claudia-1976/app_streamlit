import csv
import json
import pandas as pd

from src.utils.constantes import (
    DATASET_INDIVIDUALES,
    DATASET_HOGARES,
    ID_AGLOMERADOS,
    PATH_FOLDER_MISC,
    ID_REGIMEN_TENENCIA
)
from src.utils.generador_archivos import generate_data_out, creacion_de_columnas

from src.utils.funciones_archivos import periodos_validos
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import textwrap

# Función para obtener info de año/trimestre
def obtener_rango_temporal(path_csv=False, clave=''):
    """
    Obtiene el rango de información de años y trimestres en un dataset CSV.
    """
    if path_csv is False:
        return "No se ha proporcionado un archivo CSV válido."
    try:
        with path_csv.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            INDEX_ANO4 = header.index("ANO4")
            INDEX_TRIMESTRE = header.index("TRIMESTRE")
                
            datos = []
                
            for row in reader:
                if row[INDEX_ANO4] and row[INDEX_TRIMESTRE]:
                    año = int(row[INDEX_ANO4])
                    trimestre = int(row[INDEX_TRIMESTRE])
                    datos.append((año, trimestre))
    except FileNotFoundError:
        return "El archivo CSV no se encuentra disponible."
    
    if not datos:
        return "No hay datos disponibles."

    datos_ordenados = sorted(datos)
    primero = datos_ordenados[0]
    ultimo = datos_ordenados[-1]

    return f"El dataset de {clave} contiene información desde el trimestre y año {primero[1]}/{primero[0]} hasta el {ultimo[1]}/{ultimo[0]}."

# Simulación de recarga del dataset
def recargar_dataset():
    """
    Recarga la lectura de dataset en CSV y devuelve un mensaje con el resultado.
    """
    try:
        generate_data_out("individual")
        generate_data_out("hogar")
        creacion_de_columnas()
        return "✅ Dataset actualizado correctamente."
    except Exception as e:
        return f"⚠️ Error al generar los datasets: {e}"

def actualizar_y_mostrar(info_individuales, info_hogares):
    mensaje = recargar_dataset()
    
    if "✅" in mensaje:
        info_individuales.info(obtener_rango_temporal(DATASET_INDIVIDUALES, "individuales"))
        info_hogares.info(obtener_rango_temporal(DATASET_HOGARES, "hogares"))
        st.success(mensaje)
    else:
        st.warning(mensaje)

def mensaje_error_columnas():
    """
    Muestra un mensaje de error si las columnas no están presentes en el DataFrame.
    """
    mensaje = st.warning("No se encontraron una o más columnas requeridas en el DataFrame." \
            "Puede intentar recargar el dataset desde la sección Carga de Datos.")
    return mensaje


def cargar_selector_periodos(clave=None):
    """
    Genera un selectbox con los periodos validos. Ambos archivos se encuentran disponibles.
    """
    # Define las opciones
    opciones = periodos_validos()

    # Crea el selectbox
    selecbox = st.selectbox("Seleccione un Periodo:"
                             ,opciones
                             , key=clave
                             ,index=None
                             ,format_func=lambda x: "Año 20" + str(x[0]) + " - Trimestre: " + str(x[1])
                             ,placeholder= "Seleccionar un periodo"
                             )  # Preselecciona la primera opción

    return selecbox

def cargar_selector_trimestre():
    """
    Genera un selectbox con los trimestres.
    """
    # Define las opciones
    opciones = [1,2,3,4]

    # Crea el selectbox
    selectbox = st.selectbox("Seleccione un trimestre "
                             ,opciones
                             ,index=None
                             ,format_func=lambda x: "Trimestre " + str(x)
                             ,placeholder= "Seleccionar un trimestre"
                             ) 
    return selectbox


def cargar_selector_anios(texto=None, op_sel=None, st=st):
    """
    Genera un selectbox con los años disponibles. 
    Tiene como parámetros: 
    
    texto: para personalizar el texto que figura arriba del selector. (tipo string)
    op_sel: para definir si el selectbox muestra la opción "Todos los años" o no. (tipo booleano)
    
    Sino se brinda ningún parámetro, se muestra el selectbox con los años disponibles sin ningún
    texto personalizado ni la opción "Todos los años".
    """
    # Define las opciones
    opciones = list(set(2000 + int(anio[0]) for anio in periodos_validos()))

    # Crea el selectbox
    selectbox = st.selectbox(texto if texto!=None else "Seleccione un año"
                             ,opciones if op_sel is None or not op_sel else (["Todos"] + opciones)
                             ,index=None if op_sel is None or not op_sel else 0
                             ,format_func=lambda x: "Año " + str(x) if x != "Todos" else "Todos los años"
                             ,placeholder= "Seleccionar un año"
                             ) 
    return selectbox


def grafico_tortas_viviendas(distribucion):
    """
    Muestra un gráfico de torta con la distribución de tipos de viviendas.
    """
    # Diccionario para personalizar las leyendas
    leyendas = {
        "Unipersonal": "Unipersonal (1 persona)",
        "Nuclear": "Nuclear (2 a 4 personas)",
        "Extendido": "Extendido (5 o más personas)"
    }
    etiquetas = [leyendas.get(idx, str(idx)) for idx in distribucion.index]
    fig, ax = plt.subplots()
    distribucion.plot.pie(
        autopct='%1.2f%%',
        ax=ax,
        explode=[0.05]*len(distribucion)
    )
    ax.set_ylabel("")
    ax.legend(etiquetas, title="Tipo de vivienda", loc="best", bbox_to_anchor=(1, 0.5))
    return st.pyplot(fig)

def cargar_selector_aglomerados(st=st, clave=None):
    """
    Genera un selectbox con los aglomerados disponibles.
    """
    selectbox = st.selectbox("Seleccione un aglomerado"
                            , list(ID_AGLOMERADOS.keys())
                            , index=None
                            , format_func=lambda x: f"{x} - {ID_AGLOMERADOS[x]}"
                            , placeholder= "Seleccionar un aglomerado"
                            , key=clave
                            )
    return selectbox

def cargar_selector_regimen(st=st):
    """
    Muestra un selector múltiple de regímenes de tenencia usando Streamlit.
    Devuelve una lista de las keys seleccionadas.
    """
   
    seleccion = st.multiselect(
        "Seleccione uno o más regímenes de tenencia",
        options=list(ID_REGIMEN_TENENCIA.keys()),
        format_func=lambda x: ID_REGIMEN_TENENCIA[x],
        default=list(ID_REGIMEN_TENENCIA.keys()),
        placeholder="Seleccione uno o más regímenes de tenencia"
    )
    if seleccion == list(ID_REGIMEN_TENENCIA.keys()):
        seleccion = "Todos"
    return seleccion



def graficar_evolucion_regimen_tenencia(df, anio):
    """
    Crea un gráfico de barras agrupadas mostrando las proporciones de régimen de tenencia
    por trimestre/año.
    
    Args:
        df: DataFrame con columnas ['TRIMESTRE'/'ANO4', 'NOMBRE_REGIMEN', 'PROPORCION']
        anio: String indicando si es "Todos" o un año específico
    """
    # Determinar qué columna usar para el eje x
    x_col = 'TRIMESTRE' if anio != "Todos" else 'ANO4'
    
    # Obtener valores únicos
    regimenes = df['NOMBRE_REGIMEN'].unique()
    periodos = sorted(df[x_col].unique())
    
    # Preparar datos para el gráfico
    y = np.arange(len(regimenes))*1.2
    if len(periodos) == 0:
        st.warning("No hay datos para los filtros seleccionados.")
        return plt.figure()  
    height = 0.9 / len(periodos)  # alto de las barras
    
    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(20, 15))
    
    # Dibujar barras para cada período
    for i, periodo in enumerate(periodos):
        datos = df[df[x_col] == periodo].set_index('NOMBRE_REGIMEN').reindex(regimenes)['PROPORCION']
        bars = ax.barh(y + i * height, datos, height, label=str(periodo))
        # Agregar etiquetas de porcentaje en cada barra
        ax.bar_label(bars, labels=[f"{v:.2f}%" for v in datos], padding=0.5, fontsize=20)
    
    # Personalizar el gráfico
    ax.set_xlabel('Proporción (%)', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=20)
    
    ax.set_title(
        f'Proporción de viviendas por régimen de tenencia (Año {anio})' if anio != "Todos" 
        else 'Proporción de viviendas por régimen de tenencia (Todos los años)',
        fontsize=25,
        pad=20
    )
    
    # Envolver el texto largo en múltiples líneas
    wrapped_labels = [textwrap.fill(r, width=25) for r in regimenes]
    ax.set_yticks(y + height * (len(periodos) - 1) / 2)
    ax.set_yticklabels(wrapped_labels, fontsize=20)
    ax.invert_yaxis()  # Invertir el eje y para que el primer régimen esté arriba
    
    # Ajustar los límites del eje x para dejar espacio para la leyenda
    ymax = ax.get_ylim()[1]
    ax.set_ylim(top=ymax*2)  # Aumentar el límite superior en un 20%

    # Configurar la leyenda dentro del gráfico
    ax.legend(
        title='Trimestre' if anio != "Todos" else 'Año',
        loc='upper center',  # Ubicación en la esquina superior derecha
        ncol=len(periodos),  # Una columna por periodo
        bbox_to_anchor=(0.5, 1),  # Posición ajustada
        fontsize=18,  # Tamaño del texto de la leyenda
        title_fontsize=20  # Tamaño del título de la leyenda
    )
    
    plt.tight_layout() # Ajustar el diseño para evitar superposiciones
     
    return fig

def boton_exportar_csv(df, nombre_archivo="datos.csv"):
    """
    Muestra un botón para exportar el DataFrame a CSV en Streamlit.
    """
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Exportar a CSV",
        data=csv,
        file_name=nombre_archivo,
        mime='text/csv'
    )

def cargar_coordenadas():
    path_json = PATH_FOLDER_MISC / 'aglomerados_coordenadas.json'
    with open(path_json, 'r',encoding="utf-8") as f:
        return json.load(f)    



def tabla_con_estilo(df):
    """
        Aplica a un dataframe un conjunto de estilos definidos.
    """

    table_styles = [
    {'selector': 'th', 'props': [('background-color', '#2b4958'), ('font-weight', 'bold'),('font-size', '15'),('color', 'white')]},
    {'selector': 'td', 'props': [('border', '1px solid #2b4958'),('background-color', "#8f9699")]},
    {'selector': 'tr:hover', 'props': [('background-color', '#2b4958')]}
]
    return df.style.set_table_styles(table_styles)


def grafico_barras_dobles(df_grouped,periodo):
    """
        Genera un gráfico de barras dobles para la distribución de la población por edad y sexo.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    df_grouped.plot(kind="bar", ax=ax, color=["#ff69b4", "#1f77b4"], width=0.8, edgecolor='black')
    ax.set_title(f"Distribución de la población por edad y sexo - Año {int(periodo[0])+2000} Trimestre {int(periodo[1])}", fontsize=18)
    ax.set_xlabel("Grupo de edad", fontsize=14)
    ax.set_ylabel("Población en millones", fontsize=14)
    ax.legend(title="Sexo", fontsize=12, title_fontsize=14)

    plt.xticks(rotation=0) # Asegura que las etiquetas del eje x estén horizontales para mejor legibilidad
    plt.xticks(fontsize=10)
    plt.yticks(rotation=25)

    st.pyplot(fig)

def grafico_barras_edad_promedio(df_promedios):
    """
    Genera un gráfico de barras para la edad promedio por aglomerado.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    df_promedios.set_index("Aglomerado").plot(kind="bar", ax=ax)

    plt.xticks(rotation=0)

    ax.set_title("Edad promedio por aglomerado")
    ax.set_ylabel("Edades")
    ax.set_xlabel("Aglomerado")

    st.pyplot(fig)

def grafico_tortas_etaria(cantidad, etiquetas, periodo_sel, seleccion):
    """
    Genera un gráfico de torta para la composición etaria de la población por aglomerado
    """

    fig, ax = plt.subplots(figsize=(8, 4))

    colores = ["#37d09f", "#e07348", "#6f87c0"]

    ax.pie(cantidad, autopct="%1.1f%%", startangle=30, explode=(0.06, 0, 0.06),  pctdistance=1.20, colors=colores),
    
    ax.legend(etiquetas, title="Tramos Etarios", loc="lower left", bbox_to_anchor=(1, 0))
    
    st.pyplot(fig)


def grafico_barras_banio(df):
    """
    Grafica la proporción de viviendas con baño por aglomerado usando barras horizontales.
    Requiere un DataFrame con columnas:
    - 'NOMBRE_AGLOMERADO'
    - 'PROPORCION_BANIO' (valores en porcentaje, de 0 a 100)
    """

    # Ordenar los aglomerados de mayor a menor proporción
    df_ordenado = df.sort_values("PROPORCION_BANIO", ascending=True)

    df_ordenado["color"] = df_ordenado["PROPORCION_BANIO"].apply(
    lambda x: "red" if x < 80 else "green"
)

    fig = px.bar(
        df_ordenado,
        x="PROPORCION_BANIO",
        y="NOMBRE_AGLOMERADO",
        orientation="h",
        text="PROPORCION_BANIO",
        color="color",  # Color se basa en la columna generada
        color_discrete_map={"green": "seagreen", "red": "indianred"},
        labels={"PROPORCION_BANIO": "Porcentaje de viviendas con baño (%)"},
        title="Proporción de viviendas con baño por aglomerado"
    )
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside',
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_range=[0, 100],
        yaxis=dict(tickfont=dict(size=11)),
        yaxis_title=None,
        margin=dict(l=120, r=40, t=60, b=40),
        height=50 * len(df_ordenado),  # escalar el alto según cantidad de aglomerados
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        showlegend=False
    )
    return st.plotly_chart(fig, use_container_width=True)

def grafico_porcentaje_viviendas_villa(df):
    """
    Muestra un gráfico de barras horizontales con el porcentaje 
    de viviendas en villa de emergencia por aglomerado.
    Coloreado de verde (bajo) a rojo (alto).
    """
    fig = px.bar(
        df,
        x="PORCENTAJE",
        y="NOMBRE_AGLOMERADO",
        orientation="h",
        text="PORCENTAJE",
        labels={"PORCENTAJE": "Porcentaje de viviendas en villa (%)"},
        title="Porcentaje de viviendas en villa de emergencia por aglomerado",
        color="PORCENTAJE",
        color_continuous_scale=["seagreen", "gold", "firebrick"],
        range_color=(0, 100)
    )

    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition="outside",
        cliponaxis=False
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        xaxis_range=[0,100],
        margin=dict(l=120, r=40, t=60, b=40),
        height=50 * len(df),        
        yaxis_title=None,
        showlegend=False
    )
    return st.plotly_chart(fig, use_container_width=True)

def grafico_alfabetismo(df):
    """
    Muestra un gráfico de barras dobles con el porcentaje de personas que saben
    y no saben leer y escribir, por año.
    """

    fig, ax = plt.subplots(figsize=(12, 6))

    df.plot(
        kind="bar",
        ax=ax,
        color=["#1f77b4", "#ff69b4"],  # azul = sabe, rosa = no sabe
        width=0.8,
        edgecolor='black'
    )

    ax.set_title("Porcentaje de alfabetismo por año", fontsize=18)
    ax.set_xlabel("Año", fontsize=14)
    ax.set_ylabel("Porcentaje (%)", fontsize=14)
    ax.legend(title="Condición", fontsize=12, title_fontsize=14)

    plt.xticks(rotation=0, fontsize=10)
    plt.yticks(rotation=25)

    st.pyplot(fig)

def graficar_evolucion_edad(df_resumen):
    """
    Genera un gráfico de línea mostrando la evolución de la edad media y mediana
    a lo largo del tiempo, usando datos agrupados por año y trimestre.
    """
    df_resumen = df_resumen.copy()
    df_resumen["Periodo"] = df_resumen["ANO4"].astype(str) + "T" + df_resumen["TRIMESTRE"].astype(str)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_resumen["Periodo"], df_resumen["Edad_Media"], marker="o", label="Edad Media", color="royalblue")
    ax.plot(df_resumen["Periodo"], df_resumen["Edad_Mediana"], marker="s", label="Edad Mediana", color="darkorange")

    ax.set_title("📈 Evolución de la Edad Media y Mediana", fontsize=14)
    ax.set_xlabel("Periodo", fontsize=12)
    ax.set_ylabel("Edad", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)

    st.pyplot(fig)
