from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Comment, Follow

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create_user(username='Stanislav')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse('posts:post_create')
        }
        # Проверяем, что при обращении вызывается HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_only_author_pages(self):
        '''Проверяем переход на cраницу редактирования'''
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_group_list(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            )
        )
        first_post = response.context.get('page_obj').object_list[0]
        group = Group.objects.get(slug=self.group.slug)
        image = open(f'{first_post.image.file}', 'rb').read()
        self.assertEqual(image, self.small_gif)
        self.assertEqual(first_post.group.title, group.title)

    def test_profile_posts(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        first_post = response.context.get('page_obj').object_list[0]
        image = open(f'{first_post.image.file}', 'rb').read()
        self.assertEqual(image, self.small_gif)
        self.assertEqual(first_post.author, self.user)

    def test_post_detail(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        first_post = response.context.get('post')
        post = Post.objects.get(pk=self.post.id)
        image = open(f'{first_post.image.file}', 'rb').read()
        self.assertEqual(image, self.small_gif)
        self.assertEqual(post, first_post)

    def test_create_post(self):
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)

    def test_post_edit_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        created_post = response.context['post']
        self.assertEqual(created_post, self.post)

    def test_of_post_on_index_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(self.post, first_object)

    def test_index_view(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_post = response.context.get('page_obj').object_list[0]
        image = open(f'{first_post.image.file}', 'rb').read()
        self.assertEqual(first_post.text, 'test-text')
        self.assertEqual(first_post.group.title, 'test-title')
        self.assertEqual(image, self.small_gif)

    def test_post_on_page_group_post(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(self.post, first_object)

    def test_post_on_profile_page_of_user(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        context = response.context['page_obj'][0]
        self.assertEqual(self.post, context)

    def test_comments_on_post_detail(self):
        """Проверяем, что комментарий отображается на странице поста"""
        form_data = {
            'text': 'test-comment'
        }
        comment = Comment.objects.create(
            author=self.user,
            text=form_data['text'],
            post=self.post
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={"post_id": self.post.pk}
            )
        )
        first_object = response.context['comments'][0]
        self.assertEqual(first_object, comment)

    # def test_work_of_cache(self):
    #     post_for_cache = Post.objects.create(
    #         author=self.user,
    #         text='test-cache'
    #     )
    #     response1 = self.authorized_client.get(reverse('posts:index'))
    #     post_for_cache.delete()
    #     response2 = self.authorized_client.get(reverse('posts:index'))
    #     self.assertEqual(response1.content, response2.content)
    #     cache.clear()
    #     response3 = self.authorized_client.get(reverse('posts:index'))
    #     self.assertNotEqual(response1.content, response3.content)
    #     cache.clear()

    def test_follow_on_users(self):
        maxim = User.objects.create_user(username='Maxim')
        Post.objects.create(
            author=maxim,
            text='test-text2',
        )
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': maxim.username}
            )
        )
        follow = Follow.objects.filter(user=self.user, author=maxim)
        self.assertTrue(follow.exists())
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': maxim.username}
            )
        )
        follow2 = Follow.objects.filter(user=self.user, author=maxim)
        self.assertFalse(follow2.exists())

    def test_of_displaying_subscriptions(self):
        maxim = User.objects.create_user(username='Maxim')
        gor = User.objects.create_user(username='Gor')
        self.authorized = Client()
        self.authorized.force_login(gor)
        post1 = Post.objects.create(
            author=maxim,
            text='test-text2',
        )
        Follow.objects.create(
            user=self.user,
            author=maxim
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        objects = response.context['page_obj']
        self.assertIn(post1, objects)
        response2 = self.authorized.get(
            reverse(
                'posts:follow_index'
            )
        )
        objects2 = response2.context['page_obj']
        self.assertNotIn(post1, objects2)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create_user(username='Stanislav')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(15):
            Post.objects.bulk_create(
                [Post(author=cls.user, text='test-text', group=cls.group)]
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.get(username='Stanislav')
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), settings.TEN)

    def test_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть пять постов.
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_paginator_of_group_list(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), settings.TEN)

    def test_paginator_of_profile(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(len(response.context['page_obj']), settings.TEN)
