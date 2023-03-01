#This is where we have functions that handle requests and return responses

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import System_Admin, Student


def home(request):
    return render(request, 'testapp/home.html')


def user_register(request):
    if request.method == 'POST':
        # clg = request.POST.get('clg_name','')
        dept = request.POST.get('dept','')
        name = request.POST.get('username','')
        email = request.POST.get('email','')
        password = request.POST.get('password','')
        confirm_password = request.POST.get('confirm_password', '')

        if not User.objects.filter(email=email).exists():
            if password and confirm_password:
                if password != confirm_password:
                    return render(request, 'testapp/register.html', {'error_msg':'The two password fields must match.'})

                names = name.split()
                username = names[0]+'@'+dept[:3]
                username = username.lower()
                User.objects.create_user(username, email, password)

                # database entry - Admin model
                admin = System_Admin(dept, name, email, password)
                admin.save()
                messages.success(request, f'You have registered successfully! Your username is {username}')
                return redirect('testapp:login')
        else:
            return render(request, 'testapp/register.html', {'error_msg':'Looks like a user with that email or password already exists'})

    else:
        return render(request, 'testapp/register.html', {'error_msg':''})


@never_cache
def user_login(request, reason=''):
    if request.method=='POST':
        if reason!='':
            messages.warning(request, reason)
            return redirect('testapp:login')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if request.GET.get('next',None):
                    return redirect(request.GET['next'])
                else:
                    return redirect('testapp:dashboard')
            else:
                messages.warning(request, "Looks like you've entered the wrong credentials!")
                return redirect('testapp:login')

        else:
            messages.warning(request, 'Looks like you are not registered!')
            return redirect('testapp:register')
    else:
        return render(request, 'testapp/login.html')


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('testapp:login')


s_submit, s_edit = False, False
t_submit, t_edit = False, False
c_submit, c_edit = False, False
p_submit, p_edit = False, False

@login_required(login_url='testapp:login')
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
            return render(request, 'testapp/admin.html',
                          {'user': admin_user,'s_submit':s_submit,'table':table[0]})

        else:
            messages.warning(request, f"{enroll} is already registered!")
            return render(request, 'testapp/admin.html', context)

    return render(request, 'testapp/admin.html', {'user': admin_user})










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