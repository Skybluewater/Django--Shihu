from django.db import models
from login.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=70)
    body = models.TextField()
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    excerpt = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    # 作者  使用django内置应用
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    posts = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']

    """ 1.reverse的'blog:detail'对应blog应用下的name='detail'的方法(对应urls.py的name)
        2.reverse()方法会去解析'blog:detail'的url,解析规则是根据urls.py里的正则.
        3.根据正则规则,解析结果为post/255/,这样Post自己就生成了自己的url
        4.kwargs表示按照关键字传值将多余的传值用字典形式呈现
    """

    # 自定义获取路径方法
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    # 阅读量增加(粗略统计,同时访问被忽略)
    def increase_views(self):
        # 该函数每被调用一次 views+1
        self.views += 1
        # 只更新数据库中views字段的值
        self.save(update_fields=['views'])

    # 摘要逻辑 重写save()方法,保存到数据库之前进行一次过滤
    def save(self, *args, **kwargs):
        self.created_time = timezone.now()
        self.modified_time = self.created_time
        # 如果没填写摘要
        if not self.excerpt:
            # 实例化一个Markdown对象,用于渲染body的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        # 调用父类的 save 方法将数据保存到数据库中
        # 这里save不能有self参数(不能在模型保存中强制更新和插入)
        super(Post, self).save(*args, **kwargs)
