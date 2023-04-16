from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()
ADMINS_POST_LENGHT = 15


class Group(models.Model):
    """Получаем модель для Группы постов."""

    title = models.CharField(
        verbose_name='Имя',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        max_length=100,
        unique=True,
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        ordering = ('title',)
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        """Возвращаем название группы."""
        return self.title


class Post(CreatedModel):
    """Получаем модель Поста."""

    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст нового поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_of_posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts_in_group',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку, если желаете',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Возвращаем текст Поста."""
        return (
            self.text[:ADMINS_POST_LENGHT] + '...'
            if len(self.text) >= ADMINS_POST_LENGHT
            else self.text
        )


class Comment(CreatedModel):
    """Получаем модель для написания комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='post_comments',
        verbose_name='Комментарий к посту',
        help_text='Пост комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_comments',
        verbose_name='Комментарий автора',
        help_text='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст коммментария',
        help_text='Текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращаем текст Комментария."""
        return (
            self.text[:ADMINS_POST_LENGHT] + '...'
            if len(self.text) >= ADMINS_POST_LENGHT
            else self.text
        )


class Follow(models.Model):
    """Получаем модель для осуществления подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор в подписке',
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'author',
                ],
                name='unique_follow',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        """Возвращаем читаемую связку Подписки."""
        return (
            f'{self.user} подписан на {self.author}'
        )


class PostRating(models.Model):
    """Получаем модель оценки постов."""


    post = models.ForeignKey(
        Post,
        verbose_name='Оцениваемый пост',
        related_name='rating_post',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='rating_user',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'post',
                    'user',
                ],
                name='unique_post_rating',
            )
        ]
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        """Возвращаем читаемую связку рейтинга постов."""
        return (
            f'{self.user} оценил {self.post}'
        )
