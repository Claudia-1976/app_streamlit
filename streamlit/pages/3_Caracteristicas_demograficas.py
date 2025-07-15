import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.utils.constantes import (
    DATASET_INDIVIDUALES,
    NOMBRE_APP
)
from src.utils.funciones_streamlit import (
    cargar_selector_periodos,
    grafico_barras_dobles,
    grafico_barras_edad_promedio,
    grafico_tortas_etaria,
    cargar_selector_aglomerados,
    graficar_evolucion_edad
)

from src.utils.funciones_archivos import (
    asignar_grupos_edad,
    clasificar_tramo
)

st.set_page_config(page_title=NOMBRE_APP+' '+'Características demográficas',page_icon="👪")

st.header('Características Demográficas', anchor='False', divider='red')
container = st.container(border=True)
container.text("En esta sección se visualizará la información demográfica contenida en la población según la EPH", help=None)
st.divider()

@st.cache_data
def cargando_dataset():                                     
    return pd.read_csv(DATASET_INDIVIDUALES, encoding='utf-8', low_memory=False)

df_indiv = cargando_dataset()   # Por optimización, se carga el dataset una sola vez

## 1.3.1:
#----------------------------------------------------------------------------------------------------------------
st.subheader("Distribución de población por edad y sexo")
st.write ("Seleccione un año y trimestre para mostrar distribución de la población en ese período:")
sel_periodo = cargar_selector_periodos()  # Carga el selector de períodos

# Filtrar los datos por año y trimestre
if not sel_periodo:
    st.warning("⚠️ Por favor, seleccione un año y trimestre específicos para visualizar la distribución de la población.")
else:
    edad_minima = st.slider("Filtrar por edad mínima", min_value=0, max_value=120, value=0) # Pequeño gimmick para filtrar por edad mínima

    df_filtrado = asignar_grupos_edad(df_indiv, sel_periodo, "CH06")
    df_filtrado = df_filtrado[df_filtrado["CH06"] >= edad_minima]

    df_grouped = df_filtrado.groupby(["grupos_de_edades", "CH04_str"])["PONDERA"].sum().unstack()
    df_grouped = df_grouped.sort_index() 

    grafico_barras_dobles(df_grouped, sel_periodo)

    with st.expander("ℹ️ ¿Qué muestra este gráfico?"):
        st.markdown("""
        Este gráfico de barras dobles muestra cómo se distribuye la población por grupos de edad y sexo.
        Sirve para observar diferencias demográficas como, por ejemplo, si hay más mujeres que varones en ciertos tramos etarios.
        """)

    Fuentes = st.toggle("Mostrar Fuentes", key="fuentes_distribucion_poblacion")
    if Fuentes:
        st.write('Distribución de los datos usados de la población por edad y sexo:')
        st.dataframe(df_grouped)

#----------------------------------------------------------------------------------------------------------------

## 1.3.2:

st.divider()

ultimo_ano = df_indiv["ANO4"].max()
ultimo_trim = df_indiv[df_indiv["ANO4"] == ultimo_ano]["TRIMESTRE"].max()

df_ultimo = df_indiv[(df_indiv["ANO4"] == ultimo_ano) & (df_indiv["TRIMESTRE"] == ultimo_trim)]

df_promedios = df_ultimo.groupby("AGLOMERADO")["CH06"].mean().reset_index()
df_promedios.columns = ["Aglomerado", "Edad Promedio"]

st.header("Edad promedio por aglomerado")
st.markdown(f"📅 Último período disponible: Año {ultimo_ano}, Trimestre {ultimo_trim}")

# Inicializador del botón que activa el gráfico para que se quede luego del mostrar fuentes
if "ver_grafico_promedio" not in st.session_state:
    st.session_state.ver_grafico_promedio = False

if st.button("Ver gráfico de edad promedio"):
    st.session_state.ver_grafico_promedio = True

if st.session_state.ver_grafico_promedio:
    grafico_barras_edad_promedio(df_promedios)
    st.caption("Este gráfico muestra el promedio de edad por aglomerado urbano para el período más reciente.")
    prom_nacional = df_ultimo["CH06"].mean().round(1)
    st.markdown(f"📌 **Promedio nacional de edad:** {prom_nacional} años")

if st.toggle("Mostrar Fuentes", key="fuentes_edad_promedio"):
    st.write('Datos de edad promedio por aglomerado:')
    st.dataframe(df_promedios, hide_index=True)

#----------------------------------------------------------------------------------------------------------------

## 1.3.3:

st.divider()
st.header("👥​ Composición etaria de la población por aglomerado y período")

seleccion = cargar_selector_aglomerados(clave='key')

if seleccion is None:
    st.warning("⚠️ Por favor, selecciona un aglomerado para visualizar la composición etaria.")
else:
    df_agrupado = df_indiv[df_indiv["AGLOMERADO"] == int(seleccion)].copy()

    df_agrupado["Tramo_Etario"] = df_agrupado["CH06"].apply(clasificar_tramo)
    df_agrupado["Periodo"] = df_agrupado["ANO4"].astype(str) + " T" + df_agrupado["TRIMESTRE"].astype(str)

    df_tramos = df_agrupado.groupby(["Periodo", "Tramo_Etario"])["PONDERA"].sum().unstack(fill_value=0).reset_index()

    periodos = sorted(df_tramos["Periodo"].unique())

    periodo_sel = st.radio("🗓️ Selecciona un periodo:", df_tramos["Periodo"].unique(), index=None, horizontal=True, key=f"radio_{seleccion}")

    if periodo_sel is None:
        st.warning("⚠️ Por favor, selecciona un período para visualizar la composición etaria.")
    else:
        st.subheader(f"Aglomerado {seleccion} en el período {periodo_sel}")

        datos_periodo = df_tramos[df_tramos["Periodo"] == periodo_sel]

        valores = datos_periodo[["Niños (0-14)", "Activos (15-64)", "Jubilados (65+)"]].iloc[0]
        etiquetas = valores.index
        cantidad = valores.values

        grafico_tortas_etaria(cantidad, etiquetas, periodo_sel, seleccion)

#----------------------------------------------------------------------------------------------------------------

## 1.3.4:

st.divider()
st.header("Edad Media y Mediana de la población")

df_resumen = df_indiv.groupby(["ANO4", "TRIMESTRE"])["CH06"].agg(
    Edad_Media="mean",
    Edad_Mediana="median"
).reset_index()

st.markdown("Resumen de los datos cargados de la población por año y trimestre:")

df_resumen["Edad_Media"] = df_resumen["Edad_Media"].round(1)
df_resumen["Edad_Mediana"] = df_resumen["Edad_Mediana"].round(1)

st.dataframe(df_resumen, hide_index=True)

st.subheader("📉 Evolución temporal de la Edad Media y Mediana")

graficar_evolucion_edad(df_resumen)

st.caption("Este gráfico muestra la evolución de la edad media y mediana de la población a lo largo del tiempo, permitiendo observar tendencias demográficas.")
