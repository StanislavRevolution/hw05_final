from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        cls.user = User.objects.create_user(username='Stanislav')

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test-txxtt',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.order_by('pub_date').first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_change_post(self):
        group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='Тестовое-описание',
        )
        post = Post.objects.create(
            author=self.user,
            text='test-text',
            group=group
        )
        form_data = {
            'text': 'new-edit-text'
        }
        self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        post.refresh_from_db()
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                pk=post.id
            ).exists()
        )

    def test_of_comments_posts(self):
        post = Post.objects.create(
            author=self.user,
            text='test-text',
        )
        form_data = {
            'text': 'test-comment'
        }
        self.authorized_user.post(
            reverse('posts:add_comment', kwargs={"post_id": post.pk}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=self.user,
                post=post
            ).exists()
        )
