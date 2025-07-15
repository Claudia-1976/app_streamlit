import streamlit as st
import pandas as pd
import sys
sys.path.append('..')

from src.utils.funciones_archivos import (
    cantidad_viviendas_por_año,
    cantidad_viviendas_por_tipo,
    material_pisos_interiores_aglomerados,
    viviendas_con_banio_aglomerados,
    regimen_tenencia_viviendas_aglomerados,
    viviendas_en_villa_emergencia,
    porcentaje_condicion_habitabilidad
)
from src.utils.constantes import (
    DATASET_HOGARES,
    NOMBRE_APP
)
from src.utils.funciones_streamlit import (
    mensaje_error_columnas,
    cargar_selector_anios,
    grafico_tortas_viviendas,
    cargar_selector_aglomerados,
    cargar_selector_regimen,
    graficar_evolucion_regimen_tenencia,
    boton_exportar_csv,
    grafico_barras_banio,
    grafico_porcentaje_viviendas_villa
)

st.set_page_config(page_title=NOMBRE_APP+' '+'Características de la vivienda',page_icon="🚪")

# Cargar dataset
hogares = pd.read_csv(DATASET_HOGARES, encoding='utf-8', low_memory=False)  

st.header('Características de la vivienda', anchor='False', divider='blue')
container = st.container(border=True)
container.write("""
        En esta sección se visualizará información relacionada a las características 
         de las viviendas de la población argentina según la EPH.
        """)
st.divider()
st.subheader("Seleccione el año de análisis")
st.markdown(
    """
    Seleccione un año para explorar las características habitacionales relevadas en ese período.
    El análisis se realiza sobre los trimestres disponibles del año seleccionado.  
    Si elige la opción **"Todos los años"**, se incluirán **todos los registros disponibles** con sus respectivos trimestres.
    
    ❗ Esta selección afectará todos los indicadores y visualizaciones que se muestran en esta sección.
    """
)

# Cargar selector de años:
col1,col2 = st.columns(2)
sel_anios = cargar_selector_anios(
    "Seleccione un año",
    True,
    st=col1
)

# 1.4.1:
## Cantidad total de viviendas
cantidad = cantidad_viviendas_por_año(hogares, sel_anios)
if cantidad == "error":
    mensaje_error_columnas()
else:
    st.subheader(f"La cantidad total de viviendas en el año {sel_anios} es {cantidad}." if sel_anios !="Todos" 
        else f"La cantidad total de viviendas en todos los años es {cantidad}.")
st.divider()

# 1.4.2:
## Pie chart de tipos de viviendas
st.subheader(f"Distribución por tipo de vivienda en el año {sel_anios}" if sel_anios !="Todos"
    else "Distribución por tipo de vivienda en todos los años")
distribucion = cantidad_viviendas_por_tipo(hogares, sel_anios)
if distribucion is None:
    mensaje_error_columnas()
else:
    grafico_tortas_viviendas(distribucion)
    tabla = distribucion.reset_index()
    tabla.columns = ["Tipo", "Cantidad de viviendas"]
    fuentes = st.toggle("Mostrar datos", key="datos_tipos_viviendas")
    if fuentes:
        st.write('Distribución por tipo de vivienda:')
        st.dataframe(tabla, use_container_width=False, hide_index=True)
st.divider()

# 1.4.3:
## material predominante en los pisos interiores de las viviendas:
st.subheader("Material de pisos predominante por aglomerado")
st.markdown(
    """
    A continuación se presenta el **material de piso predominante** en las viviendas de cada aglomerado. 
    Las categorías consideradas son:
    - **1:** mosaico, baldosa, madera, cerámica o alfombra  
    - **2:** cemento o ladrillo fijo  
    - **3:** ladrillo suelto o tierra  
    - **4:** otro material
    """
)
st.write(
    f"Material predominante según la información disponible en el año {sel_anios}:" 
    if sel_anios !="Todos" else 
    "Material predominante según la información disponible en todos los años:"
)
tabla_material = material_pisos_interiores_aglomerados(hogares, sel_anios)
if tabla_material is None:
    mensaje_error_columnas()
else:
    tabla_material.columns = ["ID","Aglomerado", "Materiales predominantes", "Viviendas"]
    st.dataframe(tabla_material[["Aglomerado", "Materiales predominantes", "Viviendas"]],hide_index=True, use_container_width=False)
st.divider()

# 1.4.4:
## Por aglomerado, la proporción de viviendas que disponen de baño dentro del hogar en el año seleccionado:
st.subheader(
    f"Análisis de acceso a baño en el hogar por aglomerado {sel_anios}" 
    if sel_anios !="Todos" else 
    "Análisis de acceso a baño en el hogar por aglomerado en todos los años"
)
st.markdown(
    """
    El gráfico muestra el **porcentaje de viviendas que cuentan con baño dentro del hogar** en cada aglomerado.  
    """
)
proporcion_banio = viviendas_con_banio_aglomerados(hogares, sel_anios)
if proporcion_banio is None:
    mensaje_error_columnas()
else:
    grafico_barras_banio(proporcion_banio)
    proporcion_banio.columns = ["ID","Aglomerado", "Porcentaje"]
    fuentes = st.toggle("Mostrar datos", key="datos_banio")
    if fuentes:
        st.write('Proporción de viviendas con baño por aglomerado:')
        st.dataframe(proporcion_banio[["Aglomerado", "Porcentaje"]],
                    use_container_width=False,
                    hide_index=True
        )   
st.divider()

#1.4.5:
st.subheader("Evolución de la tenencia de la vivienda")
st.markdown(
    """
    Se visualiza a continuación la **evolución de los regímenes de tenencia de las viviendas a lo largo del tiempo**, 
    según el **aglomerado** y los **tipos de tenencia** seleccionados.
    El gráfico se ajusta de acuerdo al **año previamente elegido**:  
    - Si se seleccionó un año específico, se mostrará la evolución durante los **trimestres disponibles** de ese año.  
    - Si se eligió la opción "Todos los años", se mostrará la evolución conjunta considerando todos los trimestres disponibles de todos los años presentes en el dataset.
    """
)
# Cargar selector de aglomerados:
col3,col4 = st.columns(2)
sel_aglo = cargar_selector_aglomerados(st=col3)
# Cargar selector de regimenes de tenencia:
regimenes_seleccionados = cargar_selector_regimen()
if sel_aglo != None:
    # Filtrar los hogares según el régimen de tenencia y aglomerado seleccionado
    
    df_reg_ten = regimen_tenencia_viviendas_aglomerados(hogares, sel_anios, int(sel_aglo), regimenes_seleccionados)
    if df_reg_ten is None:
        mensaje_error_columnas()
    else:
        
        st.pyplot(graficar_evolucion_regimen_tenencia(df_reg_ten, sel_anios))
else:
    st.warning("Por favor, seleccione un aglomerado para visualizar la evolución de la tenencia de la vivienda.")
st.divider()

# 1.4.6:
#Informar de manera ordenada (decreciente) la cantidad de viviendas ubicadas en villa
#de emergencia por aglomerado. Además de la cantidad informar el porcentaje con respecto al total.
st.subheader("Viviendas en villa de emergencia por aglomerado")
st.markdown(
    """
    A continuación se muestra el **porcentaje de viviendas ubicadas en villas de emergencia** 
    en cada aglomerado, ordenadas de menor a mayor.
    """
)
df_emergencia = viviendas_en_villa_emergencia(hogares, sel_anios)
if df_emergencia is None:
    mensaje_error_columnas()
else:
    grafico_porcentaje_viviendas_villa(df_emergencia)
    df_emergencia.columns = ["ID","Aglomerado", "Cantidad de viviendas", "Porcentaje"]
    fuentes = st.toggle("Mostrar datos", key="datos_villa_emergencia")
    if fuentes:
        st.write('Cantidad y porcentaje de viviendas en villa de emergencia por aglomerado:')
        st.dataframe(df_emergencia[["Aglomerado", "Cantidad de viviendas", "Porcentaje"]],
                    use_container_width=False,
                    hide_index=True)
st.divider()

# 1.4.7:
##  Informar para cada aglomerado el porcentaje de viviendas por CONDICION_DE_HABITABILIDAD. 
# Además de informarse debe poder exportarse a un CSV los resultados.
st.subheader("Condición de habitabilidad por aglomerado")
st.markdown(
        """
        A continuación, se visualizará la condición de habitabilidad de las viviendas por aglomerado.
        La condición de habitabilidad fue determinada por un sistema de puntuación en que se evaluaron
        las siguientes características de la vivienda:  
        **Tiene agua?** / **Origen del agua?** / **Posee baño?** / **Material del techo?** / **Material del piso?**
        """
)
df_condicion = porcentaje_condicion_habitabilidad(hogares, sel_anios)
if df_condicion is None:
    mensaje_error_columnas()
else:
    st.dataframe(df_condicion, hide_index=True, use_container_width=True)
    boton_exportar_csv(df_condicion, "condicion_vivienda.csv")
st.divider()