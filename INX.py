import pandas as pd
import numpy as np
import streamlit as st

# Función para calcular la distancia entre dos puntos en 3D
def distancia_3d(punto1, punto2):
    return np.sqrt((punto1[0] - punto2[0])**2 + (punto1[1] - punto2[1])**2 + (punto1[2] - punto2[2])**2)

# Función para determinar si un taladro corta un cubo
def interseca_cubo(coordenadas_taladro, azimut, dip, profundidad, cubo):
    """
    coordenadas_taladro: [X, Y, Z]
    azimut: dirección del taladro en el plano horizontal
    dip: inclinación del taladro con respecto a la horizontal
    profundidad: distancia máxima del taladro
    cubo: coordenadas del cubo [X_centro, Y_centro, Z_centro]
    """
    
    # Definir el radio de influencia del cubo de 5x5x5
    radio_cubo = 2.5
    
    # Calcular el vector del taladro
    azimut_rad = np.radians(azimut)
    dip_rad = np.radians(dip)
    
    # Dirección del taladro (convertido en 3D)
    dx = np.sin(azimut_rad) * np.cos(dip_rad)
    dy = np.cos(azimut_rad) * np.cos(dip_rad)
    dz = np.sin(dip_rad)
    
    # Recorrido del taladro en función de la profundidad
    punto_final = [
        coordenadas_taladro[0] + dx * profundidad,
        coordenadas_taladro[1] + dy * profundidad,
        coordenadas_taladro[2] + dz * profundidad
    ]
    
    # Comprobar si el recorrido del taladro intersecta el cubo (se calcula con la distancia de centro a centro)
    distancia = distancia_3d(coordenadas_taladro, cubo)
    
    # Verificar si la distancia es menor o igual al radio de influencia del cubo
    if distancia <= radio_cubo:
        return True, punto_final  # El taladro corta el cubo, se devuelve el punto final del taladro
    return False, None

# Configuración de la interfaz de usuario en Streamlit
st.title("Análisis de Intersección de Taladro con Cubos 5x5x5")

# Cargar archivo de taladro DDH
uploaded_file_ddh = st.file_uploader("Sube tu archivo de taladro (DDH)", type="xlsx")
if uploaded_file_ddh is not None:
    ddh_data = pd.read_excel(uploaded_file_ddh)
    st.write("Datos de Taladro cargados:", ddh_data.head())

# Cargar archivo de cubos MB_CL_CL.xlsx
uploaded_file_cubos = st.file_uploader("Sube el archivo de cubos (MB_CL_CL)", type="xlsx")
if uploaded_file_cubos is not None:
    mb_cl_cl_data = pd.read_excel(uploaded_file_cubos)
    st.write("Datos de Cubos cargados:", mb_cl_cl_data.head())

# Analizar intersección si ambos archivos están cargados
if uploaded_file_ddh and uploaded_file_cubos:
    cubos_intersecados = []

    # Iterar por cada taladro
    for _, taladro in ddh_data.iterrows():
        coordenadas_taladro = [taladro["XCOLLAR"], taladro["YCOLLAR"], taladro["ZCOLLAR"]]
        azimut = taladro["AZIMUT"]
        dip = taladro["DIP"]
        profundidad = taladro["DEPTH"]
        
        # Verificar la intersección con los cubos
        for _, cubo in mb_cl_cl_data.iterrows():
            cubo_coord = [cubo["X"], cubo["Y"], cubo["Z"]]
            interseca, punto_final = interseca_cubo(coordenadas_taladro, azimut, dip, profundidad, cubo_coord)
            
            if interseca:
                cubo_info = cubo.to_dict()
                cubo_info["Taladro"] = taladro["BHID"]
                cubo_info["Punto_final_taladro"] = punto_final
                cubos_intersecados.append(cubo_info)

    # Crear un DataFrame con los cubos intersecados
    if cubos_intersecados:
        cubos_intersecados_df = pd.DataFrame(cubos_intersecados)
        st.write("Reporte de cubos intersectados:")
        st.dataframe(cubos_intersecados_df)
    else:
        st.write("No se encontraron intersecciones entre los cubos y los taladros.")
