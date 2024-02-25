from django.urls import path
from . import views
from .views import convert_to_mp3
from .views import execute_script
from visualapp.views import index, execute_script
from .views import upload_video  


urlpatterns = [
    path('upload_video/', upload_video, name='upload_video'),
    path('', views.index, name='index'),
    path('convert-to-mp3/', convert_to_mp3, name='convert_to_mp3'),
    path('execute/', execute_script, name='execute'),
    path('execute/', execute_script, name='execute_script'),
    path('execute/', execute_script, name='script_output'),

]