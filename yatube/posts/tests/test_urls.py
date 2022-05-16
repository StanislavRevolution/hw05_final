from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stanislav')
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.force_login(self.author)

    def test_available_of_pages_guest(self):
        """Проводим проверку доступности страниц
         для неавторизованного пользователя"""

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/'
        }

        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_of_pages_authorized(self):
        """Проводим проверку доступности страниц
         для авторизованного пользователя"""

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
            'posts/follow.html': '/follow/'
        }

        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_weird_page(self):
        """Проверяем переход на несуществующую страницу"""
        response = self.client.get('/weird/page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_only_authorized(self):
        """Доступ к странице создания поста только авториз. польз."""

        address_url_names = {
            f'/profile/{self.user}/',
            f'/posts/{self.post.pk}/edit/'
        }
        for addrees in address_url_names:
            with self.subTest(addrees=addrees):
                response = self.authorized_client.get(addrees)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_correct_template(self):
        """Проверяем соответсвие шаблонов страницам"""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': f'/posts/{self.post.id}/edit/',
            'posts/follow.html': '/follow/'
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
