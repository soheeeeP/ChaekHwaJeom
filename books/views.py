from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Book, Review
from accounts.models import MyUser
from chat.models import Message
from .forms import BookForm, ReviewForm, CommentForm

import json,re
from utils.naver_api import search_book_info, register_new_book

def home(request):
    cur_user = request.user
    if request.method == "GET":
        q = request.GET.get('main')
        if q:
            books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(publisher__icontains=q))
            for book in books:
                title=book.title.split('(')
                book.title = title[0]
            return render(request,'books/main_search.html',{'books':books})

    if cur_user.is_authenticated:
        return render(request,'books/base.html',{'user':cur_user}) 
    else:
        return render(request,'books/base.html') 

def query_book(request):
    if request.method == "GET":
        q = request.GET.get('main')
        if q:
            books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(publisher__icontains=q))
            # print(books)
            return render(request,'books/main_search.html',{'books':books})

@login_required()
def edit(request, pk):
    post = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now
            post.save()
            return redirect('detail', pk=post.pk)
    else:
        form = BookForm(instance=post)
    return render(request, 'books/edit.html', {'form': form})

@login_required()
def delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user == book.user:
        if book.status == 2:
            messages.error('현재 대여 중인 도서입니다.')
        else:
            book.delete_book()
            messages.info(request,'도서가 삭제되었습니다.')
    else:
        messages.error(request,'잘못된 접근입니다.')
    return redirect('user_library')


@login_required()
def user_library(request):
    user = request.user
    books = Book.objects.filter(user=user)
    for book in books:
        review = get_object_or_404(Review, pk=book)

        title = book.title.split('(')
        book.title = title[0]
        book.review = review
        book.review_rate = range(review.rate)

        return render(request, 'books/user_library.html', {'user': user, 'books': books})
    
    # kwargs값으로 nickname 붙여서 넘기기
    return HttpResponseRedirect(reverse('user_library'))

def book_search(request):
    if request.method == "GET":
        # option = request.GET.get('option')
        q = request.GET.get('query')
        
        if q is None or q == '':
            return render(request,'books/book_search.html')

        # 도서 검색 수행
        search_result = search_book_info(q)
        index = 0
        
        for book in search_result:
            book['title'] = book['title'].split('(')[0]
            # book['option'] = option
            book['index'] = index
            index += 1

        paginator = Paginator(search_result,5)
        page = request.GET.get('page')
        books = paginator.get_page(page)

        book_form = BookForm()
        review_form = ReviewForm()

        return render(request,'books/book_search.html',{'books':books,'book_form':book_form, 'review_form': review_form})

    return redirect('book_search')

@login_required()
@require_POST
def book_register(request):
    user = request.user
    if request.method == "POST":
        isbn = request.POST.get('isbnvalue')        # 도서 ISBN value
        status = request.POST.get('status')         # 도서 대여 상태
        review = request.POST.get('book_review')    # 도서 리뷰
        star_rate = request.POST.get('review-star') # 도서 별점

        state, book = register_new_book(isbn,user)
        print(state)

        if book:
            # 사용자가 선택한 도서 대여 상태 정보를 저장
            book.status = status                        
            book.save()

            new_review = Review.objects.create(
                book = book,
                book_review = review,
                rate = star_rate,
            )
            new_review.save()

            messages.info(request,'도서와 리뷰가 등록되었습니다!')
            return redirect('book_search')

    return HttpResponseRedirect(reverse('book_search'))


def like(request):
    pk = request.POST.get('pk', None)
    posts = get_object_or_404(Review, pk=pk)
    user = request.user
    if posts.likes_user.filter(email=user.email).exists():
        posts.likes_user.remove(user)
        message = '좋아요 취소'
        messages.info(request,'좋아요를 취소하였습니다.')
    else:
        posts.likes_user.add(user)
        message.info(request,'좋아요!')
    context = {'likes_count':posts.count_likes_user(), 'message': message}
    return HttpResponse(json.dumps(context), content_type="application/json")

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)       # 등록된 도서 객체
    
    # 단순 split 말고 정규표현식으로 '()' 내의 제목 추출, book.subtitle 인자로 html에 넘길 것
    book.title = book.title.split('(')[0]   
    # print(book.get_status_display())
    print(book.status) 
    neighbor = book.user

    review = Review.objects.get(book=book)      # 도서에 대한 review 객체
    
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = review
            comment.text = comment_form.cleaned_data.get("text")
            comment.save()

            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    
    return render(request,'books/book_detail.html',{
                    'neighbor' : neighbor, 
                    'book': book, 
                    'review':review,
                    'rate':range(review.rate),
                    'rate_blank': range(5-review.rate),
                    'comment_form': comment_form
                    })
  
def service_manual(request):
    return render(request, 'books/service_manual.html')


@login_required()
def neighbor_library(request):
    cur_user = request.user
    result = []
    dong = MyUser.objects.filter(
       dong__icontains=cur_user.dong).exclude(email=cur_user.email)
    for d in dong:                              # 로그인된 사용자와 같은 동에 거주하는 user
        books = d.bookuser.all()
        books_cnt = books.count()
        if books_cnt > 0:
            info = {}
            info['user'] = d
            info['books'] = d.bookuser.all()
            info['books_cnt'] = books_cnt
            result.append(info)

    result.sort(key=lambda x: x['books_cnt'], reverse=True)
    print(result)
    if not result:
        print('noneeeee')
    
    return render(request, 'books/neighbor_library.html', {'neighbor': result})