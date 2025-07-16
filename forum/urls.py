from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Головна сторінка форуму
    path('', views.ForumIndexView.as_view(), name='index'),
    
    # Категорії
    path('category/<slug:slug>/', views.ForumCategoryDetailView.as_view(), name='category_detail'),
    
    # Теми
    path('topic/new/', views.ForumTopicCreateView.as_view(), name='topic_create'),
    path('topic/<slug:slug>/', views.ForumTopicDetailView.as_view(), name='topic_detail'),
    
    # Коментарі
    path('topic/<slug:topic_slug>/reply/', views.ForumPostCreateView.as_view(), name='post_create'),
    path('topic/<slug:topic_slug>/reply/<int:parent_id>/', views.ForumPostCreateView.as_view(), name='post_reply'),
    path('topic/<slug:topic_slug>/reply-to/<int:parent_id>/', views.forum_post_reply, name='post_reply_form'),
    
    # Пошук
    path('search/', views.ForumSearchView.as_view(), name='search'),
    
    # Модерація (тільки для адміністраторів)
    path('moderation/', views.forum_moderation, name='moderation'),
    
    # Сповіщення
    path('notifications/', views.forum_notifications, name='notifications'),
    
    # AJAX
    path('ajax/reply/', views.forum_ajax_reply, name='ajax_reply'),
    path('ajax/create-post/', views.forum_ajax_create_post, name='ajax_create_post'),
] 