from django.views.generic import ListView
import re
import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from .models import Post, Category, Tag
from .forms import ArticlePostForm
from login.models import User
from django.utils import timezone
from django.core.paginator import Paginator


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)
    post.increase_views()
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    if request.session.get('is_login', None):
        id = request.session['user_id']
        if id == post.author.id:
            k = 'allowed'
            return render(request, "blog/single.html", context={'post': post, 'delete_allowance': k})
    k = 'not_allowed'
    return render(request, "blog/single.html", context={'post': post, 'delete_allowance': k})

# Create your views here.


def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context= {'post_list':post_list})


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list':post_list})


def tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=tag).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


def Money(request):
    return render(request, 'blog/_NeedMoney.html')


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10


def article_list(request):
    articlelist=Post.objects.all()
    paginator=Paginator(articlelist,3)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    return render(request,'blog/index.html',context={'post_list':post_list})


def article_post(request):
    if request.method == "POST":
        if request.session.get('is_login', None):
            article_post_form = ArticlePostForm(request.POST)
            if article_post_form.is_valid():
                article = article_post_form.save(commit=False)
                article.author = User.objects.get(name=request.session.get('user_name'))
                article.created_time = timezone.now()
                article.save()
                return redirect('/blog')
            else:
                return HttpResponse('表单内容有误')
        else:
            return HttpResponse('您尚未登陆,无法写文章')
    else:
        if request.session.get('is_login', None):
            article_post_form = ArticlePostForm()
            category_list = Category.objects.all()
            tags_list = Tag.objects.all()
            context = {'article_post_form': article_post_form, 'categoty_list': category_list, 'tags_list': tags_list}
            return render(request, 'blog/create.html', context)
        else:
            return HttpResponse('您尚未登陆,无法写文章')


def article_delete(request, id):
    if request.method == "POST":
        article = Post.objects.get(id=id)
        article.delete()
        return redirect('/blog')
    else:
        return HttpResponse("非法")


def article_edit(request, id):
    article = Post.objects.get(id=id)
    if request.method == "POST":
        if request.session.get('is_login', None):
            article_post_form = ArticlePostForm(request.POST)
            if article_post_form.is_valid():
                article.title = request.POST['title']
                article.body = request.POST['body']
                article.category = Category.objects.get(id=request.POST['category'])
                article.tags.set(*request.POST.get('tags').split(','), clear=True)
                article.save()
                return redirect("blog:detail", pk=id)
            else:
                return HttpResponse('表单内容有误')
        else:
            return HttpResponse('您尚未登陆,无法写文章')
    else:
        if request.session.get('is_login', None):
            article_post_form = ArticlePostForm()
            category_list = Category.objects.all()
            tags_list = Tag.objects.all()
            context = {'article': article, 'article_post_form': article_post_form, 'categoty_list': category_list, 'tags_list': tags_list}
            return render(request, 'blog/edit.html', context)
        else:
            return HttpResponse('您尚未登陆,无法写文章')

