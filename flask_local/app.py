"""
app.py is used to generate the user interface aspect of our project. We integrated the HTML and color palette generation
code into this python file. In the local version of app.py, it saves the uploaded images and palette images to the static
upload_imgs folder. Each time the user hits the home icon, the contents of that folder get removed.
"""





import os
from flask_uploads import UploadSet, configure_uploads, DATA


import glob
from PIL import Image

from flask import Flask, render_template, jsonify, request, url_for
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, AjaxDataSource,CustomJS, Slider, Select, RadioButtonGroup, TextInput, RangeSlider, Div, CheckboxButtonGroup, CheckboxGroup
from bokeh.layouts import widgetbox, column, row
from bokeh.io import output_file, show
from bokeh.palettes import Spectral6
import json
import math

from functions import open_file_into_dictionary

color_palettes = dict(default = ['red', 'green', 'blue', 'purple', 'brown', 'aqua', 'maroon', 'olive', 'gold'],
                     bold = ['#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22'],
                     grayscale = ['#252525', '#525252', '#737373', '#969696', '#bdbdbd', '#d9d9d9', '#f0f0f0'],
                     pastel = ['#b3e2cd', '#fdcdac', '#cbd5e8', '#f4cae4', '#e6f5c9', '#fff2ae', '#f1e2cc', '#cccccc'],
                     rainbow = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43'])

resources = INLINE
js_resources = resources.render_js()
css_resources = resources.render_css()

app = Flask(__name__)
photos = UploadSet('photos', DATA)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploaded_csv/'
configure_uploads(app, photos)

@app.route("/", methods=['GET', 'POST'])
def home():
    """
    This function is automatically called when the main function runs. It renders the home page html file and clears the
    upload_imgs folder
    :return: rendered html of home page (known as 'index.html')
    """

    for infile in glob.glob('static/uploaded_csv/*'):
        os.remove(infile)


    return render_template('index.html')


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    """
    This function waits until the user uploads/crops an image, grabs the color palette and color codes,
    and loads the page with the image and palettes displayed.
    :return: rendered template of image page (known as 'image.html') with the image files and color codes passed in
    """
    if request.method == 'POST' or request.method == 'GET':
        if "csv" in request.files:
            filename = photos.save(request.files["csv"])
            fullname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)

            dictionary = open_file_into_dictionary(fullname)
            keys = list(key.title() for key in dictionary.keys())
            values = [value for value in dictionary.values()]
            color_keys = list(key.title() for key in color_palettes.keys())
            color_values = [value for value in color_palettes.values()]

            xy_source = ColumnDataSource(data=dict(xs=[values[0]], ys=[values[1]], labels = [keys[1]],
            colors = color_palettes['default']))
            variables_source = ColumnDataSource(data = dict(keys = keys, values = values))
            colors_source = ColumnDataSource(data = dict(color_keys = color_keys, color_values = color_values))

            #Create general plot
            plot = figure(plot_width=800, plot_height=600, toolbar_location = 'above')
            plot.title.text_font= 'helvetica'
            plot.title.text_font_size = '18pt'
            plot.title.align = 'center'
            plot.title.text_font_style = 'normal'
            plot.multi_line(xs = 'xs', ys = 'ys', legend = 'labels', line_color = 'colors', source = xy_source)
            plot.min_border = 40


            #Define callbacks
            x_axis_callback = CustomJS(args=dict(xy_source = xy_source, variables_source = variables_source,
             axis = plot.xaxis[0]), code="""
                var xy_data = xy_source.data;
                var variables_data = variables_source.data;
                var string = cb_obj.value;
                var keys = variables_data.keys;
                var index = keys.indexOf(string);
                var values = variables_data.values;

                var y_length = xy_data['ys'].length;
                if (y_length == 0){
                    y_length = 1}
                var new_list = [];
                for (i = 0; i < y_length; i++) {
                new_list.push(values[index])}
                xy_data['xs'] = new_list;

                xy_source.change.emit();

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
            label_x = Div(text="""<h1>X-Axis</h1>""")
            x_axis = Select(title= 'Click to change:', options=keys, value = keys[0] + ' (Click to change.)', callback = x_axis_callback)
            label_y = Div(text="""<br /> <h1>Y-Axis</h1>""")
            y_axis = CheckboxGroup(labels=keys, active=[1], callback = y_axis_callback)
            label_axes = Div(text="""<br /><h1>Modify Labels</h1>""")

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




            #Fine-tuning toolbox callbacks
            legend_labels_callback = CustomJS(args=dict(xy_source = xy_source), code="""
                var xy_data = xy_source.data;
                var labels = cb_obj.value;
                var new_labels = labels.split(", ");
                xy_data['labels'] = new_labels;
                xy_source.change.emit();
             """)

            color_picker_callback = CustomJS(args=dict(xy_source = xy_source, colors_source = colors_source), code="""
                 var xy_data = xy_source.data;
                 var colors_data = colors_source.data;
                 var index = cb_obj.active;
                 var palette = colors_data['color_values'][index];
                 xy_data['colors'] = palette;
                 xy_source.change.emit();
              """)
            #Toolbox
            colors_label = Div(text="""<h3>Change Color Scheme</h3>""", sizing_mode = 'scale_width')
            color_picker = RadioButtonGroup(labels=color_keys, active=0, callback = color_picker_callback)
            labels_label = Div(text="""<br><h3>Edit Legend Labels</h3>""", sizing_mode = 'scale_width')
            legend_labels = TextInput(title = 'Warning: Changing the variables will reset the legend labels.', value="Label 1, Label 2, Label 3...", sizing_mode =  'scale_width')
            legend_labels.js_on_change('value', legend_labels_callback)

            fine_toolbox = widgetbox(colors_label, color_picker, labels_label, legend_labels, sizing_mode = 'scale_width')



            #Integrate with html
            parts = dict(toolbox = toolbox, plot = plot, fine_toolbox = fine_toolbox)
            script, div = components(parts, INLINE)
            return render_template('plotpage.html',
                                   script=script,
                                   toolbox_div=div['toolbox'],
                                   plot_div=div['plot'],
                                   fine_toolbox_div = div['fine_toolbox'],
                                   js_resources=INLINE.render_js(),
                                   css_resources=INLINE.render_css())

        else:
            for infile in glob.glob('static/uploaded_csv/*'):
                os.remove(infile)

            return render_template('index.html')



if __name__ == "__main__":
    # the main function just runs the app
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT, debug = True) #savethis
