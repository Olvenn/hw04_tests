from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_str_(self):
        """правильно ли отображается
        значение поля __str__ в объектах моделей"""

        test_items = {
            PostModelTest.group: PostModelTest.group.title,
            PostModelTest.post: PostModelTest.post.text[:15],
        }

        for field, expected_value in test_items.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value)
