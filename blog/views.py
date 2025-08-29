from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Post, Category, Tag, Review
from .forms import ReviewForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status='published', published_at__isnull=False, published_at__lte=timezone.now())
        
        # Поиск
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(content__icontains=q) | 
                Q(excerpt__icontains=q)
            )
        
        # Фильтр по категории
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтр по тегу
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published', published_at__isnull=False, published_at__lte=timezone.now()).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Увеличиваем счетчик просмотров
        post.views_count += 1
        post.save(update_fields=['views_count'])
        
        # Похожие статьи
        context['related_posts'] = Post.objects.filter(
            status='published',
            published_at__isnull=False,
            published_at__lte=timezone.now(),
            category=post.category
        ).exclude(id=post.id)[:3]
        
        # Популярные статьи
        context['popular_posts'] = Post.objects.filter(
            status='published',
            published_at__isnull=False,
            published_at__lte=timezone.now()
        ).order_by('-views_count')[:5]
        
        # Отзывы (только корневые) с пагинацией
        reviews = post.reviews.filter(is_approved=True, parent__isnull=True).prefetch_related('replies')
        paginator = Paginator(reviews, 5)  # 5 отзывов на страницу
        page_number = self.request.GET.get('review_page')
        reviews_page = paginator.get_page(page_number)
        context['reviews'] = reviews_page
        
        # Форма отзыва
        context['review_form'] = ReviewForm()
        
        return context


@csrf_exempt
@require_http_methods(["POST"])
def submit_review(request, post_id):
    """AJAX view для отправки отзыва"""
    post = get_object_or_404(Post, id=post_id, status='published')
    form = ReviewForm(request.POST, request.FILES)
    
    if form.is_valid():
        review = form.save(commit=False)
        review.post = post
        review.ip_address = request.META.get('REMOTE_ADDR')
        # Если пользователь отмечает как админский ответ, разрешаем только при авторизованном админ юзере
        if form.cleaned_data.get('is_admin') and not (request.user.is_authenticated and request.user.is_staff):
            review.is_admin = False
        # Безопасность: parent должен принадлежать тому же посту
        parent = form.cleaned_data.get('parent')
        if parent and parent.post_id != post.id:
            parent = None
        review.parent = parent
        review.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Спасибо за ваш отзыв! Он будет опубликован после модерации.'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published', published_at__isnull=False, published_at__lte=timezone.now())
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'blog/post_list.html', context)


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published', published_at__isnull=False, published_at__lte=timezone.now())
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'posts': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'blog/post_list.html', context)


def search_posts(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            status='published',
            published_at__isnull=False,
            published_at__lte=timezone.now()
        )
    else:
        posts = Post.objects.none()
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'query': query,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'blog/post_list.html', context)
