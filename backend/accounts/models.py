from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=20, default='', blank=True)
    phone_number = models.CharField(max_length=15, default='', blank=True)
    birth_date = models.DateField(null=True, blank=True)
    # 사진과 소개글 저장 칸 만들기
    profile_img = models.ImageField(upload_to='profile_imgs/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    
    age = models.IntegerField(default=0)
    money = models.IntegerField(default=0)
    salary = models.IntegerField(default=0)
    investment_persona = models.CharField(max_length=20, blank=True, null=True)

# SavedVideo는 반드시 User 모델 아래에 적어줘!
class SavedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_videos')
    video_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    thumbnail = models.URLField()
    channel_title = models.CharField(max_length=100)
    published_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video_id')