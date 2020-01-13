import re
import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, QueryDict
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from .models import Post, Category, Tag, Answer, Liked
from .forms import ArticlePostForm, ArticleForm, AnswerForm, AnswerPostForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from comments.models import Comment
from django.db.models import Q


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.body.replace("\r\n", '  \n')
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ], safe_mode=True, enable_attributes=False)
    post.increase_views()
    post.body = md.convert(post.body)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    answer_list = Answer.objects.filter(post=post).order_by('-views')
    like_list = Liked.objects.filter(post=post)
    if request.session.get('is_login', None):
        id = request.session['user_id']
        if id == post.author.id:
            k = 'allowed'
            return render(request, "blog/single.html",
                          context={'post': post, 'delete_allowance': k, 'answer_list': answer_list,
                                   'like_list': like_list})
    k = 'not_allowed'
    return render(request, "blog/single.html",
                  context={'post': post, 'delete_allowance': k, 'answer_list': answer_list, 'like_list': like_list})


def archive(request, year, month):
    articlelist = Post.objects.filter(created_time__year=year,
                                      created_time__month=month
                                      ).order_by('-created_time')
    paginator = Paginator(articlelist, 10)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def focus(request):
    user = User.objects.get(id=request.session.get('user_id', None))
    articlelist = Post.objects.filter(users_focus=user.id
                                      ).order_by('-created_time')
    paginator = Paginator(articlelist, 10)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    context = {'post_list': post_list}
    return render(request, 'blog/focus.html', context)


def article_focus(request, id):
    article = Post.objects.get(id=id)
    user = User.objects.get(id=request.session.get('user_id', None))
    focus = article.users_focus.all()
    i = 0
    while i < focus.__len__():
        if focus[i].id == user.id:
            break
        else:
            i = i + 1
    if i < focus.__len__():
        return HttpResponse("3")
    try:
        article.users_focus.add(user)
        return HttpResponse("1")
    except:
        return HttpResponse("2")


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    articlelist = Post.objects.filter(category=cate).order_by('-created_time')
    paginator = Paginator(articlelist, 10)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    articlelist = Post.objects.filter(tags=tag).order_by('-created_time')
    paginator = Paginator(articlelist, 10)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def Money(request):
    return render(request, 'blog/_NeedMoney.html')


def article_list(request):
    if request.GET.get('order') == 'total_views':
        articlelist = Post.objects.all().order_by('-views')
        order = 'total_views'
    else:
        articlelist = Post.objects.all()
        order = 'normal'
    paginator = Paginator(articlelist, 10)
    page = request.GET.get('page')
    post_list = paginator.get_page(page)
    context = {'post_list': post_list, 'order': order}
    return render(request, 'blog/index.html', context)


def article_post(request):
    if request.method == "POST":
        if request.session.get('is_login', None):

            rPost = request.POST.copy()

            if ('' == rPost['category']):
                return HttpResponse('表单内容有误')
            else:
                if rPost['category'] not in [c.name for c in Category.objects.all()]:
                    category = Category(name=rPost['category'])
                    category.save()
                rPost['category'] = str(Category.objects.get(name=rPost['category']).id)

            if ('' == rPost['tags']):
                return HttpResponse('表单内容有误')
            else:
                ids = []
                tags = [t.name for t in Tag.objects.all()]
                for tag in rPost['tags'].split():
                    if tag not in tags:
                        t = Tag(name=tag)
                        t.save()
                    ids.append(Tag.objects.get(name=tag).id)

                init_string = ''
                for i in ids:
                    init_string = init_string + 'tags=' + str(i) + '&'
                rPost.pop('tags')
                rPost.update(QueryDict(init_string))

            article_post_form = ArticleForm(rPost)
            if article_post_form.is_valid():
                article = article_post_form.save(commit=False)
                article.author = User.objects.get(username=request.session.get('user_name'))
                article.created_time = timezone.now()
                article.save()
                article.tags.set(article_post_form.cleaned_data['tags'])
                print(article.tags)
                return redirect('/blog')
            else:
                return HttpResponse('表单内容有误')
        else:
            return HttpResponse('您尚未登陆,无法写问题')
    else:
        if request.session.get('is_login', None):
            article_post_form = ArticleForm()
            category_list = Category.objects.all()
            tags_list = Tag.objects.all()
            context = {'article_post_form': article_post_form, 'categoty_list': category_list, 'tags_list': tags_list}
            return render(request, 'blog/create.html', context)
        else:
            return HttpResponse('您尚未登陆,无法写问题')


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
            article_post_form = ArticleForm(request.POST)
            if article_post_form.is_valid():
                article.title = request.POST['title']
                article.body = request.POST['body']
                article.category = Category.objects.get(id=request.POST['category'])
                article.save()
                article.tags.set(article_post_form.cleaned_data['tags'])
                return redirect("blog:detail", pk=id)
            else:
                return HttpResponse('表单内容有误')
        else:
            return HttpResponse('您尚未登陆,无法写问题')
    else:
        if request.session.get('is_login', None):
            dic = {'title': article.title, 'body': article.body, 'category': article.category, 'tags': article.tags}
            article_post_form = ArticlePostForm(dic)
            category_list = Category.objects.all()
            tags_list = Tag.objects.all()
            context = {'article': article, 'article_post_form': article_post_form, 'categoty_list': category_list,
                       'tags_list': tags_list}
            return render(request, 'blog/edit.html', context)
        else:
            return HttpResponse('您尚未登陆,无法写问题')


def answer_post(request, id):
    if request.method == "POST":
        if request.session.get('is_login', None):
            if not Post.objects.filter(id=id):
                return HttpResponse('没有这篇文章')
            answer = AnswerPostForm(request.POST)
            if answer.is_valid():
                article = answer.save(commit=False)
                article.author = User.objects.get(username=request.session.get('user_name'))
                article.created_time = timezone.now()
                article.post = Post.objects.get(id=id)
                article.save()
                article.tags.set(answer.cleaned_data['tags'])
                print(article.tags)
                return redirect('blog:answer_detail', article.id)
            else:
                return HttpResponse('表单内容有误')
        else:
            return HttpResponse('您尚未登陆,无法写回答')
    else:
        if request.session.get('is_login', None):
            if not Post.objects.filter(id=id):
                return HttpResponse('没有这篇文章')
            answer = AnswerPostForm()
            tags_list = Tag.objects.all()
            context = {'answer_form': answer, 'tags_list': tags_list, 'post': Post.objects.get(id=id)}
            return render(request, 'blog/create_answer.html', context)
        else:
            return HttpResponse('您尚未登陆,无法写回答')


def answer_del(request, id):
    if request.method == "POST":
        if not request.session.get('is_login', None):
            return HttpResponse('您尚未登录,请登录后操作')
        article = Answer.objects.get(id=id)
        if not article.author.id == request.session.get('user_id', None):
            return HttpResponse('这不是您的文章,请查证后操作')
        post = Post.objects.get(id=article.post.id)
        article.delete()
        return redirect('blog:detail', post.id)
    else:
        return HttpResponse("非法操作")


def answer_edit(request, id):
    if not request.session.get('is_login', None):
        return HttpResponse('您尚未登陆,无法操作')
    if not Answer.objects.filter(id=id):
        return HttpResponse('无此回答,请确认后操作')
    answer = Answer.objects.get(id=id)
    if not answer.author.id == request.session.get('user_id', None):
        return HttpResponse('非法操作!')
    if request.method == "POST":
        answer_form = AnswerPostForm(request.POST)
        if answer_form.is_valid():
            answer.title = request.POST['title']
            answer.body = request.POST['body']
            answer.save()
            answer.tags.set(answer_form.cleaned_data['tags'])
            return redirect('blog:answer_detail', answer.id)
        else:
            return HttpResponse('表单内容有误,请重新输入')
    else:
        dic = {'title': answer.title, 'body': answer.body, 'tags': answer.tags}
        answer_form = AnswerForm(dic)
        tags_list = Tag.objects.all()
        context = {'answer_form': answer_form, 'tags_list': tags_list, 'id': answer.post.id}
        return render(request, 'blog/answer_edit.html', context)


def answer_detail(request, id):
    answer = get_object_or_404(Answer, id=id)
    answer.body.replace("\r\n", '  \n')
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ], safe_mode=True, enable_attributes=False)
    answer.increase_views()
    answer.body = md.convert(answer.body)
    pre_article = Answer.objects.filter(id__lt=answer.id).order_by('-id')
    next_article = Answer.objects.filter(id__gt=answer.id).order_by('id')
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None

    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    answer.toc = m.group(1) if m is not None else ''
    if request.session.get('is_login', None):
        id = request.session['user_id']
        if id == answer.author.id:
            k = 'allowed'
            return render(request, "blog/answer.html",
                          context={'answer': answer, 'delete_allowance': k, 'pre_article': pre_article,
                                   'next_article': next_article, })
    k = 'not_allowed'
    return render(request, "blog/answer.html",
                  context={'answer': answer, 'delete_allowance': k, 'pre_article': pre_article,
                           'next_article': next_article, })


def on_like(request, id):
    user = User.objects.get(username=request.session.get('user_name'))
    post = Post.objects.get(id=id)
    like = Liked.objects.filter(Q(post=post)|Q(user=user))
    if like:
        return HttpResponse("您已经点过赞了！")
    post = get_object_or_404(Post, id=id)
    like = Liked(user=user, post=post)
    post.likecount += 1
    post.save()
    like.save()
    return HttpResponse("点赞成功！")
