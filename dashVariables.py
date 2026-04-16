import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import plotly.express as px

df = pd.read_excel('Datos/plantacion_datiles_v5.xlsx')
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype(str)

# Obtener las datos generales ----------

temp_media = df['Temperatura (°C)'].mean()
wm_comercial_media = df['Watermark Comercial'].mean()
wm_uni_media = df['Watermark Uni'].mean()
total_riegos = df['Riego'].sum()


def intervalos(var):
    n = len(var)
    x_max = var.max()
    x_min = var.min()
    recorrido = x_max - x_min
    num_intervalos = round(1 + (3.3 * (math.log10(n))))
    amplitud = (recorrido / num_intervalos)
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
    tabla3 = pd.concat([tabla1, tabla2], axis=1)
    tabla3.columns = [nomCol, 'frecAbs']

    def calcula(freecAbs):
        fRel = freecAbs / total
        return fRel

    tabla3['frecRel'] = tabla3['frecAbs'].apply(calcula)
    tabla3['frecAcum'] = tabla3['frecRel'].cumsum()

    return tabla3


def tabla_Hist(varCol):
    n = len(varCol)

    x_max = varCol.max()
    x_min = varCol.min()

    recorrido = x_max - x_min

    num_intervalos = round(1 + (3.3 * (math.log10(n))))

    amplitud = recorrido / num_intervalos

    df_tf = pd.DataFrame()
    df_tf['Clase'] = list(range(1, num_intervalos + 1))
    df_tf['limInf'] = np.full(shape=num_intervalos, fill_value=np.nan)

    for i in range(num_intervalos):
        df_tf.loc[i, 'limInf'] = round(x_min + (i * amplitud), 3)

    df_tf['limSup'] = round(df_tf['limInf'] + amplitud, 3)
    df_tf['x'] = (df_tf['limSup'] + df_tf['limInf']) / 2
    df_tf['f'] = np.full(shape=num_intervalos, fill_value=np.nan)

    varCol = varCol.reset_index(drop=True)
    for i in range(num_intervalos):
        k = 0
        if i == 0:
            for j in range(n):
                if varCol[j] <= df_tf['limSup'][i]:
                    k = k + 1
            df_tf.loc[i, 'f'] = k
        else:
            for j in range(n):
                if (varCol[j] > df_tf['limInf'][i]) and (varCol[j] <= df_tf['limSup'][i]):
                    k = k + 1
            df_tf.loc[i, 'f'] = k

    df_tf['Fa'] = df_tf['f'].cumsum()
    df_tf['fr'] = round(df_tf['f'] / n, 4)
    df_tf['Fra'] = df_tf['fr'].cumsum()

    return df_tf


def actualiza_layout(grafica, x_title, y_title):
    grafica.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_pad_l=20,
        title_font_family='verdana',
        title_font_color='black',
        title_font_size=16,
        font_size=15,
        height=400
    )


def sct(varX, varY, co, cocs, x_title, y_title, tam, titulo, marg_x=None, marg_y=None, faceCol=None):
    grafica_sc = px.scatter(df, x=varX, y=varY,
                            color=co,
                            color_continuous_scale=cocs,
                            size=tam,
                            marginal_x=marg_x,
                            marginal_y=marg_y,
                            facet_col=faceCol)

    actualiza_layout(grafica_sc, x_title, y_title)

    return grafica_sc


def histograma(var, tit, subtit, col, cods, textoA, x_titulo, y_titulo, agrupados,
               x_min=0, x_max=0, amplitud=0, varY=None, pshape=None):

    if agrupados:
        grafica_hist = px.histogram(df, x=var, title=tit, subtitle=subtit, text_auto=textoA)
        grafica_hist.update_traces(marker_line_width=1,
                                   xbins=dict(start=x_min, end=x_max, size=amplitud))
    else:
        grafica_hist = px.histogram(df, x=var, y=varY, pattern_shape=pshape,
                                    title=tit, subtitle=subtit, color=col,
                                    color_discrete_sequence=cods, text_auto=textoA)

    actualiza_layout(grafica_hist, x_titulo, y_titulo)

    return grafica_hist


import plotly.figure_factory as ff


def grafica_densidad(var, etiqueta, color):
    _, _, amplitudA = intervalos(var)
    amplitud = amplitudA

    graf_dens = ff.create_distplot([var.tolist()], [etiqueta],
                                   show_hist=True,
                                   show_curve=True,
                                   curve_type='kde',
                                   show_rug=False,
                                   bin_size=amplitud,
                                   colors=[color])

    graf_dens.update_traces(marker_line_width=1)

    graf_dens.update_layout(
        title='Gráfica de densidad: ' + etiqueta,
        xaxis_title='Rango de ' + etiqueta,
        yaxis_title='Frecuencia - Densidad',
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_pad_l=20,
        title_font_family='verdana',
        title_font_color='black',
        title_font_size=16,
        font_size=15,
        height=400
    )

    return graf_dens


def boxplt1(yvar, cds, titulo, x_titulo, y_titulo, col=None, xvar=None, puntos=None):
    grafica_box = px.box(df, x=xvar, y=yvar,
                         points=puntos,
                         color=col,
                         color_discrete_sequence=cds,
                         title=titulo)

    actualiza_layout(grafica_box, x_titulo, y_titulo)

    return grafica_box


# Gráfica Sunburst para sensores por mes y día
grafica_sunb = px.sunburst(df, path=['Mes', 'Día'],
                           values='Watermark Comercial',
                           color='Watermark Comercial',
                           color_continuous_scale=px.colors.sequential.Viridis)

grafica_sunb.update_traces(marker=dict(line=dict(color='darkblue', width=1)))

grafica_sunb.update_layout(
    title='Watermark Comercial por Mes y Día',
    font=dict(family='Courier New, monospace',
              size=14,
              color='darkblue'),
    paper_bgcolor='white',
    height=400
)

# -----------------------------------------------
st.set_page_config(page_title='Tablero - Plantación de Dátiles',
                   layout='wide', page_icon='Imagenes/imagenIco.ico')

st.markdown(
    """
    <style>
    .block-container{
        padding-top:1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
        }
    </style>
    """, unsafe_allow_html=True
)

# Título principal
st.title('Tablero de Monitoreo - Plantación de Dátiles')
st.text('Comparación de sensores de humedad: Watermark Comercial vs Watermark Universitario')

# Métricas generales
colm1, colm2, colm3, colm4 = st.columns(4, vertical_alignment="center", border=True)

with colm1:
    st.metric('Temperatura promedio',
              '%0.2f °C' % temp_media)

with colm2:
    st.metric('Watermark Comercial (promedio)',
              '%0.2f' % wm_comercial_media)

with colm3:
    st.metric('Watermark Universitario (promedio)',
              '%0.2f' % wm_uni_media)

with colm4:
    porcentaje_riego = '%0.1f' % ((total_riegos / len(df)) * 100)
    st.metric('Total de riegos',
              int(total_riegos),
              delta=f'{porcentaje_riego} % del tiempo')

st.markdown('---')

# Sidebar
st.sidebar.header('Logo Empresa')
st.sidebar.image('Imagenes/imagenG.png')

st.sidebar.markdown('---')
st.sidebar.header('Análisis exploratorio de DataSet')
op = st.sidebar.radio('Selecciona:', ['Estadistica', 'Visualizacion'])

if op == 'Visualizacion':
    st.sidebar.markdown('---')

    st.sidebar.header('Visualización exploratoria')
    opcion = st.sidebar.radio('Selecciona:', ['Una variable', 'Dos variables'])

    if opcion == 'Una variable':
        opcionUni = st.sidebar.selectbox('Selecciona una variable',
                                         ['Watermark Comercial', 'Watermark Uni',
                                          'Temperatura', 'Riego', 'Día', 'Mes'])

        col1, col2 = st.columns([0.98, 0.02])

        if opcionUni == 'Watermark Comercial':
            with col1:
                coll_1, coll_2, coll_3 = st.columns(3)
                col_wmc = df['Watermark Comercial']

                with coll_1:
                    x_min, x_max, amplitudA = intervalos(col_wmc)
                    amplitud = '%0.2f' % amplitudA
                    hist_wmc = histograma('Watermark Comercial',
                                          'Frecuencia - Watermark Comercial',
                                          'Sensor comercial de humedad',
                                          'Watermark Comercial', ['steelblue'],
                                          True, 'Rango Watermark Comercial',
                                          'Frecuencia', True,
                                          x_min, x_max, amplitud)
                    st.plotly_chart(hist_wmc, width='stretch')

                with coll_2:
                    densidad_wmc = grafica_densidad(col_wmc, 'Watermark Comercial', 'steelblue')
                    st.plotly_chart(densidad_wmc, width='stretch')

                with coll_3:
                    box_wmc = boxplt1('Watermark Comercial', ['steelblue'],
                                       'Watermark Comercial',
                                       'Sensor comercial', 'Lectura del sensor')
                    st.plotly_chart(box_wmc, width='stretch')

        elif opcionUni == 'Watermark Uni':
            with col1:
                coll_1, coll_2, coll_3 = st.columns(3)
                col_wmu = df['Watermark Uni']

                with coll_1:
                    x_min, x_max, amplitudA = intervalos(col_wmu)
                    amplitud = '%0.2f' % amplitudA
                    hist_wmu = histograma('Watermark Uni',
                                          'Frecuencia - Watermark Universitario',
                                          'Sensor universitario de humedad',
                                          'Watermark Uni', ['darkorange'],
                                          True, 'Rango Watermark Uni',
                                          'Frecuencia', True,
                                          x_min, x_max, amplitud)
                    st.plotly_chart(hist_wmu, width='stretch')

                with coll_2:
                    densidad_wmu = grafica_densidad(col_wmu, 'Watermark Uni', 'darkorange')
                    st.plotly_chart(densidad_wmu, width='stretch')

                with coll_3:
                    box_wmu = boxplt1('Watermark Uni', ['darkorange'],
                                       'Watermark Universitario',
                                       'Sensor universitario', 'Lectura del sensor')
                    st.plotly_chart(box_wmu, width='stretch')

        elif opcionUni == 'Temperatura':
            with col1:
                coll_1, coll_2, coll_3 = st.columns(3)
                col_temp = df['Temperatura (°C)']

                with coll_1:
                    x_min, x_max, amplitudA = intervalos(col_temp)
                    amplitud = '%0.2f' % amplitudA
                    hist_temp = histograma('Temperatura (°C)',
                                           'Frecuencia - Temperatura',
                                           'Temperatura en °C',
                                           'Temperatura (°C)', ['tomato'],
                                           True, 'Rango de Temperatura (°C)',
                                           'Frecuencia', True,
                                           x_min, x_max, amplitud)
                    st.plotly_chart(hist_temp, width='stretch')

                with coll_2:
                    densidad_temp = grafica_densidad(col_temp, 'Temperatura (°C)', 'tomato')
                    st.plotly_chart(densidad_temp, width='stretch')

                with coll_3:
                    box_temp = boxplt1('Temperatura (°C)', ['tomato'],
                                        'Temperatura',
                                        'Temperatura', 'Temperatura (°C)')
                    st.plotly_chart(box_temp, width='stretch')

        elif opcionUni == 'Riego':
            with col1:
                coll_1, coll_2 = st.columns(2)

                with coll_1:
                    hist_riego = histograma('Riego',
                                            'Frecuencia de variable Riego',
                                            'Eventos de riego (0 = Sin riego, 1 = Con riego)',
                                            'Riego', ['seagreen', 'royalblue'],
                                            True, 'Riego', 'Cantidad', False)
                    st.plotly_chart(hist_riego, width='stretch')

                with coll_2:
                    st.plotly_chart(grafica_sunb, width='stretch')

        elif opcionUni == 'Día':
            with col1:
                hist_dia = histograma('Día',
                                       'Frecuencia por Día de la semana',
                                       'Registros agrupados por día',
                                       'Día',
                                       px.colors.qualitative.Pastel,
                                       True, 'Día de la semana', 'Cantidad', False)
                st.plotly_chart(hist_dia, width='stretch')

        elif opcionUni == 'Mes':
            with col1:
                coll_1, coll_2 = st.columns(2)

                with coll_1:
                    hist_mes = histograma('Mes',
                                          'Frecuencia por Mes',
                                          'Registros agrupados por mes',
                                          'Mes',
                                          px.colors.qualitative.Set2,
                                          True, 'Mes', 'Cantidad', False)
                    st.plotly_chart(hist_mes, width='stretch')

                with coll_2:
                    st.plotly_chart(grafica_sunb, width='stretch')

    elif opcion == 'Dos variables':
        opcionBi = st.sidebar.multiselect('Selecciona dos variables',
                                          ['Watermark Comercial', 'Watermark Uni',
                                           'Temperatura'])

        lista1 = ['Watermark Comercial', 'Watermark Uni']
        lista2 = ['Temperatura', 'Watermark Comercial']
        lista3 = ['Temperatura', 'Watermark Uni']

        if len(opcionBi) < 2:
            st.info('Selecciona exactamente dos variables en el panel izquierdo para visualizar.')
        elif set(opcionBi) == set(lista1):
            varX = df['Watermark Comercial']
            varY = df['Watermark Uni']

            coll, col2 = st.columns(2)

            with coll:
                col = 'Riego'
                cocs = 'RdYlGn'
                x_title = 'Watermark Comercial'
                y_title = 'Watermark Uni'
                tamano = None
                titulo = 'Comparación: Watermark Comercial vs Universitario'

                grafica_sc = px.scatter(df, x=varX, y=varY,
                                        color=col,
                                        color_continuous_scale=cocs,
                                        title=titulo)
                actualiza_layout(grafica_sc, x_title, y_title)
                st.plotly_chart(grafica_sc, width='stretch')

            with col2:
                col = 'Mes'
                x_title = 'Watermark Comercial'
                y_title = 'Watermark Uni'
                titulo = 'Comparación de sensores por Mes'

                grafica_sc2 = px.scatter(df, x=varX, y=varY,
                                         color=col,
                                         marginal_x='histogram',
                                         marginal_y='box',
                                         title=titulo)
                actualiza_layout(grafica_sc2, x_title, y_title)
                st.plotly_chart(grafica_sc2, width='stretch')

            col3, col4 = st.columns(2)

            with col3:
                cds_box = ['steelblue', 'darkorange']
                df_melt = df[['Watermark Comercial', 'Watermark Uni']].melt(
                    var_name='Sensor', value_name='Lectura')
                box_comp = px.box(df_melt, x='Sensor', y='Lectura',
                                   color='Sensor',
                                   color_discrete_sequence=cds_box,
                                   points='outliers',
                                   title='Distribución comparativa de sensores')
                actualiza_layout(box_comp, 'Sensor', 'Lectura')
                st.plotly_chart(box_comp, width='stretch')

            with col4:
                col = 'Día'
                x_title = 'Watermark Comercial'
                y_title = 'Watermark Uni'
                titulo = 'Comparación de sensores por Día'

                grafica_sc3 = px.scatter(df, x=varX, y=varY,
                                          color=col,
                                          facet_col='Mes',
                                          title=titulo)
                actualiza_layout(grafica_sc3, x_title, y_title)
                st.plotly_chart(grafica_sc3, width='stretch')

        elif set(opcionBi) == set(lista2):
            varX = df['Temperatura (°C)']
            varY = df['Watermark Comercial']

            coll, col2 = st.columns(2)

            with coll:
                col = 'Riego'
                cocs = 'RdYlGn'
                titulo = 'Temperatura vs Watermark Comercial'
                grafica_sc = px.scatter(df, x=varX, y=varY,
                                        color=col,
                                        color_continuous_scale=cocs,
                                        title=titulo)
                actualiza_layout(grafica_sc, 'Temperatura (°C)', 'Watermark Comercial')
                st.plotly_chart(grafica_sc, width='stretch')

            with col2:
                varY2 = df['Watermark Uni']
                titulo2 = 'Temperatura vs Watermark Universitario'
                grafica_sc2 = px.scatter(df, x=varX, y=varY2,
                                          color='Riego',
                                          color_continuous_scale='RdYlGn',
                                          title=titulo2)
                actualiza_layout(grafica_sc2, 'Temperatura (°C)', 'Watermark Uni')
                st.plotly_chart(grafica_sc2, width='stretch')

            col3, col4 = st.columns(2)

            with col3:
                xvar = 'Riego'
                yvar = 'Watermark Comercial'
                cds = ['steelblue', 'darkorange']
                titulo = 'Watermark Comercial por evento de Riego'
                box_riego = boxplt1(yvar, cds, titulo,
                                     'Riego', 'Watermark Comercial',
                                     'Mes', xvar, 'outliers')
                st.plotly_chart(box_riego, width='stretch')

            with col4:
                xvar = 'Riego'
                yvar = 'Temperatura (°C)'
                cds = ['tomato', 'seagreen']
                titulo = 'Temperatura por evento de Riego'
                box_temp_riego = boxplt1(yvar, cds, titulo,
                                          'Riego', 'Temperatura (°C)',
                                          'Mes', xvar, 'outliers')
                st.plotly_chart(box_temp_riego, width='stretch')

        elif set(opcionBi) == set(lista3):
            varX = df['Temperatura (°C)']
            varY = df['Watermark Uni']

            coll, col2 = st.columns(2)

            with coll:
                titulo = 'Temperatura vs Watermark Universitario'
                grafica_sc = px.scatter(df, x=varX, y=varY,
                                        color='Riego',
                                        color_continuous_scale='RdYlGn',
                                        title=titulo)
                actualiza_layout(grafica_sc, 'Temperatura (°C)', 'Watermark Uni')
                st.plotly_chart(grafica_sc, width='stretch')

            with col2:
                titulo2 = 'Temperatura vs Watermark Uni con marginales'
                grafica_sc2 = px.scatter(df, x=varX, y=varY,
                                          color='Mes',
                                          marginal_x='histogram',
                                          marginal_y='box',
                                          title=titulo2)
                actualiza_layout(grafica_sc2, 'Temperatura (°C)', 'Watermark Uni')
                st.plotly_chart(grafica_sc2, width='stretch')

            col3, col4 = st.columns(2)

            with col3:
                box_uni_riego = boxplt1('Watermark Uni', ['darkorange', 'steelblue'],
                                         'Watermark Uni por evento de Riego',
                                         'Riego', 'Watermark Uni',
                                         'Mes', 'Riego', 'outliers')
                st.plotly_chart(box_uni_riego, width='stretch')

            with col4:
                box_temp_uni = boxplt1('Temperatura (°C)', ['tomato', 'mediumpurple'],
                                        'Temperatura por evento de Riego',
                                        'Riego', 'Temperatura (°C)',
                                        'Mes', 'Riego', 'outliers')
                st.plotly_chart(box_temp_uni, width='stretch')

        else:
            st.warning('Combinación no disponible. Las opciones válidas son: '
                       'Watermark Comercial + Watermark Uni, '
                       'Temperatura + Watermark Comercial, '
                       'Temperatura + Watermark Uni.')

elif op == 'Estadistica':

    st.sidebar.markdown('---')
    st.sidebar.header('Análisis exploratorio')
    opcion_explora = st.sidebar.selectbox('Selecciona:',
                                          ['Visualizar DataFrame', 'Descripcion por Variable',
                                           'Cuartiles', 'T Frecuencias No Agrupados',
                                           'T Frecuencias Agrupados', 'Medidas Centrales',
                                           'Medidas de Dispersion'])

    if opcion_explora == 'Visualizar DataFrame':
        with st.expander('Data Set: Plantación de Dátiles', expanded=False):
            st.markdown('''
            El Data Set contiene **2,232 registros** de monitoreo horario de una plantación de dátiles.
            Compara dos sensores de humedad de suelo tipo Watermark:
            * **Fecha**. Fecha del registro.
            * **Hora**. Hora del registro (00:00 a 23:00).
            * **Día**. Día de la semana del registro.
            * **Mes**. Mes correspondiente al registro.
            * **Temperatura (°C)**. Temperatura ambiente registrada.
            * **Watermark Comercial**. Lectura del sensor de humedad comercial.
            * **Watermark Uni**. Lectura del sensor de humedad desarrollado por la universidad.
            * **Riego**. Indica si hubo evento de riego (1 = sí, 0 = no).
            ''')
        st.dataframe(df, width='stretch')

        col1, col2, col3 = st.columns(3, border=True)
        with col1:
            st.text('Tipos de datos')
            tipos_df = df.dtypes
            st.write(tipos_df)
        with col2:
            info = io.StringIO()
            df.info(buf=info)
            info_df = info.getvalue()
            st.text('Información general')
            st.text(info_df)
        with col3:
            st.text('Describe df')
            describ = df.describe()
            st.write(describ)

    elif opcion_explora == 'Descripcion por Variable':
        coll1, col2, col3 = st.columns([0.3, 0.2, 0.5], border=False)
        with coll1:
            var_col = list(df.columns)
            opcion_col = st.selectbox('Selecciona la variable (describe()): ', var_col)

        with col2:
            describe_col = df[opcion_col].describe()
            st.write(describe_col)

    elif opcion_explora == 'Cuartiles':
        coll1, col2, col3 = st.columns([0.3, 0.2, 0.5], border=False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (cuartiles): ',
                                      ['Temperatura (°C)', 'Watermark Comercial',
                                       'Watermark Uni', 'Riego'])

        with col2:
            cuartiles = df[opcion_col].quantile([0.25, 0.50, 0.75])
            st.write(cuartiles)

    elif opcion_explora == 'T Frecuencias No Agrupados':
        coll1, col2, col3 = st.columns([0.2, 0.6, 0.2], border=False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ',
                                      ['Día', 'Mes', 'Riego'])

        with col2:
            tablaF = sorted(df[opcion_col].unique())
            colF = df[opcion_col]
            nomColF = opcion_col
            t_f = tablaFrecuencia(tablaF, colF, nomColF)
            st.write(t_f)

    elif opcion_explora == 'T Frecuencias Agrupados':
        coll1, col2, col3 = st.columns([0.2, 0.6, 0.2], border=False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Tabla Frecuencias): ',
                                      ['Temperatura (°C)', 'Watermark Comercial', 'Watermark Uni'])

        with col2:
            var_col = df[opcion_col]
            t_fA = tabla_Hist(var_col)
            st.write(t_fA)

    elif opcion_explora == 'Medidas Centrales':
        coll1, col2, col3, col4 = st.columns(4, border=False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas Centrales): ',
                                      ['Temperatura (°C)', 'Watermark Comercial',
                                       'Watermark Uni', 'Riego'])

        with col2:
            media_v = df[opcion_col].mean()
            st.metric('Media', '%0.2f' % media_v)

        with col3:
            mediana_v = df[opcion_col].median()
            st.metric('Mediana', '%0.2f' % mediana_v)

        with col4:
            moda_v = df[opcion_col].mode()
            st.metric('Moda', '%0.2f' % moda_v[0])

    elif opcion_explora == 'Medidas de Dispersion':
        coll1, col2, col3, col4, col5, col6 = st.columns(6, border=False)
        with coll1:
            opcion_col = st.selectbox('Selecciona la variable (Medidas Dispersion): ',
                                      ['Temperatura (°C)', 'Watermark Comercial',
                                       'Watermark Uni', 'Riego'])

        with col2:
            rango_v = df[opcion_col].max() - df[opcion_col].min()
            st.metric('Rango', '%0.2f' % rango_v)

        with col3:
            varianza_v = df[opcion_col].var()
            st.metric('Varianza', '%0.2f' % varianza_v)

        with col4:
            std_v = df[opcion_col].std()
            st.metric('Desviación estándar', '%0.2f' % std_v)

        with col5:
            asimetria_v = df[opcion_col].skew()
            st.metric('Asimetría', '%0.3f' % asimetria_v)

        with col6:
            curtosis_v = df[opcion_col].kurt()
            st.metric('Curtosis', '%0.3f' % curtosis_v)


st.sidebar.markdown('---')
st.sidebar.header('Acerca de')
st.sidebar.info('Dashboard diseñado con fines académicos para la materia')
