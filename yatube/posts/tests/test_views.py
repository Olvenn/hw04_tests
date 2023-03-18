from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from http import HTTPStatus

import random

from ..models import Group, Post, User
from yatube.constants import POSTS_PER_STR


class PostMainViewTests(TestCase):
    """Тесты проверки где достаточно проверить один пост."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='group-slug',
        )

        cls.author = User.objects.create_user(
            first_name='Лев',
            last_name='Толстой',
            username='FirstAuthor',
            email='lev@yatube.ru'
        )

        cls.post = Post.objects.create(
            group=PostMainViewTests.group,
            text='Тестовый пост',
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostMainViewTests.author)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_page_has_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={'slug': f'{self.group.slug}'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{self.post.id}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{self.post.id}'}): 'posts/post_detail.html',
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_home_page_show_correct_context(self):
        """Пост отображается на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]

        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_author_0, 'FirstAuthor')

    def test_home_page_show_correct_context(self):
        """Пост отображается на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]

        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_author_0, 'FirstAuthor')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'})))
        self.assertEqual(response.context.get('post').group.title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')

    def test_create_post__page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_correct_context(self):
        response = self.author_client.get(reverse('posts:post_edit',
                                          args=[PostMainViewTests.post.id]))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        PAGES_COUNT_1 = 14
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            description='Тестовое описание 1',
            slug='group-slug',
        )

        cls.group_2 = Group.objects.create(
            title="Тестовая группа 2",
            description="Тестовое описание 2",
            slug="group_slug_2",
        )

        cls.author = User.objects.create_user(
            first_name='Лев',
            last_name='Толстой',
            username='FirstAuthor',
            email='lev@yatube.ru'
        )

        cls.author_2 = User.objects.create_user(
            first_name='Mark',
            last_name='Tven',
            username='SecondAuthor',
            email='mark@yatube.ru'
        )

        cls.post = Post.objects.bulk_create([
            Post(group=PostMainViewTests.group,
                 text=f'Тест  1-{i + 1}',
                 author=cls.author,)
            for i in range(1, PAGES_COUNT_1)
        ])

        cls.post = Post.objects.create(
            group=PostMainViewTests.group,
            text="Пост для проверки",
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_group_page_show_correct_context(self):
        """Пост отображается на странице группы"""
        response = self.authorized_client.get(
            reverse('posts:group', args=['group-slug']))
        num = random.randint(1, POSTS_PER_STR - 1)
        first_object = response.context['page_obj'][num]
        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, 'Тестовая группа 1')

    def test_context_in_profile(self):
        """Проверка содержимого словаря context для /<username>/"""
        response = (self.authorized_client.
                    get(reverse('posts:profile', args=[self.author.username])))
        num = random.randint(1, POSTS_PER_STR - 1)
        first_object = response.context['page_obj'][num]
        post_author_0 = first_object.author.username
        self.assertEqual(post_author_0, 'FirstAuthor')

    def test_post_on_main_page(self):
        """проверка отображения на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пост для проверки")

    def test_post_on_group_page(self):
        """Проверка отображения на странице группы"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      args=[self.group.slug]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пост для проверки")

    def test_post_on_group_page(self):
        """проверка отображения на странице группы"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      args=[self.group.slug]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пост для проверки")

    def test_post_on_group_page(self):
        """Проверка отображения на странице группы"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      args=[self.group.slug]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пост для проверки")

    def test_post_on_group_page(self):
        """Проверка отображения на странице автора"""
        response = (self.authorized_client.
                    get(reverse('posts:profile', args=[self.author.username])))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пост для проверки")

    def test_post_delete(self):
        """Проверка удаления поста"""
        Post.objects.filter(text="Тест 1-14").delete()
        response = (self.authorized_client.
                    get(reverse('posts:profile', args=[self.author.username])))
        self.assertNotContains(response, "Тест 1-14")


class paginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(15):
            cls.post = Post.objects.create(
                text=f'Тестовый пост номер {count}',
                author=cls.user)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 5)
