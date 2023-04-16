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
from .models import System_Admin, Student, Team, Teacher
from django.http import JsonResponse
import json
import base64
from django.core.files.base import ContentFile
from PIL import Image
import pandas as pd
import numpy as np



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


@login_required(login_url='testapp:home')
def upload_image(request):
    if request.method == 'POST':
        # Get the image data from the request
        json_data = json.loads(request.body)
        image_data = json_data.get('image_data')
        enroll_id = json_data.get('enrollId')
        
        # Decode the base64-encoded image data
        decoded_image_data = base64.b64decode(image_data.split(',')[1])
        
        imgName = enroll_id.replace('/', '')+".png"
        
        # Create a ContentFile from the decoded image data
        image_file = ContentFile(decoded_image_data, name=imgName)
        
        # Save the image to a file or database
        student = Student.objects.get(enroll=enroll_id)
        student.img=image_file
        student.save()
        # print(student)
        
        return JsonResponse({'status': 'success'}, status=200)    
    else:
        return JsonResponse({'status': 'fail'})


@login_required(login_url='testapp:home')
def teacher(request):
    if request.method=='POST' and request.FILES['teacherDetails']:
        excel_file = request.FILES['teacherDetails']

        skipR = [0,1,2]
        df = pd.read_excel(excel_file, skiprows=skipR, usecols=[0,1,3,4,5])
        df = df.dropna(subset=['NAME'])
        # print(df)

        dbEmails = list(Teacher.objects.all().values_list('email', flat=True))
        dfEmails = df['Email'].to_list()

        try:
            if(len(dbEmails) > len(dfEmails)):    # to delete the missing teachers in the uploaded sheet
                emails_to_delete = [x for x in dbEmails if x not in dfEmails]
                Teacher.objects.filter(email__in = emails_to_delete).delete()

            else:       # to add or modify the present teachers in the uploaded sheet
                for index, row in df.iterrows():
                    teacher, created = Teacher.objects.get_or_create(
                        email = str(row['Email']),
                        defaults={
                            'name': row['NAME'],
                            'id': int(row['S.N0']),
                            'mobile': str(int(row['Mobile'])),
                            'subjects': row['Subjects']
                        }
                    )
                    if not created:
                        teacher.name = row['NAME']
                        teacher.id = int(row['S.N0'])
                        teacher.mobile = str(int(row['Mobile']))
                        teacher.subjects = row['Subjects']
                        teacher.save()

            return JsonResponse({'success': True, 'message': 'Teacher details uploaded successfully.',})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})
    
    user = User.objects.get(username=request.user)
    teacherData = list(Teacher.objects.all().values_list())
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'teachers':teacherData})
    

@login_required(login_url='testapp:home')
def schedule(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/schedule.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    

@login_required(login_url='testapp:home')
def camera(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/camera.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
