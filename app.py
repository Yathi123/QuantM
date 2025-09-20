#!flask/bin/python
import os
import io
import PIL
from PIL import Image, ImageDraw, ImageFont
import json as simplejson
import traceback
import cv2
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import base64
from lib.upload_file import uploadfile
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = 'data/'
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'rar', 'zip', '7zip', 'doc', 'docx'])
IGNORED_FILES = set(['.gitignore'])

bootstrap = Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename


def create_thumbnail(image):
    try:
        base_width = 80
        size = 12
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        fnt = ImageFont.truetype('arial.ttf', 20)

        area, pixels = calculate_object_area(os.path.join(app.config['UPLOAD_FOLDER'], image))
        text = ' Number of cells/mL : ' + str(pixels)
        image1 = Image.new(mode = "RGB", size = (int(size)*len(text),size+30), color = "blue")
        draw = ImageDraw.Draw(image1)
        draw.text((10,10), text, font=fnt, fill=(255,255,0))
        image1.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        #img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        #img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print(traceback.format_exc())
        return False


def calculate_object_area(image):
    image = cv2.imread(image)

    height= image.shape[0]
    width = image.shape[1]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)

    pixels = cv2.countNonZero(thresh1)
    
    total_pix = height * width

    total_black_pix = total_pix - pixels

    Percentage_of_black_pix = (total_black_pix / total_pix) * 100
    
    whole_number = percent_of_black_pix * 100
    conc = whole_number/0.0017
    
    print("Number of Black pixels", total_black_pix)
    print("Total pixels:", total_pix)
    #print("Fraction of black_pix:", fraction_of_black_pix)
    print("Number of cells / mL:", conc)

    return total_black_pix, conc


@app.route("/export_photo", methods=['GET', 'POST'])
def export_photo():
    # file = request.files['file']
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect(url_for('index'))


@app.route("/capture_photo", methods=['GET', 'POST'])
def capture_photo():
    # Initialize the camera
    camera = cv2.VideoCapture(1)  # 0 represents the default camera

    # Check if the camera opened successfully
    if not camera.isOpened():
        print("Error: Could not open camera.")
        exit()

    # Stabilize the camera
    for _ in range(40):  # Capture a few frames to allow the camera to stabilize
        _, _ = camera.read()

    # Capture a frame from the camera
    ret, frame = camera.read()

    # Release the camera
    camera.release()

    # Check if the frame was captured successfully
    if not ret:
        print("Error: Could not capture frame from the camera.")
        exit()

    # Define coordinates for cropping
    x, y, width, height = 0, 30, 405, 410

    # Crop the frame
    cropped_frame = frame[y:y+height, x:x+width]

    # Convert the captured frame to grayscale
    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to the grayscale image
    _, thresholded_image = cv2.threshold(gray_frame, 80, 255, cv2.THRESH_BINARY)

    hight = thresholded_image.shape[0]
    width = thresholded_image.shape[1]

    # Count the number of non-zero pixels in the thresholded image
    pixels = cv2.countNonZero(thresholded_image)

    total_pix = hight * width
    total_black_pix = total_pix - pixels

    percent_of_black_pix = (total_black_pix / total_pix) * 100

    decimal_reducer = percent_of_black_pix * 100
    conc = decimal_reducer/0.0017


    # Display the original frame and the thresholded image
    #cv2.imshow("Original Frame", frame)
    #cv2.imshow("Thresholded Image", thresholded_image)
    #cv2.imshow("cropped region", cropped_frame)

    print("White pixels:", pixels)
    print("Black pixels:", total_black_pix)
    print("Percent of black pixels:", percent_of_black_pix)
    print("Number of cells / mL:", conc)

    if 'values' in session:
        animal_id = request.form.get('animal_id')
        session['values'].append({'animal_id': animal_id, 'conc': conc})
    else:
        session['values'] = []
    session.modified = True

    ret, jpeg = cv2.imencode('.jpg', cropped_frame)
    jpg_as_text = base64.b64encode(jpeg)

    ret, jpeg1 = cv2.imencode('.jpg', thresholded_image)
    jpg_as_text1 = base64.b64encode(jpeg1)

    
    return render_template('index.html', cropped=jpg_as_text.decode('utf-8'), thresholded=jpg_as_text1.decode('utf-8'))


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']

        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                files.save(uploaded_file_path)

                # create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename)
                
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)) and f not in IGNORED_FILES ]
        
        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('index'))


@app.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)

            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)
            
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


# serve static files
@app.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], path=filename)


@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), path=filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'values' not in session:
        session['values'] = []
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
