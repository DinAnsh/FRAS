#This is where we have functions that handle requests and return responses

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import System_Admin, Student, Team
import json

def home(request):
    student_data = Student.objects.all()
    team_data = Team.objects.all()
    return render(request, 'testapp/home.html',{"sdata":student_data,'tdata':team_data, "logged":0})


def user_register(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        # clg = request.POST.get('clg_name','')
        dept = "cse"            #request.POST.get('dept','')
        name = json_data.get('username','')
        email = json_data.get('email','')
        password = json_data.get('password','')
        # confirm_password = request.POST.get('confirm_password', '')   #we can remove this line becs we don't need confirm password
        if not User.objects.filter(email=email).exists():
            names = name.split()
            username = names[0].lower()+'@'+'com'
            
            User.objects.create_user(username, email, password, first_name=names[0],last_name=" ".join(names[1:]) )

            # database entry - Admin model
            admin = System_Admin(dept, name, email, password)
            admin.save()
            return HttpResponse(json.dumps({"message":"You are successfully registered."}), status=200)
        
        else:
            return HttpResponse(json.dumps({'message':'Looks like a user with that email already exists'}),status=409)


@never_cache
def user_login(request, reason=''):
    if request.method=='POST':
        if reason!='':
            messages.warning(request, reason)
            return redirect('testapp:home')
        
        json_data = json.loads(request.body)
        username = json_data.get('uname', '')
        password = json_data.get('password', '')

        
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if request.GET.get('next',None):
                    return redirect(request.GET['next'])
                else:
                    return HttpResponse(json.dumps({"message":"Successfully logged in"}),status=200)
            else:
                # messages.warning(request, "Looks like you've entered the wrong password!")
                return HttpResponse(json.dumps({"message":"Looks like you've entered the wrong password"}), status=401)

        else:
            # messages.warning(request, 'Looks like you are not registered!')
            return HttpResponse(json.dumps({"message":"Looks like you are not registered!"}), status=404)
    else:
        return render(request, 'testapp/home.html')


@login_required(login_url='testapp:home')
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        student_data = Student.objects.all()
        team_data = Team.objects.all()
        return render(request, 'testapp/home.html',{"sdata":student_data,'tdata':team_data})



s_submit, s_edit = False, False
t_submit, t_edit = False, False
c_submit, c_edit = False, False
p_submit, p_edit = False, False

#if we can provide other data from here to the page then we can show a message to the user 'Login first'
@login_required(login_url='testapp:home')      
def dashboard(request, reason=''):
    global s_submit,p_submit,t_submit,c_submit
    context = {'s_submit': s_submit, 't_submit': t_submit,
               'c_submit': c_submit, 'p_submit': p_submit,}

    user = User.objects.get(username=request.user)
    admin_user = System_Admin.objects.get(email=user.email)

    # if request.method == 'POST':
    enroll = request.POST.get('enroll')
    teacher_name = request.POST.get('teacher_name')
    room = request.POST.get('room')
    subject =  request.POST.get('subject')

    table = []
    if enroll:                      #for student registration
        if not Student.objects.filter(enroll=enroll).exists():
            s_submit = True
            student = Student(request.POST.get('student_name'), enroll,
                              request.FILES.get('img'))
            print(request.FILES.get('img'))
            student.save()

            messages.info(request, f'{enroll} is registered successfully!')
            table.append([request.POST.get('student_name'), enroll])
            return render(request, 'testapp/dashboard.html',
                          {'user': admin_user,'s_submit':s_submit,'table':table[0]})

        else:
            messages.warning(request, f"{enroll} is already registered!")
            return render(request, 'testapp/dashboard.html', context)

    return render(request, 'testapp/dashboard.html', {'user': admin_user})

@login_required(login_url='testapp:login')
def student(request):
    return render(request, 'testapp/student.html')
    
@login_required(login_url='testapp:login')
def teacher(request):
    return render(request, 'testapp/teacher.html')
    
@login_required(login_url='testapp:login')
def schedule(request):
    return render(request, 'testapp/schedule.html')
    
@login_required(login_url='testapp:login')
def camera(request):
    return render(request, 'testapp/camera.html')
    


# future
# 's_edit': s_edit, 't_edit': t_edit, 'c_edit': c_edit, 'p_edit': p_edit

# def edit_student(request, table):
#     global s_edit, s_submit
#     s_edit = True
#     s_submit = False
#     table = table.replace("'", "")
#     table = table.replace("[", "")
#     table = table.replace("]", "")
#     table = table.replace(",", "")
#     table = table.split()
#     print(request)
#     return render(request, 'testapp/admin.html', {'s_edit':s_edit, 's_submit':s_submit, 'table':table})


# def remove_student(request):
#     print(request.POST.get('edit_name'))
#     Student.objects.filter(enroll=enroll).delete()
#     messages.info(request, f'{enroll} is deleted successfully!')
#     return redirect('testapp:dashboard')