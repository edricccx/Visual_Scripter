from django.urls import path
from . import views
from .views import convert_to_mp3
from .views import execute_script
from visualapp.views import index, execute_script
from . import views
from visualapp.views import translate
from visualapp.views import generate_preview
# from .youtube import extract_transcript_details,generate_summary



urlpatterns = [
    # path('upload_video/', upload_video, name='upload_video'),
    path('', views.index, name='index'),
    path('sum/', views.sum),
    path('prev/', views.prev),
    # path('convert-to-mp3/', convert_to_mp3, name='convert_to_mp3'),
    path('save-video/', views.upload_video, name='upload-video'),
    path('play-video/', views.play_video, name='play-video'),
    path('sum/execute_script', views.execute_script, name='execute_script'),
    path('execute_script', views.execute_script, name='execute_script'), 
    path('generate_preview/', generate_preview, name='generate_preview'),
    path('translate/', translate, name='translate'),
    path('generate_srt/', views.generate_srt, name='generate_srt'),
    path('youtube_transcripter/', views.youtube_transcripter, name='youtube_transcripter'),
]