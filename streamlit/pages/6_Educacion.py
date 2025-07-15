import streamlit as st

from src.utils.funciones_streamlit import cargar_selector_anios, boton_exportar_csv, grafico_alfabetismo

from src.utils.funciones_archivos import total_personas_nivel_educativo, nivel_educativo_mas_comun_por_edad, ranking_aglomerados_universitarios, alfabetismo_formato_barras


st.set_page_config(page_title="Educación", page_icon="📚")
st.header('Educación', anchor=False, divider='blue')
container = st.container(border=True)
container.write("""
    En esta sección se visualizará información relacionada al nivel de educación alcanzado por
    la población argentina según la EPH
    """)
st.divider()

#punto 1.6.1
col1,col2 = st.columns(2)
sel_anios = cargar_selector_anios(
    "Seleccione un año",
    False,
    st=col1
)
if sel_anios is not None:
    st.subheader(f"Cantidad de personas por nivel educativo en el año {sel_anios}.")
else:
    st.subheader("Cantidad de personas por nivel educativo (año no seleccionado).")

if sel_anios is not None:
    df_educacion = total_personas_nivel_educativo(sel_anios)
    st.dataframe(df_educacion, use_container_width=True, hide_index=True)
else:
    st.error("Por favor seleccione un año.")

#punto 1.6.2

df_nivel = nivel_educativo_mas_comun_por_edad()
st.subheader("Nivel educativo más común por grupo etario")
grupos_opciones = ["20-29", "30-39", "40-49", "50-59", "60+"]
grupos_seleccionados = st.multiselect(
    "Seleccione uno o más grupos etarios:",
    options=grupos_opciones,
    default=grupos_opciones
)
df_filtrado = df_nivel[df_nivel["Rango Etario"].isin(grupos_seleccionados)]
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

#punto 1.6.3
st.subheader("Ranking 5 aglomerados con mayor porcentaje de hogares con dos o mas ocupantes con estudios universitarios o superiores finalizados")

df_ranking = ranking_aglomerados_universitarios()

if df_ranking.empty:
    st.warning("No se encontraron datos para calcular el ranking.")
else:
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    boton_exportar_csv(df_ranking, nombre_archivo="ranking_aglomerados_universitarios.csv")

# Punto 1.6.4
st.subheader("Gráfico de alfabetismo por año")
df_grafico = alfabetismo_formato_barras()

if df_grafico.empty:
    st.warning("No hay datos suficientes para graficar.")
else:
    grafico_alfabetismo(df_grafico)

    Fuentes = st.toggle("Mostrar Fuentes", key="fuentes_alfabetismo_anual")
    if Fuentes:
        st.write("Distribución de los datos usados para calcular el porcentaje de alfabetismo por año:")
        st.dataframe(df_grafico, use_container_width=True)