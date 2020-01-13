from django import forms
from .models import Post
from mdeditor.fields import MDTextFormField


class ArticlePostForm(forms.Form):
    title = forms.CharField()
    body = MDTextFormField()
    category = forms.ChoiceField()
    tags = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        # 执行父类构造方法
        super(ArticlePostForm, self).__init__(*args, **kwargs)

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'tags')
