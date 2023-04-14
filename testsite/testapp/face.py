import cv2
import os
import numpy as np
from mtcnn import MTCNN
from keras_facenet import FaceNet
from .models import Student
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC


def extract_face(image):
    detector = MTCNN()
    try:
        faces = detector.detect_faces(image)  #[]
        x,y,w,h = faces[0]['box']   #there is only face in image
        x,y = abs(x), abs(y)
        face = image[y:y+h,x:x+w]
        face_arr = cv2.resize(face,(160,160))
        return face_arr
    except Exception as e:
        return f"No face Found! {e}"
    
    
def get_embedding(year:str):
    embedder = FaceNet()  
    
    # year = '2021'
    all_students = Student.objects.filter(enroll__startswith=year)
    
    X = []
    y = []
    
    for obj in all_students:
        if obj.encoding is None or obj.encoding == '':
            continue
            
        else:
            # Convert the string back to a NumPy array
            float_array = np.fromstring(obj.encoding, dtype=np.uint8, sep=' ').reshape(1,160,160,3)
            X.extend(float_array)
            y += [obj.enroll] * len(float_array)    
    
    
    EMBEDDED_X = []
    for img in X:
        face_img = img.astype('float32')  #3D(160X160X3)
        face_img = np.expand_dims(face_img, axis=0)
        #4D (NoneX160X160X3)
        yhat = embedder.embeddings(face_img)
        
        EMBEDDED_X.append(yhat[0])
        
    EMBEDDED_X= np.asarray(EMBEDDED_X)
    
    return EMBEDDED_X, y


def train(X,y):
    encoder = LabelEncoder()
    encoder.fit(y)
    Y_en = encoder.transform(y)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y_en, shuffle=True,random_state=17)
    model = SVC(kernel='linear', probability=True)
    model.fit(X_train,Y_train)
    
    return "Training done"