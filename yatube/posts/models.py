from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('уникальный адрес', max_length=50, unique=True)
    description = models.TextField('описание группы')

    def __str__(self):
        title = self.title
        return title[:15]


class Post(CreatedModel):
    text = models.TextField('содержание поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        text = self.text
        author = self.author
        group = self.group
        return text[:15] + " ; " + str(author) + " ; " + str(group)


class Comment(CreatedModel):
    text = models.TextField('содержание комментария')
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(self):
        user = self.user
        author = self.author
        return str(user) + " ; " + str(author)
