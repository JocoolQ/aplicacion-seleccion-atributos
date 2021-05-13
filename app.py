from flask import Flask, render_template, request, redirect, make_response, send_file
import os
import pandas as pd
import io
from logic.selection import Selector
from logic.verify import Checker
from logic.classify import Discretizer

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')

    elif request.method == 'POST':
        archivo = request.files['file']

        separador = request.form['separador']
        carpeta = os.path.realpath(__file__).replace('\\', '/').split('/')[0:-1]
        archivo.save('/'.join(carpeta) + '/static/uploads/' + archivo.filename)
        df_archivo = pd.read_csv('static/uploads/' + archivo.filename, sep=separador)
        df_head = df_archivo.head()

        df_info = {}

        df_info['head'] = df_archivo.head()
        df_info['size'] = df_archivo.size
        df_info['shape'] = df_archivo.shape
        df_info['types'] = df_archivo.dtypes
        df_info['columns'] = list(df_archivo.columns)

        checker = Checker()
        tipos_attr = checker.check_attributes(df_archivo)
        opciones_attrs = ['Categórico', 'Numérico']

        return render_template('posted.html',
        nombres_cols = df_head.columns.values,
        row_data = list(df_head.values.tolist()),
        nombre_archivo = archivo.filename,
        df_info = df_info,
        tipos_attr = tipos_attr.values(),
        opciones_attrs = opciones_attrs,
        separador = separador,
        zip = zip)

@app.route('/select_categoric/<string:nombre_archivo>/<string:separador>' ,methods=['GET', 'POST'])
def select_attr(nombre_archivo, separador):

    categorias_seleccionadas = request.form.getlist('cat')
    selector = Selector()
    df_archivo = pd.read_csv('static/uploads/' + nombre_archivo, sep=separador)

    #Identifica si todos los atributos son Categóricos o Numéricos, o si existen atributos
    #tanto numéricos como categóricos
    if(len(set(categorias_seleccionadas)) == 1):
        if(categorias_seleccionadas[0] == 'Categórico'):
            mostrar_resultado, atributos_a_eliminar, selected_for_num, substracts = selector.aplicar_seleccion_categorica(df_archivo, nombre_archivo)
        elif(categorias_seleccionadas[0] == 'Numérico'):
            mostrar_resultado, atributos_a_eliminar, substracts = selector.aplicar_seleccion_numerica(df_archivo)
            selected_for_num = 0
    else:
        return redirect('/discretize_attrs/' + nombre_archivo + '/' + separador + '/' + "".join(e + ',' for e in categorias_seleccionadas))
    
    #Encabezados de la tabla de resumen
    result_keys = mostrar_resultado.keys()
    #Valores de la tabla de resumen
    result_values = mostrar_resultado.values()
    #Encabezados de la tabla de entropías
    substract_keys = list(result_keys)[2:]

    return render_template('result.html',
    nombre_archivo = nombre_archivo,
    mostrar_resultado = mostrar_resultado,
    atributos_a_eliminar = atributos_a_eliminar,
    selected_for_num = selected_for_num,
    result_keys = result_keys,
    result_values = result_values,
    categorias_seleccionadas = categorias_seleccionadas[0],
    substracts = substracts,
    substract_keys = substract_keys,
    len = len,
    zip = zip)

@app.route('/discretize_attrs/<string:nombre_archivo>/<string:separador>/<string:categorias_seleccionadas>' ,methods=['GET', 'POST'])
def discretize_attrs(nombre_archivo, separador, categorias_seleccionadas):
    categorias = categorias_seleccionadas.split(',')
    cats_indexes = [index for index, value in enumerate(categorias) if value == 'Categórico']
    nums_indexes = [index for index, value in enumerate(categorias) if value == 'Numérico']
    df_archivo = pd.read_csv('static/uploads/' + nombre_archivo, sep=separador)
    nombres_cols = df_archivo.columns.values
    real_categorias = []
    real_numerics = []
    for index in cats_indexes:
        real_categorias.append(nombres_cols[index])
    
    for index in nums_indexes:
        real_numerics.append(nombres_cols[index])

    min_grupos = range(2, 10)
    
    if request.method == 'POST':
        params = {
            'pivot' : request.form['reference_cat'],
            'max_intervals': request.form['min_group']
        }

        discretizer = Discretizer()
        result, counter = discretizer.discretize(df_archivo, real_numerics, params['pivot'], params['max_intervals'], nombre_archivo)
        colspan_chi = len(list(result.values())[0][0])
        colspan_ranges = len(list(result.values())[0][1])

        return render_template('result_discretize.html',
        result = result,
        counter = counter,
        colspan_chi = colspan_chi,
        colspan_ranges = colspan_ranges)
    
    return render_template('discretize.html',
    nombre_archivo = nombre_archivo,
    separador = separador,
    categorias = real_categorias,
    nombres_cols = nombres_cols,
    min_grupos = min_grupos,
    categorias_seleccionadas = categorias_seleccionadas)
    
@app.route('/download/<string:kind>/', methods=['GET'])
def descarga(kind):
    result = send_file('static/generated/'+ kind +'.csv', as_attachment=True)
    return result

@app.route('/info/')
def get_info():
    return render_template('info.html')

def run():
    app.run(debug = True, host='0.0.0.0')

if __name__ == '__main__':
    run()
