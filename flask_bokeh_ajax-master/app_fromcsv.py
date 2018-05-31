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
    #Open file and create sources
    dictionary = open_file_into_dictionary('SampleCSV2.csv')
    keys = list(key.title() for key in dictionary.keys())
    values = [value for value in dictionary.values()]
    xy_source = ColumnDataSource(data=dict(xs=[values[0]], ys=[values[1]], labels = [keys[1]],
    colors = ['red', 'green', 'blue', 'purple', 'brown', 'aqua']))
    variables_source = ColumnDataSource(data = dict(keys = keys, values = values))




    #Create general plot
    plot = figure(plot_width=800, plot_height=600, toolbar_location = 'left')
    plot.title.text_font= 'helvetica'
    plot.title.text_font_size = '24pt'
    plot.title.align = 'center'
    plot.title.text_font_style = 'normal'
    plot.multi_line(xs = 'xs', ys = 'ys', legend = 'labels', line_color = 'colors', source = xy_source)


    #Define callbacks
    x_axis_callback = CustomJS(args=dict(xy_source = xy_source, variables_source = variables_source,
     axis = plot.xaxis[0]), code="""
        var xy_data = xy_source.data;
        var variables_data = variables_source.data;
        var index = cb_obj.active;
        var values = variables_data.values;

        var y_length = xy_data['ys'].length;
        var new_list = [];
        for (i = 0; i < y_length; i++) {
        new_list.push(values[index])}
        xy_data['xs'] = new_list;

        xy_source.change.emit();

        var keys = variables_data.keys;
        var label = keys[index];
        axis.axis_label = label;
    """)

    y_axis_callback = CustomJS(args=dict(xy_source = xy_source, variables_source = variables_source,
     axis = plot.yaxis[0]), code="""

        var xy_data = xy_source.data;
        var variables_data = variables_source.data;
        var index_list = cb_obj.active;

        var values = variables_data.values;
        var index_length = index_list.length;
        var keys = variables_data.keys;




        var new_ys = [];
        var new_labels = [];
        for (i = 0; i < index_length; i++) {
            new_ys.push(values[index_list[i]]);
            new_labels.push(keys[index_list[i]])}
        xy_data['labels'] = new_labels;
        xy_data['ys'] = new_ys;

        var x_variable = xy_data['xs'][0];
        var new_x = [];
        for (i = 0; i < index_length; i++) {
            new_x.push(x_variable)}
        xy_data['xs'] = new_x;

        xy_source.change.emit();



    """)

#
# xy_source.change.emit();
#
# var keys = variables_data.keys;
# var label = keys[index_list[0]];
# axis.axis_label = label;
    #Create toolbox
    label_x = Div(text="""X-Axis""", width=200)
    x_axis = RadioButtonGroup(labels=keys, active=0, callback = x_axis_callback)
    label_y = Div(text="""Y-Axis""", width=200)
    y_axis = CheckboxButtonGroup(labels=keys, active=[1], callback = y_axis_callback)
    label_axes = Div(text="""<br />Modify Labels""", width=200)
    title_name = TextInput(title="Title", value='Default Title')
    plot.title.text = title_name.value
    x_name = TextInput(title="X-Axis", value='Default X Label')
    plot.xaxis.axis_label = keys[0]
    y_name = TextInput(title="Y-Axis", value='Default Y Label')
    plot.yaxis.axis_label = keys[1]

    toolbox = widgetbox(label_x, x_axis, label_y, y_axis, label_axes, title_name, x_name, y_name)




    #Integrate with html
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
