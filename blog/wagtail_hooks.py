from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, CreateView, IndexView
from wagtail.admin.ui.tables import Column
from wagtail.admin.widgets.button import Button
from wagtail.images.formats import unregister_image_format, register_image_format, Format

from .models import Review, ArticlePage, AuthorPage


# --- Комментарии: список в стиле WordPress ---

class ReviewCreateView(CreateView):
    """Форма создания комментария. Если пришли с 'Ответить' — предзаполняем поля."""

    def get_initial(self):
        initial = super().get_initial()
        parent_id = self.request.GET.get("parent")
        post_id = self.request.GET.get("post")

        if parent_id:
            initial["parent"] = parent_id
        if post_id:
            initial["post"] = post_id

        if self.request.GET.get("reply") == "1":
            initial["name"] = "Администратор"
            initial["is_admin"] = True
            initial["status"] = Review.Status.APPROVED

        return initial


class ReviewIndexView(IndexView):
    """Список комментариев с дополнительной кнопкой 'Ответить как администратор' в меню '...'."""

    def get_list_buttons(self, instance):
        buttons = super().get_list_buttons(instance)

        reply_url = (
            reverse("wagtailsnippets_blog_review:add")
            + f"?parent={instance.pk}&post={instance.post_id}&reply=1"
        )
        buttons.append(
            Button(
                label="Ответить как администратор",
                url=reply_url,
                priority=50,
            )
        )
        return buttons


class ReviewActionsColumn(Column):
    """Кастомная нессортируемая колонка со ссылками действий."""

    def get_value(self, instance):
        approve_url = reverse("review_quick_action", args=[instance.pk, "approve"])
        reject_url = reverse("review_quick_action", args=[instance.pk, "reject"])
        reply_url = (
            reverse("wagtailsnippets_blog_review:add")
            + f"?parent={instance.pk}&post={instance.post_id}&reply=1"
        )
        return format_html(
            '<a href="{}">Одобрить</a> · <a href="{}">Отклонить</a> · <a href="{}">Ответить</a>',
            approve_url, reject_url, reply_url,
        )


class ReviewViewSet(SnippetViewSet):
    model = Review
    icon = "comment"
    menu_label = "Комментарии"
    menu_order = 200
    add_view_class = ReviewCreateView
    index_view_class = ReviewIndexView

    list_display = [
        "name", "post", "rating", "status", "created_at",
        ReviewActionsColumn("actions", label="Действия", sort_key=None),
    ]
    list_filter = ["status", "is_admin", "rating"]
    search_fields = ["name", "text", "post__title"]
    ordering = ["-created_at"]


register_snippet(ReviewViewSet)


@staff_member_required
def review_quick_action(request, pk, action):
    review = get_object_or_404(Review, pk=pk)

    if action == "approve":
        review.status = Review.Status.APPROVED
    elif action == "reject":
        review.status = Review.Status.REJECTED
    review.save(update_fields=["status"])

    return redirect(reverse("wagtailsnippets_blog_review:list"))


@hooks.register("register_admin_urls")
def register_review_admin_urls():
    return [
        path(
            "reviews/<int:pk>/<str:action>/",
            review_quick_action,
            name="review_quick_action",
        ),
    ]


# --- Права юристов: видят и редактируют только свои статьи ---

@hooks.register("construct_page_queryset")
def limit_articles_to_own_author(pages, request):
    if pages.model is ArticlePage and not request.user.is_superuser:
        try:
            author = request.user.author_profile
            return pages.filter(author=author)
        except AuthorPage.DoesNotExist:
            return pages.none()
    return pages



# --- Форматы изображений в RichText — ограничение размера ---

unregister_image_format('fullwidth')
register_image_format(Format(
    'fullwidth', 'Full width', 'richtext-image full-width', 'fill-800x450'
))

unregister_image_format('left')
register_image_format(Format(
    'left', 'Left-aligned', 'richtext-image left', 'width-400'
))

unregister_image_format('right')
register_image_format(Format(
    'right', 'Right-aligned', 'richtext-image right', 'width-400'
))