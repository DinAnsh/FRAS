#This is where we have functions that handle requests and return responses

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import System_Admin, Student, Team


def home(request):
    student_data = Student.objects.all()
    team_data = Team.objects.all()
    for i in team_data:
        print(i.image)
    return render(request, 'testapp/home.html',{"sdata":student_data,'tdata':team_data})


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
                # below code will be done by js
                # if password != confirm_password:
                #     return render(request, 'testapp/home.html', {'error_msg':'The two password fields must match.'})

                names = name.split()
                username = names[0]+'@'+dept[:3]
                username = username.lower()
                User.objects.create_user(username, email, password, first_name=names[0], last_name=" ".join(names[1:]) )

                # database entry - Admin model
                admin = System_Admin(dept, name, email, password)
                admin.save()
                messages.success(request, f'You have registered successfully! Your username is {username}')
                return redirect('testapp:home')
        else:
            messages.warning(request, 'Looks like a user with that email or password already exists')
            return render(request, 'testapp/home.html')

    else:
        return render(request, 'testapp/home.html')


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
        return redirect('testapp:home')


# s_submit, s_edit = False, False
# t_submit, t_edit = False, False
# c_submit, c_edit = False, False
# p_submit, p_edit = False, False

@login_required(login_url='testapp:login')
def dashboard(request, reason=''):

    # global s_submit,p_submit,t_submit,c_submit
    # context = {'s_submit': s_submit, 't_submit': t_submit,
    #            'c_submit': c_submit, 'p_submit': p_submit,}

    user = User.objects.get(username=request.user)
    # admin_user = System_Admin.objects.get(email=user.email)

    # # if request.method == 'POST':
    # enroll = request.POST.get('enroll')
    # teacher_name = request.POST.get('teacher_name')
    # room = request.POST.get('room')
    # subject =  request.POST.get('subject')

    # table = []
    # if enroll:                      #for student registration
    #     if not Student.objects.filter(enroll=enroll).exists():
    #         s_submit = True
    #         student = Student(request.POST.get('student_name'), enroll,
    #                           request.FILES.get('img'))
    #         print(request.FILES.get('img'))
    #         student.save()

    #         messages.info(request, f'{enroll} is registered successfully!')
    #         table.append([request.POST.get('student_name'), enroll])
    #         return render(request, 'testapp/dashboard.html',
    #                       {'user': admin_user,'s_submit':s_submit,'table':table[0]})

    #     else:
    #         messages.warning(request, f"{enroll} is already registered!")
    #         return render(request, 'testapp/dashboard.html', context)

    # return render(request, 'testapp/dashboard.html', {'user': admin_user})

    return render(request, 'testapp/dashboard.html', {'UserName': user.get_full_name(), 'UserMail': user.email})


@login_required(login_url='testapp:login')
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


@login_required(login_url='testapp:login')
def student(request):
    user = User.objects.get(username=request.user)
    students = Student.objects.all()
    students_list = []
    
    for student in students:
        ref = student.__dict__
        students_list.append([ref['enroll'],ref['name'],ref['email'],ref['mobile']])
       
    return render(request, 'testapp/student.html', {'UserName': user.get_full_name(), 'UserMail': user.email, 'Students':students_list})


@login_required(login_url='testapp:login')
def get_student_data(request):
    selected_class = request.GET.get('class')
    page_number = request.GET.get('page')

    current_year = timezone.now().strftime('%Y')
    # current_month = timezone.now().strftime('%m')

    adm_year = str(int(current_year)-int(selected_class))
    student_data = Student.objects.filter(enroll__startswith=adm_year).values()
    
    paginator = Paginator(list(student_data), 1)
    page = paginator.get_page(page_number)
    
    previous_page_url = page.previous_page_number() if page.has_previous() else None
    next_page_url = page.next_page_number() if page.has_next() else None
    
    page_obj = {
        'number': page.number,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'current_page': page.number,
        'total_pages': paginator.num_pages,
        'has_other_pages': page.has_other_pages(),
        'previous_page_number': previous_page_url,
        'next_page_number': next_page_url,
    }
    print(page_obj)
    
    return JsonResponse({'data':list(page), 'page_obj':page_obj}, safe=False)


@login_required(login_url='testapp:login')
def teacher(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    

@login_required(login_url='testapp:login')
def schedule(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/schedule.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    

@login_required(login_url='testapp:login')
def camera(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/camera.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    




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