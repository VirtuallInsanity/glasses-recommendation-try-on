import face_recognition
import pickle


def comapare(path_to_img='static/client_img/client.jpg'):

    encodings_data = list(pickle.load(open('encodings_data.pickle', 'rb')))
    encodings_names = list(pickle.load(open('encodings_names.pickle', 'rb')))
    print(encodings_names)

    client_image = face_recognition.load_image_file(path_to_img)
    client_encodings = face_recognition.face_encodings(client_image)[0]

    face_distances = list(face_recognition.face_distance(encodings_data, client_encodings))
    print(face_distances)
    distance_name_best = sorted(zip(face_distances, encodings_names), reverse=True)[:3]

    top1 = distance_name_best[0]
    top2 = distance_name_best[1]
    top3 = distance_name_best[2]

    return top1, top2, top3
