from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_model_post_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post.text))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_names(self):
        group = self.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group.title))
