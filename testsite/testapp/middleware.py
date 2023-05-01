from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            print(f">>>>>>>>>>>>>>>>>>>>>>Last activity: {last_activity}<<<<<<<<<<<<<<<<<<<<<")
            if last_activity:
                idle_time = datetime.now() - datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S.%f")
                print(f">>>>>>>>>>>>>>>>>>>>>>Idle Time: {idle_time}<<<<<<<<<<<<<<<<<<<<<")
                if idle_time > timedelta(minutes=5):    #for college it's hour=10
                    logout(request)
                    
            request.session['last_activity'] = str(datetime.now())
            
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        return response
