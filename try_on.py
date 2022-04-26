import dlib
import cv2
import face_recognition
import face_recognition_models
import numpy as np
from scipy import ndimage


class Webcam_try_on(object):
    def __init__(self, glasses_type, img_path=''): # хорошо если поток не будет создаваться когда надо только фото
        self.video = cv2.VideoCapture(0)

        self.img_path = img_path

        predictor_68_point_model = face_recognition_models.pose_predictor_model_location()
        self.predictor = dlib.shape_predictor(predictor_68_point_model)

        if glasses_type == 'cat-black':
            print('cat-black')
            self.glasses = cv2.imread("glasses/cat.png", -1)
        elif glasses_type == 'narrow-black':
            print('narrow-black')
            self.glasses = cv2.imread("glasses/narrow.png", -1)
        elif glasses_type == 'round-black':
            print('round-black')
            self.glasses = cv2.imread("glasses/round.png", -1)
        elif glasses_type == 'semi-black':
            print('semi-black')
            self.glasses = cv2.imread("glasses/semi.png", -1)
        elif glasses_type == 'square-black':
            print('square-black')
            self.glasses = cv2.imread("glasses/square.png", -1)
        elif glasses_type == 'square-red':
            print('square-red')
            self.glasses = cv2.imread("glasses/square-red.png", -1)

        cuda_check = dlib.DLIB_USE_CUDA
        print(f'CUDA init: {cuda_check}')

    # Resize an image to a certain width
    def resize(self, img, width):
        r = float(width) / img.shape[1]
        dim = (width, int(img.shape[0] * r))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        return img

    # Combine an image that has a transparency alpha channel
    def blend_transparent(self, face_img, sunglasses_img):
        overlay_img = sunglasses_img[:, :, :3]
        overlay_mask = sunglasses_img[:, :, 3:]

        background_mask = 255 - overlay_mask

        overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
        background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

        face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
        overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

        return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))

    # Find the angle between two points
    def angle_between(self, point_1, point_2):
        angle_1 = np.arctan2(*point_1[::-1])
        angle_2 = np.arctan2(*point_2[::-1])
        return np.rad2deg((angle_1 - angle_2) % (2 * np.pi))

    def try_on(self, photo=False):

        if photo:
            img = cv2.imread(self.img_path)
        else:
            success, img = self.video.read()

        img_copy = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        try:
            dets = face_recognition.face_locations(gray, model='cnn')[0]

            x, y, w, h = dets[3], dets[0], dets[1], dets[2]
            dlib_rect = dlib.rectangle(x, y, w, h)

            detected_landmarks = self.predictor(gray, dlib_rect).parts()

            landmarks = np.matrix([[p.x, p.y] for p in detected_landmarks])

            for idx, point in enumerate(landmarks):
                pos = (point[0, 0], point[0, 1])
                if idx == 0:
                    eye_left = pos
                elif idx == 16:
                    eye_right = pos

                try:
                    # cv2.line(img_copy, eye_left, eye_right, color=(0, 255, 255))
                    degree = np.rad2deg(np.arctan2(eye_left[0] - eye_right[0], eye_left[1] - eye_right[1]))
                except:
                    pass

            ##############   Resize and rotate glasses   ##############

            # Translate facial object based on input object.
            eye_center = (eye_left[1] + eye_right[1]) / 2

            # Sunglasses translation
            glass_trans = int(.1 * (eye_center - y))  # .2

            # resize glasses to width of face and blend static
            face_width = w - x

            # resize_glasses
            glasses_resize = self.resize(self.glasses, face_width)

            # Rotate glasses based on angle between eyes
            yG, xG, cG = glasses_resize.shape
            glasses_resize_rotated = ndimage.rotate(glasses_resize, (degree + 90))
            glass_rec_rotated = ndimage.rotate(img[y + glass_trans:y + yG + glass_trans, x:w], (degree + 90))

            # blending with rotation
            h5, w5, s5 = glass_rec_rotated.shape
            rec_resize = img_copy[y + glass_trans:y + h5 + glass_trans, x:x + w5]
            blend_glass3 = self.blend_transparent(rec_resize, glasses_resize_rotated)
            img_copy[y + glass_trans:y + h5 + glass_trans, x:x + w5] = blend_glass3

            ret, jpeg = cv2.imencode('.jpg', img_copy)
            return jpeg.tobytes()

        except Exception:
            print('что-то пошло не так')
            ret, jpeg = cv2.imencode('.jpg', img_copy)
            return jpeg.tobytes()
