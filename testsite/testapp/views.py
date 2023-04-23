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
from .models import *
from django.http import JsonResponse
from django.core.files.base import ContentFile
from PIL import Image
import base64
import json
import pandas as pd
import numpy as np
from datetime import datetime



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
                if Camera.objects.all() and Classroom.objects.all():
                    return JsonResponse({"message":"Successfully logged in"},status=200)
                else:
                    if not Class.objects.exists():
                        instances = [
                            Class(id=2, name='Second Year'),
                            Class(id=3, name='Third Year'),
                            Class(id=4, name='Final Year'),
                        ]
                        Class.objects.bulk_create(instances)
                    return JsonResponse({"message":"Successfully logged in", 'status':'first_time'})
            else:
                return JsonResponse({"message":"Looks like you've entered the wrong password"}, status=401)

        else:
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
    student_data = Student.objects.filter(enroll__startswith=adm_year).values().order_by('enroll')
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
        df = pd.read_excel(excel_file, skiprows=skipR, usecols=[0,1,3,4,5], index_col='S.N0')
        df = df.dropna(subset=['NAME'])
        df.index = df.index.astype(int)

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
                            'id': index,
                            'mobile': str(int(row['Mobile'])),
                            'subjects': row['Subjects']
                        }
                    )
                    if not created:
                        teacher.name = row['NAME']
                        teacher.id = index
                        teacher.mobile = str(int(row['Mobile']))
                        teacher.subjects = row['Subjects']
                        teacher.save()

            save_subjects(df.loc[:,['Subjects']])   # to save relevant data to the Subject model
            return JsonResponse({'success': True, 'message': 'Details are uploaded successfully.',})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})
    
    user = User.objects.get(username=request.user)
    teacherData = list(Teacher.objects.all().values_list())
    teacherData.sort(key=lambda x: int(x[1]))
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'teachers':teacherData})
    

@login_required(login_url='testapp:home')
def schedule(request):
    selected_class = request.GET.get('class')
    if request.method=='POST' and request.FILES['timeTable']:
        excel_file = request.FILES['timeTable']

        skipR = [0,1,2,3,4]
        df = pd.read_excel(excel_file, skiprows=skipR, usecols='A:I', index_col='Day')
        df.fillna('-', inplace=True)

        try:
            db_entry = clean_schedule(df)
            class_obj = Class.objects.get(id = selected_class)
            
            dict_data = [{'day_of_week': row[0], 'class_id': class_obj,
                          'start_time': datetime.strptime(row[1], '%H').time(), 
                          'end_time': datetime.strptime(row[2], '%H').time(), 
                          'subject': row[3]} for row in db_entry]

            # to delete old records
            if Schedule.objects.filter(class_id = selected_class).values_list():
                Schedule.objects.filter(class_id = selected_class).delete()
            
            # an efficient way to create multiple instances of a model at once
            Schedule.objects.bulk_create([Schedule(**row) for row in dict_data])
            return JsonResponse({'success': True, 'message': 'Schedule is uploaded successfully.'})           
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})
    
    schedule_data = []
    if selected_class:
        data = Schedule.objects.filter(class_id = selected_class).values_list()
        if data:
            try:
                schedule_data = [row[-1] for row in list(data)]
                schedule_data = [schedule_data[i:i+8] for i in range(0, len(schedule_data), 8)]
                return JsonResponse({'success': True, 'schedule':schedule_data})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'There is an exception {e}'})
        elif Schedule.objects.all().values_list():
            return JsonResponse({'success': False, 'message': f'There is no data for the selected class!'})

    user = User.objects.get(username=request.user)
    return render(request, 'testapp/schedule.html', {'UserName': user.get_full_name(), 'UserMail': user.email})


@login_required(login_url='testapp:home')
def classroom(request):
    assign_class = request.GET.get('assign_class')
    assign_camera = request.GET.get('assign_camera')
    
    if assign_class:
        try:
            cls = request.GET.get('class')
            room = request.GET.get('room')
            
            classroom, created = Classroom.objects.get_or_create(
                room = room, defaults={'class_id': Class.objects.get(id=cls)})
            if not created:
                classroom.class_id = Class.objects.get(id=cls)
                classroom.save()
        
            return JsonResponse({'success': True, 'message': 'Classroom assigned successfully.',})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})
    
    if assign_camera:
        try:
            cam_ip = request.GET.get('cam_ip')
            cls = request.GET.get('class')

            camera, created = Camera.objects.get_or_create(
                camera_ip = cam_ip, defaults={'class_id': Class.objects.get(id=cls)})
            if not created:
                camera.class_id = Class.objects.get(id=cls)
                camera.save()
        
            return JsonResponse({'success': True, 'message': 'Camera assigned successfully.',})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})

    data = []
    for obj in Camera.objects.all().values_list():
        room_no = Classroom.objects.filter(class_id=Class.objects.get(id=obj[1])).values_list()
        if room_no:
            data += [{
                'class': Class.objects.get(id=obj[1]),
                'room': room_no[0][0],
                'camera': obj[0]
            }]

    user = User.objects.get(username=request.user)
    return render(request, 'testapp/camera.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'data':data})


# some extra helper functions
def clean_schedule(df):
    db_entry = []
    for i in df.index:    #each day
        for j in df.loc[i].index:    #each period

            if j != '1-2':    #not a lunch time
                if ('\n' in df.loc[i,j]) or ('/' in df.loc[i,j]):    #for multiple items
                    row = [i, j.split('-')[0], j.split('-')[1]]
                
                    if '\n' in df.loc[i,j]:    #1st hour of two subjects
                        row.append(df.loc[i,j].replace('\n',','))
                    
                    if '/' in df.loc[i,j]:    #1st hour of NCC/NSS/Scout
                        row.append(df.loc[i,j].replace('/',' or '))
                    
                    db_entry.append(row)
                    
                    #for the subjects having 2hrs assigned
                    start = j.split('-')[1]
                    if int(start) < 5 or int(start) > 9:
                        end = int(start) + 1
                        if end > 12:
                            end %= 12
                        
                        #to avoid the overriding the subject presents in the next period
                        next_period = '-'.join([start, str(end)])
                        if df.loc[i,next_period] == '-':
                            if '\n' in df.loc[i,j]:    #2nd hour of two subjects
                                df.loc[i,next_period] = df.loc[i,j].replace('\n',',')
                            if '/' in df.loc[i,j]:    #2nd hour of NCC/NSS/Scout
                                df.loc[i,next_period] = df.loc[i,j].replace('/',' or ')

                else:    #single subject or no subject
                    db_entry.append([
                            i,
                            j.split('-')[0],
                            j.split('-')[1],
                            df.loc[i,j],
                        ])
                    
            else:    #lunch time
                db_entry.append([
                    i,
                    j.split('-')[0],
                    j.split('-')[1],
                    'LUNCH',
                ])
    return db_entry


def save_subjects(data):
    res_dict = {}
    try:
        # to process the text
        for row in data.iterrows():
            sub_col = row[1].values[0]
            if ',' in sub_col:    #for multiple subjects
                subj = sub_col.split(',')
                for sub in subj:
                    res = [i.strip(')') for i in sub.split('(')]
                    res_dict[res[1]] = [res[0], Teacher.objects.get(id=row[0])]
            else:    #for single subject
                res = [i.strip(')') for i in sub_col.split('(')]
                res_dict[res[1]] = [res[0], Teacher.objects.get(id=row[0])]
        
        # to save the processed values
        for key, value in res_dict.items():
            subject, created = Subject.objects.get_or_create(
                id = key,
                defaults={
                    'name': value[0].strip(),
                    'teacher_id': value[1]
                }
            )
            if not created:
                subject.name = value[0].strip()
                subject.teacher_id = value[1]
                subject.save()

    except Exception as e:
        return f'There is an exception {e}'
    return "Successfully saved the subjects!"