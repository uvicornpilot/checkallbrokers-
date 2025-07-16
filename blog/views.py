from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Post, Category, Tag


class PostListView(ListView):
    """Список всех статей"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Получаем только опубликованные статьи"""
        return Post.objects.filter(status='published').select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.filter(is_active=True)
        context['meta_title'] = "Блог - Broker Control"
        context['meta_description'] = "Полезные статьи о проверке брокеров, защите инвесторов и юридических консультациях"
        return context


class PostDetailView(DetailView):
    """Детальная страница статьи"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        """Получаем только опубликованные статьи"""
        return Post.objects.filter(status='published').select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Увеличиваем счетчик просмотров
        post.increase_views()
        
        # Добавляем SEO метаданные
        context['meta_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or post.excerpt
        context['meta_keywords'] = post.meta_keywords
        
        # Похожие статьи
        related_posts = Post.objects.filter(
            status='published',
            category=post.category
        ).exclude(id=post.id)[:3]
        context['related_posts'] = related_posts
        
        # Популярные статьи
        popular_posts = Post.objects.filter(status='published').order_by('-views_count')[:5]
        context['popular_posts'] = popular_posts
        
        return context


class CategoryPostListView(ListView):
    """Список статей по категории"""
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Получаем статьи конкретной категории"""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Post.objects.filter(
            status='published',
            category=self.category
        ).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.filter(is_active=True)
        context['meta_title'] = f"{self.category.name} - Broker Control"
        context['meta_description'] = self.category.description or f"Статьи в категории {self.category.name}"
        return context


class TagPostListView(ListView):
    """Список статей по тегу"""
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Получаем статьи с конкретным тегом"""
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'], is_active=True)
        return Post.objects.filter(
            status='published',
            tags=self.tag
        ).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.filter(is_active=True)
        context['meta_title'] = f"Тег: {self.tag.name} - Broker Control"
        context['meta_description'] = f"Статьи с тегом {self.tag.name}"
        return context


def search_posts(request):
    """Поиск по статьям"""
    query = request.GET.get('q', '')
    posts = []
    
    if query:
        posts = Post.objects.filter(
            Q(status='published') &
            (Q(title__icontains=query) | 
             Q(excerpt__icontains=query) | 
             Q(content__icontains=query))
        ).select_related('category').prefetch_related('tags')
    
    # Пагинация
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'query': query,
        'categories': Category.objects.filter(is_active=True),
        'tags': Tag.objects.filter(is_active=True),
        'meta_title': f"Поиск: {query} - Broker Control" if query else "Поиск - Broker Control",
        'meta_description': f"Результаты поиска для '{query}'" if query else "Поиск по статьям",
    }
    
    return render(request, 'blog/search_results.html', context)
