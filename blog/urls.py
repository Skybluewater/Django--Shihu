from django.urls import path, include
from . import views


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
    path("answer_detail/<int:id>/", views.answer_detail, name="answer_detail"),
    path("answer_delete/<int:id>/", views.answer_del, name="answer_delete"),
    path("answer_create/<int:id>", views.answer_post, name="answer_create"),
    path("answer_edit/<int:id>", views.answer_edit, name="answer_edit"),
]
