from django.db import models

class Video(models.Model):
    video_file = models.FileField(upload_to='videos/')
    audio_file = models.FileField(upload_to='audios/', blank=True)