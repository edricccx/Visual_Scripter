from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sum/', views.sum, name='sum'),
    path('prev/', views.prev, name='prev'),
    path('youtube_transcripter/', views.youtube_transcripter, name='youtube_transcripter'),
    path('save-video/', views.upload_video, name='upload-video'),
    path('play-video/', views.play_video, name='play-video'),
    path('sum/execute_script', views.execute_script, name='execute_script'),
    path('execute_script', views.execute_script, name='execute_script'), 
    path('generate_preview', generate_preview, name='generate_preview'),
    path('translate/', translate, name='translate'),
    path('generate_srt/', views.generate_srt, name='generate_srt'),
]
