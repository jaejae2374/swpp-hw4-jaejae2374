from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse

import json
from json.decoder import JSONDecodeError

from blog.models import Article, User, Comment

def check_user_auth(request):
    if not request.user.is_authenticated:
        return False
    return True

def get_article(id):
    try:   
        return Article.objects.get(id=id)
    except Article.DoesNotExist:
        return None
    
def get_comment(id):
    try:
        return Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return None
    
def is_author(instance, request):
    if instance.author != request.user:
        return False
    return True

def get_body_value(request, *args):
    results = []
    body = request.body.decode()
    for arg in args:
        results.append(json.loads(body)[arg])
    return results

class ArticleCreateListView(View):

    def get(self, request):
        if not check_user_auth(request): return HttpResponse(status=401)
        articles = Article.objects.all()
        articles = list(map(lambda x: {"id": x.id, "title": x.title, "content": x.content, "author": x.author.id}, articles))
        return JsonResponse(articles, status=200, safe=False)

    def post(self, request):
        if not check_user_auth(request): return HttpResponse(status=401)
        author = request.user
        try:
            title, content = get_body_value(request, 'title', 'content')
        except (KeyError, JSONDecodeError):
            return HttpResponseBadRequest()
        article = Article.objects.create(title=title, content=content, author=author)
        return JsonResponse({
            "id": article.id, 
            "title": article.title, 
            "content": article.content, 
            "author": article.author.id}, status=201)

    
class ArticleRetUptDelView(View):
        
    def get(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        article = get_article(id)
        if not article:
            return HttpResponse(status=404)
        return JsonResponse({
            "title": article.title, 
            "content": article.content, 
            "author": article.author.id}, status=200)

    def put(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        article = get_article(id)
        if not article:
            return HttpResponse(status=404)
        if not is_author(article, request):
            return HttpResponse(status=403)
        try:
            title, content = get_body_value(request, 'title', 'content')
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        article.title = title
        article.content = content
        article.save()
        return JsonResponse({
            "id": article.id, 
            "title": article.title, 
            "content": article.content, 
            "author": article.author.id}, status=200)
        
    def delete(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        article = get_article(id)
        if not article:
            return HttpResponse(status=404)
        if not is_author(article, request):
            return HttpResponse(status=403)
        article.delete()
        return HttpResponse(status=200)


class CommentCreateListView(View):

    def get(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        article = get_article(id)
        if not article:
            return HttpResponse(status=404)
        comments = Comment.objects.filter(article=id)
        comments = list(map(lambda x: {"id": x.id, "article": x.article.id, "content": x.content, "author": x.author.id}, comments))
        return JsonResponse(comments, status=200, safe=False)

    def post(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        article = get_article(id)
        if not article:
            return HttpResponse(status=404)
        author = request.user
        try:
            content = get_body_value(request, 'content')[0]
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        comment = Comment.objects.create(content=content, article=article, author=author)
        return JsonResponse({
            "id": comment.id, 
            "article": comment.article.id, 
            "content": comment.content, 
            "author": comment.author.id}, status=201)

    
class CommentRetUptDelView(View):

    def get(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        comment = get_comment(id)
        if not comment:
            return HttpResponse(status=404)
        return JsonResponse({
            "content": comment.content,
            "article": comment.article.id,
            "author": comment.author.id}, status=200)

    def put(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        comment = get_comment(id)
        if not comment:
            return HttpResponse(status=404)
        if not is_author(comment, request):
            return HttpResponse(status=403)
        try:
            content = get_body_value(request, 'content')[0]
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        comment.content = content
        comment.save()
        return JsonResponse({
            "id": comment.id, 
            "content": comment.content, 
            "article": comment.article.id,
            "author": comment.author.id}, status=200)

    def delete(self, request, id):
        if not check_user_auth(request): return HttpResponse(status=401)
        comment = get_comment(id)
        if not comment:
            return HttpResponse(status=404)
        if not is_author(comment, request):
            return HttpResponse(status=403)
        comment.delete()
        return HttpResponse(status=200)
    

def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['POST'])

def signin(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        user = authenticate(request, username=username, password=password)
        if user: 
            login(request, user)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['POST'])

def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
