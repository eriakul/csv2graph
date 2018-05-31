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
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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
        if (y_length == 0){
            y_length = 1}
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

        if (index_length > 0){
            var x_variable = xy_data['xs'][0];
            var new_x = [];
            for (i = 0; i < index_length; i++) {
                new_x.push(x_variable)}
            xy_data['xs'] = new_x;}

        xy_source.change.emit();

        var y_axis_name = keys[[index_list[0]]];
        for (i = 1; i < index_length; i++) {
            y_axis_name += ", " + keys[[index_list[i]]];}
        axis.axis_label = y_axis_name;
    """)

    title_callback = CustomJS(args= dict(title = plot.title), code="""
        var title_text = cb_obj.value;
        title.text = title_text;

    """)
    x_name_callback = CustomJS(args=dict(axis = plot.xaxis[0]), code="""
        var label_text = cb_obj.value;
        axis.axis_label = label_text;
         """)

    y_name_callback = CustomJS(args=dict(axis = plot.yaxis[0]), code="""
        var label_text = cb_obj.value;
        axis.axis_label = label_text;
         """)


    #Create toolbox
    label_x = Div(text="""X-Axis""", width=200)
    x_axis = RadioButtonGroup(labels=keys, active=0, callback = x_axis_callback)
    label_y = Div(text="""Y-Axis""", width=200)
    y_axis = CheckboxButtonGroup(labels=keys, active=[1], callback = y_axis_callback)
    label_axes = Div(text="""<br />Modify Labels""", width=200)

    title_name = TextInput(title="Title", value='Default Title')
    plot.title.text = title_name.value
    title_name.js_on_change('value', title_callback)

    x_name = TextInput(title="X-Axis", value='Default X Label')
    plot.xaxis.axis_label = keys[0]
    x_name.js_on_change('value', x_name_callback)
    y_name = TextInput(title="Y-Axis", value='Default Y Label')
    plot.yaxis.axis_label = keys[1]
    y_name.js_on_change('value', y_name_callback)

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





if __name__ == "__main__":
    app.run(debug=True)
