from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
import uuid
from django.shortcuts import render, redirect

# Chaekhwajeom custom MyUser model manager
class MyUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

    # 일반 유저 생성
    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_admin', False)
        return self._create_user(email, password, **kwargs)

    # 관리자 유저 생성
    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_admin', True)
        return self._create_user(email, password, **kwargs)

    # 소셜 회원가입 유저 생성
    def get_or_create_google_user(self,user_pk):
        user = MyUser.objects.get(pk=user_pk)
        user.save()
        return user

class MyUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = verbose_name
        get_latest_by = 'date_joined'

    uuid = models.UUIDField(
        primary_key=True, 
        unique=True,
        editable=False, 
        default=uuid.uuid4, 
        verbose_name='PK'
    )

    email = models.EmailField(unique=True, verbose_name='이메일')
    username = models.CharField(max_length=20, verbose_name='이름')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='가입일')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    is_admin = models.BooleanField(default=False, verbose_name='관리자 여부')

    sido = models.CharField(max_length=10, verbose_name='시도')
    sigungu = models.CharField(max_length=50, verbose_name='시군구')
    dong = models.CharField(max_length=50, verbose_name='동') # 동읍면리
    profileimage = models.ImageField(blank=True, verbose_name='프로필이미지')
    nickname = models.CharField(max_length=200, verbose_name='닉네임')
    
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
