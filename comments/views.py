from django.shortcuts import render

# Create your views here.
from blog.models import Post
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from .forms import CommentForm
from login.models import User
import markdown

@require_POST
def comment(request, post_pk):
    # 先获取被评论的文章，因为后面需要把评论和被评论的文章关联起来。
    # 这里我们使用了 django 提供的一个快捷函数 get_object_or_404，
    # 这个函数的作用是当获取的文章（Post）存在时，则获取；否则返回 404 页面给用户。
    post = get_object_or_404(Post, pk=post_pk)
    # django 将用户提交的数据封装在 request.POST 中，这是一个类字典对象。
    # 我们利用这些数据构造了 CommentForm 的实例，这样就生成了一个绑定了用户提交数据的表单。

    # 先把POST的内容过一遍markdown的渲染器
    # 这事是不是应该拿js在用户机器上做？
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
    ])
    # https://docs.djangoproject.com/zh-hans/3.0/ref/request-response/#django.http.QueryDict.__setitem__
    rPOST = request.POST.copy()
    rPOST.__setitem__("text", md.convert(rPOST.get("text")))
    form = CommentForm(rPOST)

    # 当调用 form.is_valid() 方法时，django 自动帮我们检查表单的数据是否符合格式要求。
    if form.is_valid():
        # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
        comment = form.save(commit=False)
        # 将评论和被评论的文章关联起来。
        comment.created_time = timezone.now()
        comment.post = post
        Author = User.objects.get(name=request.session.get('user_name'))
        comment.author = Author
        # 最终将评论数据保存进数据库，调用模型实例的 save 方法
        comment.save()
        # 重定向到 post 的详情页，实际上当 redirect 函数接收一个模型的实例时，它会调用这个模型实例的 get_absolute_url 方法，
        # 然后重定向到 get_absolute_url 方法返回的 URL。
        return redirect(post)
    # 检查到数据不合法，我们渲染一个预览页面，用于展示表单的错误。
    # 注意这里被评论的文章 post 也传给了模板，因为我们需要根据 post 来生成表单的提交地址。
    context = {
        'post': post,
        'form': form,
    }
    return redirect(post)
