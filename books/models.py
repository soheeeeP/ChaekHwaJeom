from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import MyUser

# custom manager
class BookManager(models.Manager):
    use_for_related_fields = True

class Book(models.Model):
    objects = BookManager()

    STATUS_CHOICES = (
        ('대여 가능','대여 가능'),
        ('예약 중','예약 중'),
        ('대여 중','대여 중'),
        ('대여 불가능','대여 불가능'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="bookuser",on_delete=models.CASCADE,blank=False)
    ISBN = models.CharField(max_length=13,blank=False,verbose_name='ISBN')
    title = models.CharField(max_length=50,verbose_name='도서명')
    author = models.CharField(max_length=30, blank=True,verbose_name="저자")
    publisher = models.CharField(max_length=30,blank=True,verbose_name='출판사')
    status = models.CharField(choices=STATUS_CHOICES,default='대여 가능',max_length=10,verbose_name='상태')
    bookcover = models.URLField(max_length=400,blank=True,verbose_name='표지')
    stored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book'
        verbose_name = '도서'
        verbose_name_plural = verbose_name
        ordering = ['-stored_at']

    def __str__(self):
        return f'[{self.user.email}]님의 도서: {self.title}'

    def validate_new_book(isbn,user):
        # 중복 도서 확인
        if Book.objects.filter(ISBN=isbn).exists():
            unique_check = Book.objects.filter(Q(ISBN=isbn) & Q(user=user))
            if unique_check.exists():
                return False, f'{user.nickname}\'ve already registered book [{isbn}]'
        return True

    def save(self,*args,**kwargs):
        return super(Book,self).save(*args,**kwargs)

class Review(models.Model):
    book = models.OneToOneField(Book,on_delete=models.CASCADE,primary_key=True)
    book_review=models.TextField(max_length=100,blank=True,verbose_name='리뷰')
    rate=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],default=1,verbose_name='별점')
    likes_user = models.ManyToManyField(settings.AUTH_USER_MODEL,blank=True,related_name='likes_user',verbose_name='좋아요')
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'book_review'
        verbose_name = '도서 리뷰'
        verbose_name_plural = verbose_name
        ordering = ['-created_date']

    def count_likes_user(self):
        return self.likes_user.count()

    def __str__(self):
        return f'[{self.book.ISBN}] - {self.book_review[:10]}...'
    

class Comment(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    review_comment = models.TextField(default='')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'[{self.review_comment[:10]}...]'
    class Meta:
        db_table = 'neighbor_review'
        verbose_name = '이웃의 리뷰'
        verbose_name_plural = verbose_name
        ordering = ['-created_date']
