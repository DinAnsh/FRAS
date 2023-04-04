#This is where we have functions that handle requests and return responses

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import System_Admin, Student, Team
from django.http import JsonResponse
import json
import base64
from django.core.files.base import ContentFile
from PIL import Image

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


<<<<<<< HEAD
# s_submit, s_edit = False, False
# t_submit, t_edit = False, False
# c_submit, c_edit = False, False
# p_submit, p_edit = False, False
=======
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3

# s_submit, s_edit = False, False
# t_submit, t_edit = False, False
# c_submit, c_edit = False, False
# p_submit, p_edit = False, False

#if we can provide other data from here to the page then we can show a message to the user 'Login first'
@login_required(login_url='testapp:home')      
def dashboard(request, reason=''):
    # global s_submit,p_submit,t_submit,c_submit
    # context = {'s_submit': s_submit, 't_submit': t_submit,
    #            'c_submit': c_submit, 'p_submit': p_submit,}

    #Check in session if logged in 
    
    # try:
    user = User.objects.get(username=request.user)
    # admin_user = System_Admin.objects.get(email=user.email)
    # except:
    #     return HttpResponse(json.dumps({"message":"Need to login again!"}), status=401)

    # user = User.objects.get(username=request.user)
    # admin_user = System_Admin.objects.get(email=user.email)

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
    # else:
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


<<<<<<< HEAD
@login_required(login_url='testapp:login')
=======
@login_required(login_url='testapp:home')
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3
def student(request):
    user = User.objects.get(username=request.user)
    students = Student.objects.all()
    students_list = []
    
<<<<<<< HEAD
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
=======
# @login_required(login_url='testapp:home')
def upload_image(request):
    if request.method == 'POST':
        # Get the image data from the request
        json_data = json.loads(request.body)
        image_data = json_data.get('image_data')
        # enroll_id = json_data.get('enroll')
        
        # Decode the base64-encoded image data
        decoded_image_data = base64.b64decode(image_data.split(',')[1])
        
        imgName = enroll_id+".png"
        
        # Create a ContentFile from the decoded image data
        image_file = ContentFile(decoded_image_data, name='student.png')
        
        # Save the image to a file or database
        # student = Student.objects.filter(enroll=enroll)
        student = Student(name="Dipendra",enroll="2019/ctae/140",img=image_file)
        student.save()
        
        return JsonResponse({'status': 'success'}, status=200)    
    else:
        return JsonResponse({'status': 'fail'})


@login_required(login_url='testapp:home')
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3
def teacher(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/teacher.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    
<<<<<<< HEAD

@login_required(login_url='testapp:login')
=======
@login_required(login_url='testapp:home')
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3
def schedule(request):
    user = User.objects.get(username=request.user)
    return render(request, 'testapp/schedule.html', {'UserName': user.get_full_name(), 'UserMail': user.email})
    
<<<<<<< HEAD

@login_required(login_url='testapp:login')
=======
@login_required(login_url='testapp:home')
>>>>>>> 7d6dfd007dd500511fd13f0652dc12b7f4d7b5a3
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