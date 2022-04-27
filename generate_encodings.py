import pickle
import face_recognition
import os

encodings_data = []
encodings_names = []

for file in os.listdir(os.fsencode('faces')):
    filename = os.fsdecode(file).strip()
    name = os.path.splitext(filename)[0]
    name_s = name.split('-')
    type_color = name_s[0]+'-'+name_s[1]
    print(type_color)
    encodings_names.append(type_color)

    image = face_recognition.load_image_file('faces/'+filename)
    image_encodings = face_recognition.face_encodings(image)[0]

    encodings_data.append(image_encodings)

print(encodings_data[1])
print('--------------')

with open('encodings_data.pickle', 'wb') as f:
    pickle.dump(encodings_data, f)

with open('encodings_names.pickle', 'wb') as f:
    pickle.dump(encodings_names, f)

# test
with open('encodings_data.pickle', 'rb') as f:
    data = pickle.load(f)

with open('encodings_names.pickle', 'rb') as f:
    data_names = pickle.load(f)

print(list(data)[0])
print(list(data_names))

