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
        data = {
            'name': request.form['name']
        }

        file_fetched = request.files['file']

        separator = request.form['separator']
        folder = os.path.realpath(__file__).replace('\\', '/').split('/')[0:-1]
        file_fetched.save('/'.join(folder) + '/static/uploads/' + file_fetched.filename)
        df_fetched = pd.read_csv('static/uploads/' + file_fetched.filename, sep=separator)
        df_head = df_fetched.head()

        df_info = {}

        df_info['head'] = df_fetched.head()
        df_info['size'] = df_fetched.size
        df_info['shape'] = df_fetched.shape
        df_info['types'] = df_fetched.dtypes
        df_info['columns'] = list(df_fetched.columns)

        checker = Checker()
        kind_of_attrs = checker.check_attributes(df_fetched)
        attrs_options = ['Categórico', 'Numérico']

        return render_template('posted.html',
        data = data,
        column_names = df_head.columns.values,
        row_data = list(df_head.values.tolist()),
        filename = file_fetched.filename,
        df_info = df_info,
        kind_of_attrs = kind_of_attrs.values(),
        attrs_options = attrs_options,
        separator = separator,
        zip = zip)

@app.route('/select_categoric/<string:filename>/<string:separator>' ,methods=['GET', 'POST'])
def select_attr(filename, separator):

    cats_selected = request.form.getlist('cat')
    selector = Selector()
    df_fetched = pd.read_csv('static/uploads/' + filename, sep=separator)

    if(len(set(cats_selected)) == 1):
        if(cats_selected[0] == 'Categórico'):
            show_result, attr_to_erase, selected_for_num, substracts = selector.apply_categoric_selection(df_fetched, filename)
        elif(cats_selected[0] == 'Numérico'):
            show_result, attr_to_erase, substracts = selector.apply_numeric_selection(df_fetched)
            selected_for_num = 0
    else:
        return redirect('/discretize_attrs/' + filename + '/' + separator + '/' + "".join(e + ',' for e in cats_selected))
    
    result_keys = show_result.keys()
    result_values = show_result.values()
    substract_keys = list(result_keys)[2:]

    return render_template('result.html',
    filename = filename,
    show_result = show_result,
    attr_to_erase = attr_to_erase,
    selected_for_num = selected_for_num,
    result_keys = result_keys,
    result_values = result_values,
    cats_selected = cats_selected[0],
    substracts = substracts,
    substract_keys = substract_keys,
    len = len,
    zip = zip)

@app.route('/discretize_attrs/<string:filename>/<string:separator>/<string:cats_selected>' ,methods=['GET', 'POST'])
def discretize_attrs(filename, separator, cats_selected):
    categories = cats_selected.split(',')
    cats_indexes = [index for index, value in enumerate(categories) if value == 'Categórico']
    nums_indexes = [index for index, value in enumerate(categories) if value == 'Numérico']
    df_fetched = pd.read_csv('static/uploads/' + filename, sep=separator)
    column_names = df_fetched.columns.values
    real_categories = []
    real_numerics = []
    for index in cats_indexes:
        real_categories.append(column_names[index])
    
    for index in nums_indexes:
        real_numerics.append(column_names[index])

    min_groups = range(2, 10)
    
    if request.method == 'POST':
        params = {
            'pivot' : request.form['reference_cat'],
            'max_intervals': request.form['min_group']
        }

        discretizer = Discretizer()
        result, counter = discretizer.discretize(df_fetched, real_numerics, params['pivot'], params['max_intervals'], filename)
        colspan_chi = len(list(result.values())[0][0])
        colspan_ranges = len(list(result.values())[0][1])

        return render_template('result_discretize.html',
        result = result,
        counter = counter,
        colspan_chi = colspan_chi,
        colspan_ranges = colspan_ranges)
    
    return render_template('discretize.html',
    filename = filename,
    separator = separator,
    categories = real_categories,
    column_names = column_names,
    min_groups = min_groups,
    cats_selected = cats_selected)
    
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
