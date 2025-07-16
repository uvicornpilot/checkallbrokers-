from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .models import ForumCategory, ForumTopic, ForumPost, ForumModerationLog, ForumNotification
from .forms import ForumTopicForm, ForumPostForm, ForumSearchForm, ForumModerationForm


class ForumIndexView(ListView):
    """Главная страница форума"""
    model = ForumCategory
    template_name = 'forum/index.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ForumCategory.objects.filter(is_active=True).annotate(
            topics_count=Count('topics', filter=Q(topics__is_active=True)),
            posts_count=Count('topics__posts', filter=Q(topics__posts__is_approved=True))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_topics'] = ForumTopic.objects.filter(is_active=True).order_by('-created_at')[:5]
        context['popular_topics'] = ForumTopic.objects.filter(is_active=True).order_by('-views_count')[:5]
        return context


class ForumCategoryDetailView(DetailView):
    """Детальная страница категории"""
    model = ForumCategory
    template_name = 'forum/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = self.object.topics.filter(is_active=True).annotate(
            posts_count=Count('posts', filter=Q(posts__is_approved=True))
        )
        
        # Пагінація
        paginator = Paginator(topics, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['topics'] = page_obj
        context['page_obj'] = page_obj
        return context


class ForumTopicDetailView(DetailView):
    """Детальная страница темы"""
    model = ForumTopic
    template_name = 'forum/topic_detail.html'
    context_object_name = 'topic'
    
    def get_object(self):
        obj = super().get_object()
        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем только одобренные посты
        posts = self.object.posts.filter(is_approved=True).order_by('created_at')
        
        # Пагинация
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['posts'] = page_obj
        context['page_obj'] = page_obj
        context['post_form'] = ForumPostForm(topic=self.object)
        context['reply_form'] = ForumPostForm(topic=self.object)
        
        # Добавляем посты, ожидающие модерации
        # Для авторизованных пользователей - их собственные посты
        # Для анонимных - посты с их email
        if self.request.user.is_authenticated:
            context['pending_posts'] = self.object.posts.filter(
                is_approved=False, 
                is_moderated=False,
                author=self.request.user
            ).order_by('created_at')
        else:
            # Для анонимных пользователей показываем посты с их email (если он есть в сессии)
            anonymous_email = self.request.session.get('anonymous_email')
            if anonymous_email:
                context['pending_posts'] = self.object.posts.filter(
                    is_approved=False, 
                    is_moderated=False,
                    anonymous_email=anonymous_email
                ).order_by('created_at')
        
        return context


class ForumTopicCreateView(LoginRequiredMixin, CreateView):
    """Створення нової теми"""
    model = ForumTopic
    form_class = ForumTopicForm
    template_name = 'forum/topic_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Тема створена! Вона буде опублікована після модерації.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('forum:topic_detail', kwargs={'slug': self.object.slug})


class ForumPostCreateView(CreateView):
    """Створення коментаря (для всіх користувачів)"""
    model = ForumPost
    form_class = ForumPostForm
    template_name = 'forum/post_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['topic'] = get_object_or_404(ForumTopic, slug=self.kwargs['topic_slug'])
        if 'parent_id' in self.kwargs:
            kwargs['parent'] = get_object_or_404(ForumPost, id=self.kwargs['parent_id'])
        # Передаємо автора, якщо користувач авторизований
        if self.request.user.is_authenticated:
            kwargs['author'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Якщо користувач авторизований, встановлюємо автора
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        else:
            # Зберігаємо email анонімного користувача в сесії
            if form.cleaned_data.get('anonymous_email'):
                self.request.session['anonymous_email'] = form.cleaned_data['anonymous_email']
        
        post = form.save()
        messages.success(self.request, 'Коментар додано! Він буде опублікований після модерації.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('forum:topic_detail', kwargs={'slug': self.kwargs['topic_slug']})


class ForumSearchView(ListView):
    """Пошук по форуму"""
    model = ForumTopic
    template_name = 'forum/search.html'
    context_object_name = 'results'
    paginate_by = 20
    
    def get_queryset(self):
        form = ForumSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q', '')
            category = form.cleaned_data.get('category')
            search_in = form.cleaned_data.get('search_in', 'all')
            
            if not q:
                return ForumTopic.objects.none()
            
            queryset = ForumTopic.objects.filter(is_active=True)
            
            if category:
                queryset = queryset.filter(category=category)
            
            if search_in == 'topics':
                queryset = queryset.filter(
                    Q(title__icontains=q) | Q(content__icontains=q)
                )
            elif search_in == 'posts':
                queryset = queryset.filter(
                    posts__content__icontains=q,
                    posts__is_approved=True
                ).distinct()
            else:  # all
                queryset = queryset.filter(
                    Q(title__icontains=q) | 
                    Q(content__icontains=q) |
                    Q(posts__content__icontains=q, posts__is_approved=True)
                ).distinct()
            
            return queryset.order_by('-created_at')
        
        return ForumTopic.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ForumSearchForm(self.request.GET)
        return context


@login_required
def forum_post_reply(request, topic_slug, parent_id):
    """Відповідь на коментар"""
    topic = get_object_or_404(ForumTopic, slug=topic_slug)
    parent = get_object_or_404(ForumPost, id=parent_id, topic=topic)
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST, topic=topic, parent=parent)
        if form.is_valid():
            post = form.save(author=request.user)
            messages.success(request, 'Відповідь додана! Вона буде опублікована після модерації.')
            return redirect('forum:topic_detail', slug=topic_slug)
    else:
        form = ForumPostForm(topic=topic, parent=parent)
    
    return render(request, 'forum/post_reply.html', {
        'form': form,
        'topic': topic,
        'parent': parent
    })


@staff_member_required
def forum_moderation(request):
    """Сторінка модерації"""
    pending_posts = ForumPost.objects.filter(is_approved=False, is_moderated=False).order_by('created_at')
    
    if request.method == 'POST':
        form = ForumModerationForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get('post_id')
            post = get_object_or_404(ForumPost, id=post_id)
            action = form.cleaned_data['action']
            reason = form.cleaned_data['reason']
            
            if action == 'approve':
                post.is_approved = True
                post.is_moderated = True
                post.save()
                
                # Створюємо лог
                ForumModerationLog.objects.create(
                    moderator=request.user,
                    post=post,
                    action='approve',
                    reason=reason
                )
                
                # Створюємо сповіщення
                ForumNotification.objects.create(
                    user=post.author,
                    notification_type='post_approved',
                    post=post
                )
                
                messages.success(request, f'Пост від {post.author.username} одобрено.')
                
            elif action == 'reject':
                post.is_approved = False
                post.is_moderated = True
                post.save()
                
                # Створюємо лог
                ForumModerationLog.objects.create(
                    moderator=request.user,
                    post=post,
                    action='reject',
                    reason=reason
                )
                
                # Створюємо сповіщення
                ForumNotification.objects.create(
                    user=post.author,
                    notification_type='post_rejected',
                    post=post
                )
                
                messages.success(request, f'Пост від {post.author.username} відхилено.')
                
            elif action == 'delete':
                # Створюємо лог перед видаленням
                ForumModerationLog.objects.create(
                    moderator=request.user,
                    post=post,
                    action='delete',
                    reason=reason
                )
                
                post.delete()
                messages.success(request, f'Пост від {post.author.username} видалено.')
    
    return render(request, 'forum/moderation.html', {
        'pending_posts': pending_posts,
        'moderation_form': ForumModerationForm()
    })


@login_required
def forum_notifications(request):
    """Сторінка сповіщень"""
    notifications = ForumNotification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(ForumNotification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
    
    return render(request, 'forum/notifications.html', {
        'notifications': notifications
    })


@csrf_exempt
def forum_ajax_reply(request):
    """AJAX відповідь на коментар"""
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        parent_id = request.POST.get('parent_id')
        content = request.POST.get('content')
        anonymous_name = request.POST.get('anonymous_name', '')
        anonymous_email = request.POST.get('anonymous_email', '')
        
        if topic_id and content:
            topic = get_object_or_404(ForumTopic, id=topic_id)
            parent = None
            if parent_id:
                parent = get_object_or_404(ForumPost, id=parent_id, topic=topic)
            
            # Створюємо пост
            post = ForumPost.objects.create(
                topic=topic,
                parent=parent,
                content=content,
                author=request.user if request.user.is_authenticated else None,
                anonymous_name=anonymous_name if not request.user.is_authenticated else '',
                anonymous_email=anonymous_email if not request.user.is_authenticated else ''
            )
            
            # Зберігаємо email анонімного користувача в сесії
            if not request.user.is_authenticated and anonymous_email:
                request.session['anonymous_email'] = anonymous_email
            
            return JsonResponse({
                'success': True,
                'message': 'Коментар додано! Він буде опублікований після модерації.',
                'post_id': post.id
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Помилка при створенні коментаря'
    })


@csrf_exempt
def forum_ajax_create_post(request):
    """AJAX створення коментаря під постом"""
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        content = request.POST.get('content')
        anonymous_name = request.POST.get('anonymous_name', '')
        anonymous_email = request.POST.get('anonymous_email', '')
        
        if topic_id and content:
            topic = get_object_or_404(ForumTopic, id=topic_id)
            
            # Створюємо пост
            post = ForumPost.objects.create(
                topic=topic,
                content=content,
                author=request.user if request.user.is_authenticated else None,
                anonymous_name=anonymous_name if not request.user.is_authenticated else '',
                anonymous_email=anonymous_email if not request.user.is_authenticated else ''
            )
            
            # Зберігаємо email анонімного користувача в сесії
            if not request.user.is_authenticated and anonymous_email:
                request.session['anonymous_email'] = anonymous_email
            
            return JsonResponse({
                'success': True,
                'message': 'Коментар додано! Він буде опублікований після модерації.',
                'post_id': post.id,
                'author_name': post.get_author_name(),
                'created_at': post.created_at.strftime('%d.%m.%Y %H:%M')
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Помилка при створенні коментаря'
    })
