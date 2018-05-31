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
from bokeh.models import ColumnDataSource, AjaxDataSource,CustomJS, Slider, Select, RadioButtonGroup, TextInput, RangeSlider, Div, CheckboxButtonGroup
from bokeh.layouts import widgetbox, column, row
from bokeh.io import output_file, show
from bokeh.palettes import Spectral6
import json
import math

from functions import open_file_into_dictionary

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




    # create a plot and style its properties

    # Set up data




        # fig = figure(plot_width=600, plot_height=600)
        # fig.vbar(
        #     x=[1, 2, 3, 4],
        #     width=0.5,
        #     bottom=0,
        #     top=[1.7, 2.2, 4.6, 3.9],
        #     color='navy'
        # )

        # grab the static resources


        # js_resources = INLINE.render_js()
        # css_resources = INLINE.render_css()
        #
        # # render template
        # script, div = components(fig)
        # html = render_template(
        #     'uploadstrata.html',
        #     plot_script=script,
        #     plot_div=div,
        #     js_resources=js_resources,
        #     css_resources=css_resources,
        # )
        # return encode_utf8(html)

    # global crop_count
    # # initializing variables passed into image.html
    # bounds = ""
    # filename2 = ""
    # color_names1 = []
    # color_names2 = []
    # color_names3 = []
    # hex1 = []
    # hex2 = []
    # hex3 = []
    # rgb1 = []
    # rgb2 = []
    # rgb3 = []
    # if request.method == 'POST':
    #     # check if user uploaded an image
    #     if "image" in request.files:
    #         filename = photos.save(request.files["image"])
    #         fullname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    #         img = Image.open(fullname)
    #         extension = filename.split(".")[-1]
    #         if extension in ['jpeg', 'jpg', 'JPG', 'JPEG']:
    #             extension = extension.lower()
    #         if extension in ['png']:
    #             extension = extension.lower()
    #             img = img.convert('RGB')
    #
    #         # resize the uploaded image if it is too big
    #         resized_img = crop_img.resize(img)
    #         resized_img.save(fullname)
    #         filename2 = fullname
    #
    #         # generate classic palette type
    #         palette1, rgb1, hex1 = main.generate(img, 3)
    #         palettes1 = crop_img.crop_palette(palette1)
    #
    #         color_names1 = []
    #
    #         for ind, color in enumerate(palettes1):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette1" + filename[-1 * (len(extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette1_" + str(ind) + filename[
    #                                                                                          -1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names1.append(name)
    #
    #         # generate default palette type
    #         palette2, rgb2, hex2 = main.generate(img, 1)
    #         palettes2 = crop_img.crop_palette(palette2)
    #
    #         color_names2 = []
    #
    #         for ind, color in enumerate(palettes2):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette2" + filename[-1 * (len(extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette2_" + str(ind) + filename[
    #                                                                                          -1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names2.append(name)
    #
    #         # generate analogous palette type
    #         palette3, rgb3, hex3 = main.generate(img, 2)
    #         palettes3 = crop_img.crop_palette(palette3)
    #
    #         color_names3 = []
    #
    #         for ind, color in enumerate(palettes3):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette3" + filename[-1 * (len(extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = fullname[0:-1 * (len(extension) + 1)] + "_palette3_" + str(ind) + filename[
    #                                                                                          -1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names3.append(name)
    #
    #     # check if user cropped an image
    #     if "bounds" in request.form:
    #         crop_count += 1
    #         text = request.form['img']
    #         bounds = request.form['bounds']
    #         text = str(text[22:])
    #         img = Image.open(text)
    #         extension = text.split(".")[-1]
    #         filename2 = text
    #         if extension in ['jpeg', 'jpg', 'JPG', 'JPEG']:
    #             extension = extension.lower()
    #         if extension in ['png']:
    #             extension = extension.lower()
    #             img = img.convert('RGB')
    #         # crop the image
    #         cropped_img = crop_img.crop_img(img, bounds)
    #
    #         # generate classic palette type
    #         palette1, rgb1, hex1 = main.generate(cropped_img, 3)
    #         palettes1 = crop_img.crop_palette(palette1)
    #
    #         color_names1 = []
    #
    #         for ind, color in enumerate(palettes1):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette1_crop" + str(crop_count) + filename2[
    #                                                                                                      -1 * (len(
    #                                                                                                          extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette1_crop" + str(crop_count) + str(
    #                     ind) + filename2[-1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names1.append(name)
    #
    #         # generate default palette type
    #         palette2, rgb2, hex2 = main.generate(cropped_img, 1)
    #         palettes2 = crop_img.crop_palette(palette2)
    #
    #         color_names2 = []
    #
    #         for ind, color in enumerate(palettes2):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette2_crop" + str(crop_count) + filename2[
    #                                                                                                      -1 * (len(
    #                                                                                                          extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette2_crop" + str(crop_count) + str(
    #                     ind) + filename2[
    #                            -1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names2.append(name)
    #
    #         # generate analogous palette type
    #         palette3, rgb3, hex3 = main.generate(cropped_img, 2)
    #         palettes3 = crop_img.crop_palette(palette3)
    #
    #         color_names3 = []
    #
    #         for ind, color in enumerate(palettes3):
    #             # save each palette image into the upload_imgs folder
    #             if ind == 5:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette3_crop" + str(crop_count) + filename2[
    #                                                                                                      -1 * (len(
    #                                                                                                          extension) + 1):]
    #                 color.save(name)
    #             else:
    #                 name = filename2[0:-1 * (len(extension) + 1)] + "_palette3_crop" + str(crop_count) + str(
    #                     ind) + filename2[
    #                            -1 * (len(extension) + 1):]
    #                 color.save(name)
    #             color_names3.append(name)
    #
    # return render_template('image.html', filename1=filename2, filename2=color_names1, hex1=hex1, rgb1=rgb1,
    #                        filename3=color_names2, hex2=hex2, rgb2=rgb2, filename4=color_names3, hex3=hex3, rgb3=rgb3,
    #                        bounds=bounds)


if __name__ == "__main__":
    # the main function just runs the app
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT, debug = True) #savethis
