from django.apps import apps
from django.utils import timezone
from .models import Class, Student, Subject

class Subjects_and_Students:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if Student.objects.exists():     # for class models
            
            # select only those classes for which subjects are already uploaded
            cls_inDB = list(Class.objects.filter(id__in=Subject.objects.values_list('class_id', flat=True)).values_list('name', flat=True))
            current_year = timezone.now().strftime('%Y')
            current_month = timezone.now().strftime('%m')
            
            for cls in cls_inDB:
                try:
                    if cls != 'None':
                        cls_model = apps.get_model('testapp', cls.lower().replace(" ", '_'))
                        
                        if int(current_month) <= 6:
                            stu_obj = Student.objects.filter(enroll__startswith = str(int(current_year) - int(Class.objects.get(name=cls).id)))
                        else:
                            stu_obj = Student.objects.filter(enroll__startswith = str(int(current_year) + 1 - int(Class.objects.get(name=cls).id)))

                        # populate the empty class model with relevant enrolls
                        if not cls_model.objects.exists():
                            for s in stu_obj:
                                cls_model.objects.create(enroll_id=s)
                            print('..............populating class models..............')

                        else:
                            if len(stu_obj) > len(cls_model.objects.all()):
                                for s in stu_obj:
                                    cls_model.objects.get_or_create(enroll_id=s)
                                print('..............adding new students into class models..............')


                except Exception as e:
                    print(f'There is an exception -- {e}')


        response = self.get_response(request)
        return response
