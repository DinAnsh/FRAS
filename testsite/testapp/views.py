#This is where we have functions that handle requests and return responses

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import System_Admin, Student, Team
from django.http import JsonResponse
import json
import base64
from django.core.files.base import ContentFile
from PIL import Image
import pandas as pd
import numpy as np
import face_recognition
import cv2
import os
from .face import extract_face, get_embedding, train
import matplotlib.pyplot as plt

def home(request):
    team_data = Team.objects.all()
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        return render(request, 'testapp/home.html',{'tdata':team_data, 'logged':1, 'UserName': user.get_full_name(), 'UserMail': user.email})
    else:
        return render(request, 'testapp/home.html',{'tdata':team_data,'logged':0})


def user_register(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        # clg = request.POST.get('clg_name','')
        dept = json_data.get('dept','')
        name = json_data.get('name','')
        email = json_data.get('email','')
        password = json_data.get('password','')
        
        if not User.objects.filter(email=email).exists():
            names = name.split()
            username = names[0].lower()+'@'+ dept[:3]

            User.objects.create_user(username, email, password, first_name=names[0],last_name=" ".join(names[1:]) )

            # database entry - Admin model
            admin = System_Admin(dept, name, email, password)
            admin.save()
            return JsonResponse({"message":"You are successfully registered."}, status=200)
        
        else:
            return JsonResponse({'message':'Looks like a user with that email already exists'},status=409)


@never_cache
def user_login(request, reason=''):
    if request.method=='POST':
        if reason!='':          #If CSRF Fails return a json with the reason
            messages.warning(request, reason)
            return redirect('testapp:home')
        
        json_data = json.loads(request.body)
        username = json_data.get('uname', '')
        password = json_data.get('password', '')

        
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # if request.GET.get('next',None):
                #     return redirect(request.GET['next'])
                # else:
                return JsonResponse({"message":"Successfully logged in"},status=200)
            else:
                # messages.warning(request, "Looks like you've entered the wrong password!")
                return JsonResponse({"message":"Looks like you've entered the wrong password"}, status=401)

        else:
            # messages.warning(request, 'Looks like you are not registered!')
            return JsonResponse({"message":"Looks like you are not registered!"}, status=404)
    else:
        return render(request, 'testapp/home.html')


@login_required(login_url='testapp:home')
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        student_data = Student.objects.all()
        team_data = Team.objects.all()
        # request.session['logged']=0
        return redirect('testapp:home')


#if we can provide other data from here to the page then we can show a message to the user 'Login first'
@login_required(login_url='testapp:home')      
def dashboard(request, reason=''):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/dashboard.html', {'UserName': user.get_full_name(), 'UserMail': user.email})


@login_required(login_url='testapp:home')
def update_profile(request):
    if request.method=='POST':
        old_password = request.POST.get('old-password','')
        new_password = request.POST.get('new-password','')
        cnf_password = request.POST.get('confirm-password','')
        
        user = User.objects.get(username=request.user)
        sys_admin = System_Admin.objects.get(email=user.email)

        user = request.user
        if not user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
            return redirect('testapp:dashboard') 
        if new_password != cnf_password:
            messages.error(request, 'The two password fields did not match.')
            return redirect('testapp:dashboard') 
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password was successfully updated!')

        return redirect('testapp:dashboard') 


@login_required(login_url='testapp:home')
def student(request):
    if request.method=='POST' and request.FILES['studentDetails']:
        excel_file = request.FILES['studentDetails']

        skipR = [0,1,2,4] + list(np.linspace(404,408,6, dtype=int))
        df = pd.read_excel(excel_file, skiprows=skipR, usecols='B:J')
        df = df.dropna(subset=['NAME'])
        
        dbEnrolls = list(Student.objects.all().values_list('enroll', flat=True))
        dfEnrolls = df['Enrollment No.'].to_list()
        # print()

        try:
            if(len(dbEnrolls) > len(dfEnrolls)):    # to delete the missing enrolls in the uploaded sheet
                enrolls_to_delete = [x for x in dbEnrolls if x not in dfEnrolls]
                Student.objects.filter(enroll__in = enrolls_to_delete).delete()

            else:       # to add or modify the present enrolls in the uploaded sheet
                for index, row in df.iterrows():
                    student, created = Student.objects.get_or_create(
                        enroll = str(row['Enrollment No.']),
                        defaults={
                            'name': row['NAME'],
                            'email': row['Email'],
                            'mobile': str(int(row['Mobile']))
                        }
                    )
                    if not created:
                        student.name = row['NAME']
                        student.email = row['Email']
                        student.mobile = str(int(row['Mobile']))
                        student.save()

            return JsonResponse({'success': True, 'message': 'Student details uploaded successfully.',})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})

    user = User.objects.get(username=request.user)   
    return render(request, 'testapp/student.html', {'UserName': user.get_full_name(), 'UserMail': user.email,})


@login_required(login_url='testapp:home')
def get_student_data(request):
    selected_class = request.GET.get('class')

    current_year = timezone.now().strftime('%Y')
    # current_month = timezone.now().strftime('%m')

    adm_year = str(int(current_year)-int(selected_class))
    student_data = Student.objects.filter(enroll__startswith=adm_year).values()
    # print(list(student_data))     #list of dicts
    return JsonResponse({'data':list(student_data),}, safe=False)



def get_encodings(image):
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # faces = faceCascade.detectMultiScale(gray,scaleFactor=1.05,
    #                                     minNeighbors=6,
    #                                     flags=cv2.CASCADE_SCALE_IMAGE)
    # for (x,y,w,h) in faces:
    #     cv2.rectangle(image, (x, y), (x + w, y + h),(0,255,0), 2)
    #     faceROI = image[y:y+h,x:x+w]
    
    # convert image from BGR (OpenCV ordering) to dlib ordering (RGB)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb,model='cnn')
    enc = face_recognition.face_encodings(rgb,boxes)
    return enc[0]


def face_recognize(request):
    if request.method =='POST': 
        if request.content_type == 'application/json':
            json_data = json.loads(request.body)   
            img = json_data.get('class_image')
            
            decoded_image_data = base64.b64decode(img.split(',')[1])
            # Create a ContentFile from the decoded image data
            image_file = ContentFile(decoded_image_data, name="Captured Image")
            
        elif 'image' in request.FILES:
            image_file = request.FILES['image']
            
        
        pil_img = Image.open(image_file)
        # pil_img.show()
        
        
        knownEncodings = []
        knownEnroll = []
        
        #need to fetch only particular year students 
        # all_students = Student.objects.all()
        year = '2021'
        all_students = Student.objects.filter(enroll__startswith=year)
        for obj in all_students:
            if obj.encoding is None or obj.encoding == '':
                continue
            
            else:
                # Convert the string back to a NumPy array
                float_array = np.fromstring(obj.encoding[1:-1], dtype=np.float64, sep=' ')
                knownEncodings.append(float_array)
                knownEnroll.append(obj.enroll)           
            
        #save encodings along with their names in dictionary data
        data = {"encodings": knownEncodings, "enrollments": knownEnroll} 
        
        # convert the input frame from BGR to RGB 
        rgb = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BGR2RGB)
        
        # boxes = face_recognition.face_locations(rgb,model='cnn')
        
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        
        enrolls = []
        
        for encoding in encodings:
        #Compare encodings with encodings in data["encodings"]
        #Matches contain array of the same length of data["encodings"] with boolean values and True for the embeddings it matches closely and False for rest
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            
            #set name =inknown if no encoding matches
            enroll = "Unknown"
            
            # check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                
                counts = {}
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    enroll = data["enrollments"][i]
                    
                    #increase count for the name we got
                    counts[enroll] = counts.get(enroll, 0) + 1
                    
                #set name which has highest count
                enroll = max(counts, key=counts.get)
                
            # update the list of names
            enrolls.append(enroll)    
            
        return JsonResponse({"enrolls":enrolls})
    
    else:
        return JsonResponse({"status":"There is some error!"})
                
def train_model(request):
    year = request.GET.get("year")
    X,y = get_embedding(year)
    
    s = train(X,y)
    return JsonResponse({"status":s})

@login_required(login_url='testapp:home')
def upload_image(request):
    if request.method == 'POST':
        # Get the image data from the request
        json_data = json.loads(request.body)
        image_data = json_data.get('image_data')
        enroll_id = json_data.get('enrollId')
        
        year = enroll_id[0:5]
        
        # Decode the base64-encoded image data
        decoded_image_data = base64.b64decode(image_data.split(',')[1])
        
        imgName = enroll_id.replace('/', '')+".png"
        
        # Create a ContentFile from the decoded image data
        image_file = ContentFile(decoded_image_data, name=imgName)
        
        pil_img = Image.open(image_file)
        opencvImage = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BGR2RGB)
        
        # face_encoding = get_encodings(opencvImage)
        
        faces = []
        #need to pass list of 5 images
        # for i in images:
        face_array = extract_face(opencvImage)
        faces.append(face_array)
        
        # if type(face_arrays) == str:
        #     return JsonResponse({'status': 'No face Found!'}, status=200)
        
        # else:  
        # Save the image to a file or database
        student = Student.objects.get(enroll=enroll_id)
        student.img=image_file
        flatten_arr = np.asarray(faces).flatten()
        flat_str = ''
        for i in flatten_arr:
            flat_str+=str(i) + " " 
            
        student.encoding = flat_str
        student.save()
                
        
        # print(f"------------------------{student.encoding}------------------------------")
        # print(f"------------------------{float_array}------------------------------")
        # print(f"-------------------------{len(float_array)}-----------------------")
        # print(f"-------------------------{float_array.reshape(1,160,160,3)}-----------------------")
        # face_recognize(enroll_id)
        # print(student)
        return JsonResponse({'status': 'success'}, status=200)    
    else:
        return JsonResponse({'status': 'fail'})

def sort(request):
    return JsonResponse({"status":"success! sorted"})


@login_required(login_url='testapp:home')
def teacher(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    

@login_required(login_url='testapp:home')
def schedule(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/schedule.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    

@login_required(login_url='testapp:home')
def camera(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/camera.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
