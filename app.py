from flask import Flask, render_template, request, Response
from flask_uploads_fix.flask_uploads_fixed import UploadSet, configure_uploads, IMAGES

from webcam_stream import Webcam
from try_on import Webcam_try_on
from ai_recom import comapare

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = './static/client_img_upload/'
configure_uploads(app, photos)

glasses_type = ''
img_path = ''


def gen_cam(camera):
    print('Generating frames!')
    while True:
        frame = camera.framing()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


def photo(camera):
    print('Single photo!')
    frame = camera.framing()
    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


def try_on_cam(camera):
    print('Trying on!')
    while True:
        frame = camera.try_on()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'

def try_on_photo(camera):
    print('Trying on photo!')
    frame = camera.try_on(photo=True)
    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


### front page
@app.route('/')
def index():
    return render_template('index.html')


### image processing
@app.route('/image')
def image():
    return render_template('image_load.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_img():
    global img_path
    if request.method == 'POST' and request.files['photo'].filename:
        filename = photos.save(request.files['photo'])
        img_path = './static/client_img_upload/' + filename
        try:
            best_matches = comapare(img_path)
        except Exception as e:
            print(e)
            print('лицо не найдено, должно быть только одно')  # !!!!
            return render_template('image_load.html')
        return render_template('best_selection.html', best_matches=best_matches)


## for webcam
@app.route('/photo')
def take_photo():
    return render_template('take_photo.html')


@app.route('/cam_video_feed_photo')
def cam_video_feed_photo():
    frame = gen_cam(Webcam())
    print('Sending frames!')
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cam_video_feed_photo_taken')
def cam_video_feed_photo_taken():
    return render_template('photo.html')


@app.route('/recommendations')
def get_recommendations():
    global img_path
    img_path = ''
    try:
        best_matches = comapare()
    except Exception as e:
        print(e)
        print('лицо не найдено, должно быть только одно')  # !!!!
        return render_template('photo.html')
    return render_template('best_selection.html', best_matches=best_matches)


# тут примерка
@app.route('/try-on', methods=["POST"])
def try_on():
    global glasses_type
    glasses_type = request.form.get('type')
    print(glasses_type)
    return render_template('try_on.html')


@app.route('/try-on-stream')
def try_on_stream():
    if img_path != '':
        frame = try_on_photo(Webcam_try_on(glasses_type, img_path))
        return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        print(glasses_type)
        frame = try_on_cam(Webcam_try_on(glasses_type))
        return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0t', port=5000)  # localhost
