import cv2
import numpy as np
from mtcnn import MTCNN
from keras_facenet import FaceNet
from .models import Student
from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
from django.utils import timezone

detector = MTCNN()
embedder = FaceNet()  


def extract_face(image):
    '''
    the function takes an image as input, detects faces in the image, crops and resizes the detected faces, and returns a list of cropped face arrays.\n
    image: OpenCV image array\n
    return: array of faces
    '''
    face_arr = []
    # detector = MTCNN()
    try:
        faces = detector.detect_faces(image)    #returns a list of detected faces in the form of dictionaries
        for f in faces:
            x,y,w,h = f['box']                  #there is only face in image
            x,y = abs(x), abs(y)
            #crops the face from the input image and resizes it to a fixed size of 160x160 pixels
            face = image[y:y+h,x:x+w]
            crop_face_arr = cv2.resize(face,(160,160))      # 3d array of face - (160x160x3)
            face_arr.append(crop_face_arr)
        return face_arr
    except Exception as e:
        return f"No face Found! {e}"
    
    
def get_embedding(year:str):
    '''
    Parameter-
    year: Class Year of the student \n
    returns the EMBEDDED_X and y arrays.
    '''
    current_year = timezone.now().strftime('%Y')
    # current_month = timezone.now().strftime('%m')

    adm_year = str(int(current_year)-int(year))  #2,3
    # embedder = FaceNet()  
    
    # fetches all the students' data from the database whose enrollment numbers start with the admission year
    all_students = Student.objects.filter(enroll__startswith=adm_year)
    
    X = []
    y = []
    
    for obj in all_students:
        if obj.encoding is None or obj.encoding == '':
            continue
            
        else:
            # Convert the string back to a NumPy array
            float_array = np.fromstring(obj.encoding, dtype=np.uint8, sep=' ').reshape(5,160,160,3)
            X.extend(float_array)   #
            en = "".join(obj.enroll.split("/")[0::2])     #2019140
            y += [en] * len(float_array)    
    
    
    EMBEDDED_X = []
    for img in X:
        face_img = img.astype('float32')  #3D(160X160X3)
        face_img = np.expand_dims(face_img, axis=0)   #4D (NoneX160X160X3)
        yhat = embedder.embeddings(face_img)
        
        EMBEDDED_X.append(yhat[0])
        
    EMBEDDED_X= np.asarray(EMBEDDED_X)
    y = np.asarray(y,dtype=int)
    
    # global class_names              #need to store in a numpy file .npz
    # class_names = np.unique(y)
    # np.savez("Classes", array1=class_names)
    return EMBEDDED_X, y


def train(X,y,year):
    '''
    This function trains a Support Vector Machine (SVM) model using the provided training data X and y. It saves the trained model as a pickle file with a name specified using the year parameter.
    '''
    # X_train, X_test, Y_train, Y_test = train_test_split(X,y, shuffle=True,random_state=17)
    model = SVC(kernel='linear', probability=True)
    model.fit(X,y)
    
    filename = 'model'+year+'.pkl'  # Specify the filename
    with open(filename, 'wb') as file:
        pickle.dump(model, file)
        
    return "Training done"


def makePrediction(image, class_year):
    '''
    This function takes an image and a class year as input and returns the predicted labels of the faces in the image.
    '''
    # embedder = FaceNet()
    faces =  extract_face(image)   
    year = class_year

    EMBEDDED_X = []
    for img in faces:
        face_img = img.astype('float32')  #3D(160X160X3)
        face_img = np.expand_dims(face_img, axis=0)   #4D (NoneX160X160X3)
        yhat = embedder.embeddings(face_img)
        
        EMBEDDED_X.append(yhat[0])
        
    EMBEDDED_X= np.asarray(EMBEDDED_X)
    
    if EMBEDDED_X.ndim == 1:
        return "No face Found!"
    
    # global model                #need to store using pickle
    # global class_names
    try:    
        filename = 'model'+year+'.pkl' 
        with open(filename, 'rb') as file:
            model = pickle.load(file)
    except Exception as e:
        return f"Model not trained {e}"    
    # class_names = np.load("Classes.npz")['array1']
        
    prob_scores = model.predict_proba(EMBEDDED_X) 
    threshold = 0.2
    predictions = []
    for label_scores in prob_scores:
        # print("-------------------",label_scores)
        # print("-------------------",model.classes_)
        max_confidence = max(label_scores)
        if max_confidence >= threshold:
            pred_label = model.classes_[label_scores.argmax()]
            
        else:
            pred_label = "Unknown"
            
        predictions.append(pred_label)
            
    return predictions
    