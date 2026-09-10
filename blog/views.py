from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ArticlePage, Category, Tag
from .forms import ReviewForm
from django.db import models
from .models import Review


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = (
        ArticlePage.objects.live()
        .filter(category=category)
        .order_by("-first_published_at")
    )

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "category": category,
        "posts": page_obj,
        "categories": Category.objects.filter(is_active=True),
        "tags": Tag.objects.all(),
    })


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = (
        ArticlePage.objects.live()
        .filter(tags=tag)
        .order_by("-first_published_at")
    )

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "tag": tag,
        "posts": page_obj,
        "categories": Category.objects.filter(is_active=True),
        "tags": Tag.objects.filter(is_active=True),
    })


def search_posts(request):
    query = request.GET.get("q", "")
    posts = ArticlePage.objects.live().search(query) if query else ArticlePage.objects.none()

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "posts": page_obj,
        "query": query,
        "categories": Category.objects.filter(is_active=True),
        "tags": Tag.objects.filter(is_active=True),
    })


def _get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


@require_http_methods(["POST"])
def submit_review(request, post_id):
    """AJAX-приём комментария. Требует CSRF-токен из формы/куки — csrf_exempt убран намеренно (была дыра в безопасности)."""
    post = get_object_or_404(ArticlePage.objects.live(), id=post_id)

    # Honeypot: поле 'website' видимо только ботам (спрятано в CSS).
    # Если оно заполнено — притворяемся, что всё прошло успешно, но ничего не сохраняем.
    # Бот думает, что комментарий опубликован, и не пытается обойти защиту повторно.
    if request.POST.get("website"):
        return JsonResponse({
            "success": True,
            "message": "Спасибо за ваш отзыв! Он будет опубликован после модерации.",
        })

    form = ReviewForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    review = form.save(commit=False)
    review.post = post
    review.ip_address = _get_client_ip(request)

    parent = form.cleaned_data.get("parent")
    if parent and parent.post_id != post.id:
        parent = None
    review.parent = parent

    review.save()

    return JsonResponse({
        "success": True,
        "message": "Спасибо за ваш отзыв! Он будет опубликован после модерации.",
    })

@require_http_methods(["POST"])
def mark_review_helpful(request, review_id):
    """AJAX: +1 к счётчику 'Полезно' у отзыва. Без строгой защиты от повторных
    голосов на сервере — блокировка повтора делается на клиенте (localStorage),
    этого достаточно для косметической метрики, не для голосования с весом."""


    review = get_object_or_404(Review, id=review_id, status=Review.Status.APPROVED)
    Review.objects.filter(pk=review.pk).update(helpful_count=models.F("helpful_count") + 1)
    review.refresh_from_db(fields=["helpful_count"])

    return JsonResponse({"success": True, "helpful_count": review.helpful_count})

