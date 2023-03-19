from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Тестовая группа')
        cls.group = mixer.blend(Group, title='test2')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_str_(self):
        """правильно ли отображается
        значение поля __str__ в модели Post"""

        test_items = {
            self.post: self.post.text[:15],
        }

        for field, expected_value in test_items.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value)


class GroupeModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = mixer.blend(Post, tittextle='Тестовый пост')

    def test_str_(self):
        """правильно ли отображается
        значение поля __str__ в модели Group"""

        test_items = {
            self.group: self.group.title,
        }

        for field, expected_value in test_items.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value)
