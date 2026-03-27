import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px

df = pd.read_csv('Datos/Seguros.csv')

# Obtener las metricas generales----------

# Costo medio de la poliza
si_fumador = df[df['fumador'] == 'Si']
si_fumadores_media = si_fumador['costo'].mean()

no_fumador = df[df['fumador'] == 'No']
no_fumadores_media = no_fumador['costo'].mean()

# Cantidad de fumadores
fumadores = df['fumador'].value_counts()
no_fuma = fumadores[0]
si_fuma = fumadores[1]


def intervalos(var):
    import math

    n = len(var)
    x_max = var.max()
    x_min = var.min()
    recorrido = x_max - x_min
    intervalos = round(1 + (3.3 * (math.log10(n))))
    amplitud = (recorrido / intervalos)

    return x_min, x_max, amplitud

def tablaFrecuencia(tabla, col, nomCol):
    tabla1 = pd.DataFrame(tabla)
    lista = []

    for reg in tabla:
        cont = 0
        for i in col:
            if reg == i:
                cont = cont + 1
        lista.append(cont)
    
    tabla2 = pd.DataFrame(lista)
    total = tabla2.sum()
    tabla3 = pd.concat([tabla1, tabla2], axis = 1)
    tabla3.columns = [nomCol, 'frecAbs']

    def calcula(freecAbs):
        fRel = freecAbs / total
        return fRel
    
    tabla3['frecRel'] = tabla3['frecAbs'].apply(calcula)
    tabla3['frecAcum'] = tabla3['frecRel'].cumsum()

    return tabla3

# Función para tabla de frecuencias agrupados

#global invertidos
def tabla_Hist(varCol, nomCol):
    global intervalos
    # Paso1: Determinar el tamaño de la muestra
    print('Variable: ' + nomCol, '\n')
    n = len(varCol)
    print('Paso1: Tamaño de la muestra: ', n, '\n')

    # Paso2: Determinar el maximo y el minimo
    x_max = varCol.max()
    x_min = varCol.min()
    print('Paso2: Maximo y minimo: ')
    print('Maximo: ', x_max)
    print('Minimo: ', x_min, '\n')

    # Paso3: Calcular el recorrido
    recorrido = x_max - x_min
    print('Paso3: Recorrido: ', recorrido, '\n')

    # Paso4: Calcular intervalos (clases)
    # Formula de Sturges (1 + 3.3 log n)
    intervalos = round(1 + (3.3 * (math.log10(n))))
    print('Paso4: Intervalos: ', intervalos, '\n')

    # Paso5: Calcular la amplitud de cada intervalo
    amplitud = recorrido / intervalos
    print('Paso5: Amplitud: ', '%0.2f' %amplitud, '\n')

    # Paso6: Construir la tabla de frecuencias
    df_tf = pd.DataFrame()
    df_tf['Clase'] = list(range(1, intervalos + 1))
    df_tf['limInf'] = np.full(shape = intervalos, fill_value = np.nan)

    for i in range(intervalos):
        df_tf.loc[i, 'limInf'] = round(x_min + (i * amplitud), 3)

    df_tf['limSup'] = round(df_tf['limInf'] + amplitud, 3)
    df_tf['x'] = (df_tf['limSup'] + df_tf['limInf']) / 2
    df_tf['f'] = np.full(shape = intervalos, fill_value = np.nan)

    for i in range (intervalos):
        k = 0
        if i == 0:
            for j in range(n):
                if varCol[j] <= df_tf['limSup'][i]:
                    k = k + 1
                df_tf.loc[i, 'f'] = k
            else:
                for j in range(n):
                    if(varCol[j] > df_tf['limInf'][i]) and (varCol[j] <= df_tf['limSup'][i]):
                        k = k + 1
                    df_tf.loc[i, 'f'] = k
    
    df_tf['Fa'] = df_tf['f'].cumsum()
    df_tf['fr'] = round(df_tf['f'] / n, 4)
    df_tf['Fra'] = df_tf['fr'].cumsum()

    return df_tf

# Funcion para actualizar el layout de las graficas
def actualiza_layout(grafica, x_title, y_title):

    grafica.update_layout(
        xaxis_title = x_title,
        yaxis_title = y_title,
        paper_bgcolor = 'white',
        plot_bgcolor = 'white',
        title_pad_1 = 20,
        title_font_family = 'verdana',
        title_font_color = 'black',
        title_font_size = 16,
        font_size = 15,
        height = 400
    )


# Grafica de Scatter

def sct(varX, varY, co, cocs, x_title, y_title, tam, titulo, marg_x = None, marg_y = None, faceCol = None):
    grafica_sc = px.scatter(df, x = varX, y = varY, 
                            color = co, 
                            color_continuous_scale = cocs, 
                            size = tam, 
                            marginal_x = marg_x, 
                            marginal_y = marg_y, 
                            facet_col = faceCol)

    actualiza_layout(grafica_sc, x_title, y_title)

    grafica_sc.show()