from django.urls import path, include
from . import views
from django.conf.urls import url


app_name = "blog"
urlpatterns = [
    path("", views.article_list, name="index"),
    path("posts/<int:pk>/", views.detail, name="detail"),
    path("archives/<int:year>/<int:month>/", views.archive, name="archive"),
    path("categories/<int:pk>/", views.category, name="category"),
    path("tags/<int:pk>/", views.tag, name="tag"),
    path("money/", views.Money, name="money"),
    path("create/", views.article_post, name="create"),
    path("delete/<int:id>", views.article_delete, name="delete"),
    path("edit/<int:id>", views.article_edit, name="edit"),
]
