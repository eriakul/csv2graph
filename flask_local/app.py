"""
app.py is used to generate the user interface aspect of our project. We integrated the HTML and color palette generation
code into this python file. In the local version of app.py, it saves the uploaded images and palette images to the static
upload_imgs folder. Each time the user hits the home icon, the contents of that folder get removed.
"""

import os
from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, DATA


import glob
from PIL import Image


from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8


app = Flask(__name__)
photos = UploadSet('photos', DATA)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploaded_csv/'
configure_uploads(app, photos)

crop_count = 0


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

#
# @app.route("/sentiment", methods=['GET', 'POST'])
# def sentiment():
#     """
#     sentiment() renders the sentiment.html file
#     :return: rendered html of image sentiment analysis feature
#     """
#     return render_template('sentiment.html')
#
#
# @app.route("/about", methods=['GET', 'POST'])
# def about():
#     """
#     about() renders the about.html file
#     :return: rendered html of about page
#     """
#     return render_template('about.html')


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    """
    This function waits until the user uploads/crops an image, grabs the color palette and color codes,
    and loads the page with the image and palettes displayed.
    :return: rendered template of image page (known as 'image.html') with the image files and color codes passed in
    """
    if request.method == 'POST':
        if "image" in request.files:
            filename = photos.save(request.files["csv"])
            fullname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)

    # create a plot and style its properties
        fig = figure(plot_width=600, plot_height=600)
        fig.vbar(
            x=[1, 2, 3, 4],
            width=0.5,
            bottom=0,
            top=[1.7, 2.2, 4.6, 3.9],
            color='navy'
        )

        # grab the static resources
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        # render template
        script, div = components(fig)
        html = render_template(
            'upload.html',
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
        )
        return encode_utf8(html)

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
    app.run(host=HOST, port=PORT)
