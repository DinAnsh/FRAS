#This is where we have functions that handle requests and return responses

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime
from django.apps import apps
from PIL import Image
from .models import *
from .helper import *
from .face import *
import pandas as pd
import numpy as np
import base64
import json
import cv2


year2 = set()
year3 = set()
year4 = set()


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
            pro = Profile.objects.create(user=User.objects.get(email=email))
            pro.created_at = timezone.now()
            pro.save()
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
                    return JsonResponse({"message":"Successfully logged in", 'status':'old_user'})
                else:
                    if not Class.objects.exists():
                        instances = [
                            Class(id=0, name='None'),
                            Class(id=2, name='Second Year'),
                            Class(id=3, name='Third Year'),
                            Class(id=4, name='Final Year'),
                        ]
                        Class.objects.bulk_create(instances)

                        Sub_Tracker.objects.bulk_create([Sub_Tracker(class_id_id='2'), Sub_Tracker(class_id_id='3'), Sub_Tracker(class_id_id='4')])
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
        return redirect('testapp:home')


@never_cache
def change_password(request, token):
    context = {}
    try:
        prof_obj = Profile.objects.filter(forget_password_token = token).first()
        #here check if the token created at and current time difference the token will only valid for 10 min
        now = timezone.now()
        created_at = prof_obj.created_at    
        days_diff = (now - created_at).days

        # Calculate the remaining hours and minutes difference
        remaining_diff = (now - created_at).seconds // 60

        # Calculate the hours and minutes separately
        hours_diff = remaining_diff // 60
        minutes_diff = remaining_diff % 60
        
        if days_diff==0 and hours_diff==0 and minutes_diff>2:
            messages.warning(request,"Link expired please generate new reset password link!")
            return redirect('forgot_password')
    
        context = {
            "user_id": prof_obj.user.id
        }
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            if user_id is None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change_password/{token}/')
            
            if new_password != confirm_password:
                messages.warning(request,"password doesn't match")
                return redirect(f'/change_password/{token}/')


            user_obj = User.objects.get(id=user_id)
            email = user_obj.email
            user = System_Admin.objects.get(email=email)
            user.password = new_password
            user.save()
            user_obj.set_password(new_password)
            user_obj.save()
            
            messages.success(request,"Password Changed Successfully!")
            return redirect('home')
        
        
    except Exception as e:
        print(f"There is an exception - {e}")
        messages.warning(request,"Bad token request, regenerate the link!")
        return redirect('forgot_password')
        
    return render(request,'change_password.html', context=context)


@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('user_email')
        #first check if the email already exist or not
        try:
            if not User.objects.filter(email=email).exists():
                messages.success(request, 'User with this email does not exist.')
                return redirect('forgot_password')
            
            else:
                user = User.objects.get(email=email)
                token = get_random_string(length=32)
                
                profile_obj = Profile.objects.get(user= user)
                profile_obj.forget_password_token = token
                profile_obj.save()
                meta = {"scheme":request.scheme, "host":request.get_host(), "token":token}
                send_forget_password_mail(user.email, meta)
                messages.success(request, 'An Email is Sent.')
                return redirect('forgot_password')
                
        except Exception as e:
            print(f"There is an exception - {e}")
        
    return render(request, 'forgot_password.html')
 

#if we can provide other data from here to the page then we can show a message to the user 'Login first'
@login_required(login_url='testapp:home')      
def dashboard(request, reason=''):
    user = User.objects.get(username=request.user)
    try:
        global sub_map
        sub_map = check_subMap()

        if request.method == 'POST':
            if request.content_type == 'application/json':
                payload = json.loads(request.body)
                cameras = Camera.objects.all()

                if cameras and payload.get("get_class"):
                    try:
                        cam = Camera.objects.get(camera_ip=payload.get("cam_id")) 
                    except Camera.DoesNotExist:      
                        return JsonResponse({"class": 'Not Found!'}, status=200)
                    return JsonResponse({"class": str(cam.class_id)}, status=200)
                elif payload.get("get_class"):
                    return JsonResponse({"status":"success"},status=307)

            # handle the request to reset records
            if request.POST.get('approve') == 'Yes':
                reset_models()
                referring_url = request.META.get('HTTP_REFERER')
                return redirect(referring_url)
                
        res_cls = {'Second Year':0,'Third Year':0,'Final Year':0}    # record of total attendance of each class
        res_sub = {}    # record of total attendance of top three subject
        if sub_map is not None:
            for cls in sub_map.keys():
                fields_to_sum = list(sub_map[cls].keys())       #[sub1,sub2,sub3,.......]
                cls_model = apps.get_model('testapp', cls.lower().replace(" ", '_'))        #get year model ex- second_year model, thirst_year...
                values_list = cls_model.objects.all().values(*fields_to_sum)    # list of dicts
                res_cls[cls] = sum([sum(dic.values()) for dic in values_list])

                for sub in fields_to_sum:
                    res_sub[sub_map[cls][sub]] = list(cls_model.objects.aggregate(Sum(sub)).values())[0]
            
            try:
                res_sub = dict(sorted(res_sub.items(), key=lambda x: x[1], reverse=True)[:3])
            # print(">>>>>>>>>>>>>res_sub>>>>>>>>>>", res_sub)
            except :
                return HttpResponse("No Student Found please upload students details!") 
            
            return render(request, 'testapp/dashboard.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'maxCls': json.dumps(res_cls), 'maxSub': json.dumps(res_sub)})
        else:
            return HttpResponse("No Subject Found please upload schedules!") 
    except Exception as e:
        print(f'There is an exception --- {e}')
    

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
            # to delete the missing enrolls in the uploaded sheet
            enrolls_to_delete = [x for x in dbEnrolls if x not in dfEnrolls]
            if len(enrolls_to_delete):
                Student.objects.filter(enroll__in = enrolls_to_delete).delete()

            # to add or modify the present enrolls in the uploaded sheet
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

    global sub_map
    sub_map = check_subMap()
    user = User.objects.get(username=request.user)   
    return render(request, 'testapp/student.html', {'UserName': user.get_full_name(), 'UserMail': user.email,})


@login_required(login_url='testapp:home')
def get_student_data(request):
    selected_class = request.GET.get('class')

    current_year = timezone.now().strftime('%Y')
    current_month = timezone.now().strftime('%m')

    if int(current_month) <= 6:
        adm_year = str(int(current_year)-int(selected_class))
    else:
        adm_year = str(int(current_year)+1-int(selected_class))
    
    try:
        student_data = Student.objects.filter(enroll__startswith=adm_year).values().order_by('enroll')
        if len(student_data)>0:
            return JsonResponse({'data':list(student_data),}, safe=False)
        else:
            return JsonResponse({'message': 'Student details are not uplaoded for the selected class.'}, status=500)

    except Exception as e:
        print(f'There is an exception --- {e}')


@login_required(login_url='testapp:home')
def face_recognize(request):
    if request.method =='POST': 
        try:
            current_min = datetime.now().strftime("%M")
            global year2, year3, year4
            if int(current_min) in list(range(0,51)):  #this time will be 10, 50
                
                for img in request.FILES:
                    # image_class -> image_3
                    print("-----------------",img)
                    class_id = img.split("_")[-1]
                    
                    image_file = request.FILES[img]
                    pil_img = Image.open(image_file)
                    # pil_img.show()
                    rgb = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BGR2RGB)
                    
                    if class_id == "0":
                        pass                #need to decide what to do with default
                    
                    if class_id == "2":
                        class2_enrolls = makePrediction(rgb,"2")
                        if type(class2_enrolls) != str:
                            for e in class2_enrolls:
                                e = str(e)
                                if e != "Unknown":
                                    year2.add(e[:4]+"/CTAE/"+e[4:])
                                else:
                                    year2.add("Unknown")

                        
                    elif class_id == "3":
                        class3_enrolls = makePrediction(rgb,"3")
                        if type(class3_enrolls) != str:
                            for e in class3_enrolls:
                                e = str(e)
                                if e != "Unknown":
                                    year3.add(e[:4]+"/CTAE/"+e[4:])
                                else:
                                    year3.add("Unknown")

                        
                    elif class_id == "4":
                        class4_enrolls = makePrediction(rgb,"4")
                        if type(class4_enrolls) != str:
                            for e in class4_enrolls:
                                e = str(e)
                                if e != "Unknown":
                                    year4.add(e[:4]+"/CTAE/"+e[4:])
                                else:
                                    year4.add("Unknown")
                    
                return JsonResponse({"status":"Prediction recorded!"})

            else:
            # pil_img = Image.open(image_file)
            # pil_img.show()
                pred = {}
    
                pred["Second Year"] = year2
                pred["Third Year"] = year3
                pred["Final Year"] = year4
                
                year2 = []
                year3 = []
                year4 = []
                
                print("----------Predictions------->",pred)
                mark_attendance(pred)
                return JsonResponse({"status":"successfully attendance marked"})
            
        except Exception as e:
            # return JsonResponse({"status":"We think images were not sent by cameras!"})
            print(">>>>>>>>>>>>>>>>>>>>>>>>>",e)
            return JsonResponse({"status":f"Internal server error {e}"}, status=500)
            
    else:
        return JsonResponse({"status":"There is request error!"})
         

@login_required(login_url='testapp:home')
def train_model(request):
    try:
        json_data = json.loads(request.body)
        year = json_data.get("year")
        print("---------------->",year)
        X,y = get_embedding(year)
        s = train(X,y,year)
        
        return JsonResponse({"status":s}, status=200)
    
    except Exception as e:
        return JsonResponse({"status":f"Internal server error {e}"}, status=500)


@login_required(login_url='testapp:home')
def get_attendance_data(request):
    selected_class = request.GET.get('class')    

    try:
        if selected_class == '2':
            fields = ['enroll_id'] + list(sub_map['Second Year'].keys())
            header = list(sub_map['Second Year'].values())
            attd = Second_Year.objects.values_list(*fields)
            data = np.array(Sub_Tracker.objects.filter(class_id_id='2').values_list(*list(sub_map['Second Year'].keys()))[0]).astype(float)

        elif selected_class == '3':
            fields = ['enroll_id'] + list(sub_map['Third Year'].keys())
            header = list(sub_map['Third Year'].values())
            attd = Third_Year.objects.values_list(*fields)
            data = np.array(Sub_Tracker.objects.filter(class_id_id='3').values_list(*list(sub_map['Third Year'].keys()))[0]).astype(float)

        elif selected_class == '4':
            fields = ['enroll_id'] + list(sub_map['Final Year'].keys())
            header = list(sub_map['Final Year'].values())
            attd = Final_Year.objects.values_list(*fields)
            data = np.array(Sub_Tracker.objects.filter(class_id_id='4').values_list(*list(sub_map['Final Year'].keys()))[0]).astype(float)
        
        res = []
        for student in attd:
            arr_a = np.array(student[1:]).astype(float)
            result = np.divide(arr_a, data, out=np.zeros_like(arr_a), where=data!=0)
            pct = (result*100).tolist()
            res.append([student[0]] + pct)
        
        return JsonResponse({'data':res, 'header':header, 'success': True}, safe=False)
    except Exception as e:
        print(f'There is an exception -- {e}')
        return JsonResponse({'success': False, 'message': f'There are no subjects for the selected class - {selected_class}'})    


#Called when student face is registered or saved
@login_required(login_url='testapp:home')
def upload_image(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                # Get the image data from the request
                json_data = json.loads(request.body)
                image_data = json_data.get('image_data')
                enroll_id = json_data.get('enrollId')
                
                # Decode the base64-encoded image data and Create a ContentFile
                decoded_image_data = base64.b64decode(image_data.split(',')[1])
                imgName = enroll_id.replace('/', '')+".png"
                image_file = ContentFile(decoded_image_data, name=imgName)
            
            else:
                image_file = request.FILES.get('image')
                enroll_id = request.POST.get('enrollId')
            
            # year = enroll_id[0:4]
            
            pil_img = Image.open(image_file)
            # pil_img.show()
            opencvImage = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BGR2RGB)
            face_array = extract_face(opencvImage)

            #here we need to check if the extract_face returns the list having 5 faces(len(extract_face)==5)
            if (type(face_array)!= str) and (len(face_array)==5):
                # Save the image to a file or database
                student = Student.objects.get(enroll=enroll_id)
                student.img=image_file  ##This is only for Demonstration purpose
                flatten_arr = np.asarray(face_array).flatten()
                flat_str = ''
                for i in flatten_arr:
                    flat_str+=str(i) + " " 
                    
                student.encoding = flat_str
                student.save()
                return JsonResponse({'status': 'Success! Faces Stored Succesfully'}, status=200)   
            
            else:
                return JsonResponse({"status": f"Failed to detect 5 faces or {len(face_array)} faces Found!"}, status=500) 
        except Exception as e:
            return JsonResponse({"status": f"Internal server error {e}"}, status=500)
    else:
        return JsonResponse({'status': 'Fail!'}, status=405)


@login_required(login_url='testapp:home')
def teacher(request):
    if request.method=='POST' and request.FILES['teacherDetails']:
        excel_file = request.FILES['teacherDetails']

        try:
            skipR = [0,1,2]
            df = pd.read_excel(excel_file, skiprows=skipR, usecols=[0,1,3,4,5], index_col='S.N0')
            df = df.dropna(subset=['NAME'])
            df.index = df.index.astype(int)

            dbEmails = list(Teacher.objects.all().values_list('email', flat=True))
            dfEmails = df['Email'].to_list()
            
            # to delete the missing teachers in the uploaded sheet
            emails_to_delete = [x for x in dbEmails if x not in dfEmails]
            if(len(emails_to_delete)):    
                Teacher.objects.filter(email__in = emails_to_delete).delete()

            # to add or modify the present teachers in the uploaded sheet
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
            # to add or modify the present teachers in the uploaded sheet
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

            return JsonResponse({'success': True, 'message': 'Details are uploaded successfully.'}, status=201)
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception - {e}'}, status=500)

    global sub_map
    sub_map = check_subMap()
    check_subjects()

    user = User.objects.get(username=request.user)
    teacherData = list(Teacher.objects.all().values_list())
    teacherData.sort(key=lambda x: int(x[1]))
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'teachers':teacherData})
    

@login_required(login_url='testapp:home')
def schedule(request):
    selected_class = request.GET.get('class')
    if request.method=='POST' and request.FILES['timeTable']:
        excel_file = request.FILES['timeTable']

        try:
            skipR = [0,1,2,3,4]
            df = pd.read_excel(excel_file, skiprows=skipR, usecols='A:I', index_col='Day')
            df.fillna('-', inplace=True)

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
            return JsonResponse({'success': False, 'message': f'There is an exception -- {e}'})
    
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
        else:
            return JsonResponse({'success': True})

    global sub_map
    sub_map = check_subMap()
    check_subjects()
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
            room_id = request.GET.get('room_id')

            camera, created = Camera.objects.get_or_create(
                camera_ip = cam_ip,
                defaults={'class_id': Class.objects.get(id=cls),
                          'room_id':Classroom.objects.get(room=room_id)
                          })
            if not created:
                camera.class_id = Class.objects.get(id=cls)
                camera.room_id = Classroom.objects.get(room=room_id)
                camera.save()
        
            return JsonResponse({'success': True, 'message': 'Camera assigned successfully.',})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})

    if request.GET.get('class'):
        try:
            rooms = [val[0] for val in Classroom.objects.filter(class_id = Class.objects.get(id=request.GET.get('class'))).values_list(named=False)]
            print(rooms)
            return JsonResponse({'success': True, 'rooms': rooms})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'There is an exception {e}'})

    data = []
    for room in Classroom.objects.all().values_list():
        cameras = Camera.objects.filter(room_id=Classroom.objects.get(room=room[0])).values_list()
        data += [{
            'class': Class.objects.get(id=room[1]),
            'room': room[0],
            'camera': ', '.join([camera[0] for camera in cameras])
        }]

    global sub_map
    sub_map = check_subMap()
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/camera.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'data':data})

