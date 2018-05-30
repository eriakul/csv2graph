from flask import Flask, render_template, jsonify, request, url_for
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, AjaxDataSource,CustomJS, Slider, Select, RadioButtonGroup, TextInput, RangeSlider, Div, CheckboxButtonGroup
from bokeh.layouts import widgetbox, column, row
from bokeh.io import output_file, show
from bokeh.palettes import Spectral6
import json
import math

from functions import open_file_into_dictionary
# Some parts of the code was addopted from https://stackoverflow.com/questions/37083998/flask-bokeh-ajaxdatasource

resources = INLINE
js_resources = resources.render_js()
css_resources = resources.render_css()

app = Flask(__name__)

# To prevent caching files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def home():
    dictionary = open_file_into_dictionary('SampleCSV2.csv')
    keys = list(key.title() for key in dictionary.keys())
    values = [value for value in dictionary.values()]
    source = ColumnDataSource(data=dict(x=values[0], y=values[1]))
    source2 = ColumnDataSource(data = dict(keys = keys, values = values))
    print(values)




    plot = figure(plot_width=800, plot_height=600, toolbar_location = 'left')
    plot.title.text_font= 'helvetica'
    plot.title.text_font_size = '24pt'
    plot.title.align = 'center'
    plot.title.text_font_style = 'normal'

    plot.line('x', 'y', source = source, line_width=3, line_alpha=0.6)
    plot.multi_line(xs = [[10,20, 30],[10, 20, 30]], ys = [[12,30,40],[1, 20,30]])

    x_axis_callback = CustomJS(args=dict(source=source, source2 = source2, axis = plot.xaxis[0]), code="""
        var data = source.data;
        var data2 = source2.data;
        var index = cb_obj.active;
        var keys = data2.keys;
        var label = keys[index];
        axis.axis_label = label;
        var values = data2.values;
        var new_list = values[index];
        var x = data['x'];
        var y = data['y'];
        for (var i = 0; i < x.length; i++) {
                x[i] = new_list[i];
            }
        source.change.emit();
    """)



    label_x = Div(text="""X-Axis""", width=200)
    x_axis = RadioButtonGroup(labels=keys, active=0, callback = x_axis_callback)
    label_y = Div(text="""Y-Axis""", width=200)
    y_axis = CheckboxButtonGroup(labels=keys, active=[1])
    label_axes = Div(text="""<br />Modify Labels""", width=200)
    title_name = TextInput(title="Title", value='Default Title')
    plot.title.text = title_name.value
    x_name = TextInput(title="X-Axis", value=keys[0])
    plot.xaxis.axis_label = x_name.value
    y_name = TextInput(title="Y-Axis", value=keys[1])
    plot.yaxis.axis_label = y_name.value





    toolbox = widgetbox(label_x, x_axis, label_y, y_axis, label_axes, title_name, x_name, y_name)





    parts = dict(toolbox = toolbox, plot = plot)
    script, div = components(parts, INLINE)
    return render_template('plotpage.html',
                           script=script,
                           toolbox_div=div['toolbox'],
                           plot_div=div['plot'],
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css())




my_data = {'one': [1, 3, 5],
           'two': [2, 7, 5],
           'three': [8, 3, 6]}


@app.route('/new_option', methods=['POST'])
def new_option():
    json.dumps(request.form)
    option = request.form['value']
    return jsonify(option=my_data[option])


@app.route('/ajax', methods=["POST", "GET"])
def ajax():
    x = [1, 2, 3]
    source = ColumnDataSource(data=dict(x=x, y=my_data['one']))
    plot = figure(height=250, width=300)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.8)
    callback = CustomJS(args=dict(source=source), code="""
    var selected_value = cb_obj.value;
    var plot_data = source.data;
    jQuery.ajax({
        type: 'POST',
        url: '/new_option',
        data: {"value": selected_value},
        dataType: 'json',
        success: function (response) {
            plot_data['y'] = response["option"];
            source.trigger('change');
        },
        error: function() {
            alert("An error occured!");
        }
    });
    """)

    select = Select(value='one',
                    options=['one', 'two', 'three'],
                    callback=callback)

    layout = column(widgetbox(select, width=100), plot)
    script, div = components(layout, INLINE)
    return jsonify(script=script,
                   div=div,
                   js_resources=INLINE.render_js(),
                   css_resources=INLINE.render_css())


x1, y = 0, 0


@app.route("/data", methods=['POST'])
def get_x():
    global x1, y
    x1 = x1 + 0.1
    y = math.sin(x1)
    return jsonify(x=[x1], y=[y])


@app.route("/stream", methods=["POST"])
def simple():
    source = AjaxDataSource(data_url="http://127.0.0.1:5000/data",
                            polling_interval=500, mode='append',
                            max_size=30)
    source.data = dict(x=[], y=[])

    fig = figure(height=250, width=450)
    fig.circle('x', 'y', source=source)

    script, div = components(fig, INLINE)

    return jsonify(
        script=script,
        div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css()
    )


if __name__ == "__main__":
    app.run(debug=True)
