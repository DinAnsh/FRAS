from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.apps import apps
from .models import *
import os.path
import json
import os

sub_map = {}

def clean_schedule(df):
    '''
    This function takes the processed excel sheet of the uplaoded schedule as a pandas dataframe
    and extract subjects for each period for 6 days of week. So, there are 8 periods having one/two/no 
    subjects for 6 days a week. At the last, it returns a list of lists of length 48 and each child list 
    have 4 values: day_of_week, start_time, end_time, and subject.
    '''
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


def mark_attendance(data):
    '''
    This function is one of the main part of the FRAS as it is used to track attendance
    of the students and subjects on daily basis. It takes a dictionary as a parameter which
    consists of classes as keys and enrollments of the present students for the corresponding class.
    '''

    current_sub = get_subjects()
    print("XXXXXXXXXXXXXXXX",current_sub)
    for cls, enrolls in data.items():
        cls_model = apps.get_model('testapp', cls.lower().replace(" ", '_'))
        if len(enrolls) != 0:
            print("---------------------------",sub_map)
            try:
                for k,v in sub_map[cls].items():
                    if v in current_sub[cls]:
                        # enrolls = list(enrolls)
                        cls_model.objects.filter(enroll_id__enroll__in=enrolls).update(**{k: models.F(k) + 1})
                        # to keep the track of the subjects
                        Sub_Tracker.objects.filter(class_id=Class.objects.get(name=cls)).update(**{k: models.F(k) + 1})
                
                print('...............attendance marked successfully..................')
            except Exception as e:
                print(f'There is an exception -- {e}')
    print(sub_map)
    print(current_sub)


def get_subjects():
    '''
    It is used to get the class-wise subjects for the currently ongoing
    period of time. It uses current hour and the present day of the week
    to get the relevant subject from the Schedule database.
    '''

    now = datetime.now()   #YYYY-MM-DD HH:MM:SS.ssssss
    hour = now.hour % 12      #12 hour format
    weekday_name = now.strftime("%A")   #output will be a string that represents the current day of the week,
    
    curr_subj = {}
    for obj in Schedule.objects.filter(class_id_id = 2):
        if hour == obj.start_time.hour and weekday_name == obj.day_of_week:
            curr_subj['Second Year'] = obj.subject
    
    for obj in Schedule.objects.filter(class_id_id = 3):
        if hour == obj.start_time.hour and weekday_name == obj.day_of_week:
            curr_subj['Third Year'] = obj.subject

    for obj in Schedule.objects.filter(class_id_id = 4):
        if hour == obj.start_time.hour and weekday_name == obj.day_of_week:
            curr_subj['Final Year'] = obj.subject

    return curr_subj


def check_subMap():
    '''
    This is the backbone for the tracking of subject-wise records in the database.
    It maintains the mapping between database fields/columns and the subject IDs.
    This function uses a file named 'submap.json' to keep the mapping consistent.
    '''

    # Returns True if the QuerySet contains any results, and False if not.
    if Subject.objects.exists():
        try:
            # select only those classes for which subjects are already uploaded
            cls_inDB = list(Class.objects.filter(id__in=Subject.objects.values_list('class_id', flat=True)).values_list('name', flat=True))
            for cls in cls_inDB:
                if cls != 'None':
                    
                    # for updating the map according to the current subjects
                    cls_model = apps.get_model('testapp', cls.lower().replace(" ", '_'))
                    subjects = Subject.objects.filter(class_id = Class.objects.get(name=cls)).values_list('id', flat=True)
                    fields = [f.name for f in cls_model._meta.get_fields()[2:]]
                    
                    # to update the sub_map with the existing map
                    global sub_map
                    if os.path.exists('submap.json'):
                        with open('submap.json', 'r') as json_file:
                            sub_map = json.load(json_file)
                    else:
                        with open('submap.json', 'w') as json_file:
                            json.dump(sub_map, json_file)

                    if cls in sub_map.keys():
                        # for adding new subjects in map
                        new_sub = [sub for sub in subjects if sub not in sub_map[cls].values()]
                        new_key = [key for key in fields if key not in sub_map[cls].keys()]
                        for sub,key in zip(new_sub, new_key):
                            sub_map[cls][key] = sub

                        # for deleting subjects in map
                        del_sub = [sub for sub in sub_map[cls].values() if sub not in subjects]
                        del_key = []
                        for sub in del_sub:
                            del_key += [key for key, value in sub_map[cls].items() if value == sub]
                        for key in del_key:
                            del sub_map[cls][key]            
                        
                    else:
                        sub_map[cls] = {f:s for f,s in zip(fields, subjects)}
                        

                    with open('submap.json', 'r+') as json_file:
                        json_file.truncate()
                        json.dump(sub_map, json_file)

            print('...........sub_map updated successfully!.........')
            return sub_map
        except Exception as e:
            print(f'There is an exception {e}')
    else:
        print("-------------------------------Subject table is Empty!----------------------------------------")
        return None


def check_subjects():
    '''
    This function checks the Schedule and Teacher database to save the subjects with relevant
    teacher ID and class ID. It is used to populate or modify Subject database model with all
    the subjects by doing some text-processing on the 'subjects' column of Teacher model.
    '''

    if Schedule.objects.exists() and Teacher.objects.exists():      # for subject model
        data = Teacher.objects.all().values_list('id','subjects')
        
        try:
            res_dict = {}
            for val in data:        # to process the text
                if ',' in val[1]:   # for multiple subjects
                    subj = val[1].split(',')
                    
                    for sub in subj:
                        res = [i.strip(')') for i in sub.split('(')]
                        res_dict[res[1]] = [res[0], Teacher.objects.get(id=val[0])]
                
                else:    #for single subject
                    res = [i.strip(')') for i in val[1].split('(')]
                    res_dict[res[1]] = [res[0], Teacher.objects.get(id=val[0])]
            
            for key, value in res_dict.items():     # to save the processed values
                subject, created = Subject.objects.get_or_create(
                    id = key,
                    defaults={
                        'name': value[0].strip(),
                        'teacher_id': value[1],
                        'class_id': Class.objects.get(name=Schedule.objects.filter(subject__icontains=key)[0]) if Schedule.objects.filter(subject__icontains=key) else Class.objects.get(id='0')
                    }
                )
                if not created:
                    subject.name = value[0].strip()
                    subject.teacher_id = value[1]
                    subject.class_id = Class.objects.get(name=Schedule.objects.filter(subject__icontains=key)[0]) if Schedule.objects.filter(subject__icontains=key) else Class.objects.get(id='0')
                    subject.save()
            
            print("..........Successfully saved the subjects!............")
        
        except Exception as e:
            print(f'There is an exception - {e}')


def reset_models():
    '''
    This function is used to clear the database records of
    all of the class models, schedule model, subject tracker model,
    and the mapping that is saved in the submap.json file.
    '''

    a = Second_Year.objects.all().delete()
    b = Third_Year.objects.all().delete()
    c = Final_Year.objects.all().delete()
    d = Schedule.objects.all().delete()

    for i in ['2','3','4']:
        cls_obj = Sub_Tracker.objects.get(class_id_id=i)
        for field in cls_obj._meta.fields[2:]:
            field_name = field.name
            field_default = field.get_default()
            setattr(cls_obj, field_name, field_default)

        cls_obj.save()

    print("Database models are cleared: ",a[1],b[1],c[1],d[1])

    file_path = 'submap.json'
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Map deleted successfully.")
    else:
        print("Map does not exist.")


def send_forget_password_mail(email, meta):
    subject = "Reset your FRAS password!"
    message = f'''
Hello, We received a request to reset the password for your account for this email address. To initiate the password reset process for your account, click the link below. 
{meta["scheme"]}://{meta["host"]}/change_password/{meta["token"]}/
Note: the link will be validated only for 2 minutes.

This link can only be used once. If you need to reset your password again, please visit {meta["scheme"]}://{meta["host"]}/ and request another reset.
If you did not make this request, you can simply ignore this email.

Sincerely,
The FRAS Team
    '''
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True