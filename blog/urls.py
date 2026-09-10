from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("category/<slug:slug>/", views.category_posts, name="category"),
    path("tag/<slug:slug>/", views.tag_posts, name="tag"),
    path("search/", views.search_posts, name="search"),
    path("post/<int:post_id>/submit-review/", views.submit_review, name="submit_review"),
    path("review/<int:review_id>/mark-helpful/", views.mark_review_helpful, name="mark_review_helpful"),
]