import sys
import os.path
from datetime import datetime
import random
from flask import Flask, render_template, request, send_from_directory, url_for
sys.path.append('../QR')
from QR import QR_code

app = Flask(__name__)

def setConvertedCount(count):
    with open('count.data', 'w') as f:
        f.write(str(count))
        f.close()

def getConvertedCount():
    with open('count.data', 'r') as f:
        count = int(f.read())
        f.close()
    return count


@app.route("/counter")
def counter():
    current_count = getConvertedCount()
    return str(current_count)

@app.route("/")
def index():
    current_count = getConvertedCount()
    return render_template("index.html", current_count=current_count)


@app.route("/download")
def download():
    filename = request.args.get('filename')
    arg = ''
    found_exception = False
    if filename is None:
        arg = "argument 'filename' not specified"
        found_exception = True
    if filename == '':
        arg = "argument 'filename' cannot be empty"
        found_exception = True
    if not os.path.isfile(filename):
        arg = "resource no longer exist"
        found_exception = True

    if found_exception:
        return render_template("error.html", error=arg)

    return send_from_directory(directory='./',path=filename)


@app.route("/generate")
def generate():
    filename = str(datetime.now()) + "_" + str(random.randint(0, 10000))
    input_str = request.args.get('encode_str')
    error_correction = request.args.get('ec')
    block_c = tuple(int(request.args.get('block_color').strip('#')[i:i + 2], 16) for i in (0, 2, 4))
    block_a = request.args.get('block_color_alpha')
    background_c = tuple(int(request.args.get('background_color').strip('#')[i:i + 2], 16) for i in (0, 2, 4))
    background_a = request.args.get('background_color_alpha')
    block_color = (block_c[0], block_c[1], block_c[2], int(block_a))
    background_color = (background_c[0], background_c[1], background_c[2], int(background_a))
    resolution = int(request.args.get('resolution'))

    arg = ''
    found_exception = False

    if input_str is None:
        arg += "argument 'encode_str' not provided\n"
        found_exception = True
    if error_correction is None:
        arg += "argument 'ec' not provided\n"
        found_exception = True
    if block_c is None:
        arg += "argument 'block_color' not provided\n"
        found_exception = True
    if block_a is None:
        arg += "argument 'block_color_alpha' not provided\n"
        found_exception = True
    if background_c is None:
        arg += "argument 'background_color' not provided\n"
        found_exception = True
    if background_a is None:
        arg += "argument 'background_color_alpha' not provided\n"
        found_exception = True
    if resolution is None:
        arg += "argument 'resolution' not provided\n"
        found_exception = True
    if resolution > 4000:
        arg += "argument 'resolution' need to be lower than 4000\n"
        found_exception = True
    if resolution < 177:
        arg += "argument 'resolution' need to be equal or larger than 177\n"
        found_exception = True

    if found_exception:
        return render_template("error.html", error=arg)

    print("###########################")
    print("incoming request")
    print(f"str: '{input_str}'")
    print(f"ec: '{error_correction}'")
    print(f"block color: {block_color}")
    print(f"background color: {background_color}")
    print(f"resolution: {resolution}")
    print("###########################")

    try:
        qr = QR_code(input_str, error_correction)
        simple_json = qr.simple_info
        complex_json = qr.complex_info
        qr.SaveToFile(f"static/output/{filename}.bmp", resolution, 2835, block_color, background_color)
    except Exception as e:
        print(e)
        return render_template("error.html", error=e)

    current_count = getConvertedCount()
    setConvertedCount(current_count+1)

    return render_template("generate.html", filename=f"static/output/{filename}.bmp", simple_json=simple_json,
                           complex_json=complex_json, current_count=current_count)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=1234)
