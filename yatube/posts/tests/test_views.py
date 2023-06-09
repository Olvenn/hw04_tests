import shutil
import tempfile
import random
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from yatube.constants import POSTS_PER_STR

from ..models import Group, Post, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostMainViewTests(TestCase):
    """Тесты проверки где достаточно проверить один пост."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

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

        cls.author_client = Client()
        cls.author_client.force_login(PostMainViewTests.author)

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

        cls.post = Post.objects.create(
            group=PostMainViewTests.group,
            text='Тестовый пост',
            author=cls.author,
            image=uploaded,
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
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_author_0, 'FirstAuthor')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_page_show_correct_context(self):
        """Проверка отображения на странице группы"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      args=[self.group.slug]))
        first_object = response.context['page_obj'][0]
        post_image_0 = first_object.image
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_image_0, 'posts/small.gif')
    
    def test_post_on_author_page(self):
        """Проверка отображения нового поста на странице автора"""
        response = (self.authorized_client.
                    get(reverse('posts:profile', args=[self.author.username])))
        first_object = response.context['page_obj'][0]
        post_image_0 = first_object.image
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_image_0, 'posts/small.gif')
    

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'})))
        self.assertEqual(response.context.get('post').group.title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').image, 'posts/small.gif')

    def test_context_in_profile(self):
        """Шаблон post_profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
            get(reverse('posts:profile', args=[self.author.username])))
        self.assertEqual(response.context.get('post').group.title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').image, 'posts/small.gif')

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

    def test_add_comment_correct(self):
        """Комментировать посты может только авторизованный пользователь."""
        form_data = {'text': 'test_add_comment_correct', }
        add_comment_url = reverse(
            'posts:add_comment', kwargs={
                'post_id': PostMainViewTests.post.id
            }
        )
        response = self.client.post(
            add_comment_url,
            data=form_data,
            follow=True
        )
        # проверяем корректность редиректа неавторизованного пользователя
        self.assertRedirects(
            response, f'{reverse("users:login")}?next={add_comment_url}'
        )
        # создаем комментарий
        form_data = {'text': 'test_add_comment_correct', }
        response = self.authorized_client.post(
            add_comment_url,
            data=form_data,
            follow=True,
        )
        # проверяем корректность редиректа
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostMainViewTests.post.id
                }
            )
        )
        # проверяем, что первый комментарий на странице только что добавленный
        self.assertIn('comments', response.context)
        self.assertGreaterEqual(len(response.context['comments']), 1)
        self.assertEqual(
            response.context['comments'][0].text, form_data['text']
        )


class CacheIndexPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.author = User.objects.create(
            username='Author',
        )
        
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='group-slug',
        )

        cls.post = Post.objects.create(
            group=cls.group,
            text='Тестовый пост для проверки кэширования.',
            author=cls.author,
        )
    
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_cach_in_index_page(self):
        """Проверяем работу кеша на главной странице"""

        # проверим, что пост есть
        response_1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response_1.content,
            response_2.content
        )
        cache.clear()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_1.content,
            response_2.content
        )


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
        cache.clear()

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


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='followingUser')
        cls.author_user = Client()
        cls.author_user.force_login(cls.author)
        cls.follower = User.objects.create_user(username='followerUser')
        cls.follower_user = Client()
        cls.follower_user.force_login(cls.follower)
        cls.unfollower = User.objects.create_user(username='User')
        cls.unfollower_user = Client()

        cls.post = Post.objects.create(
            author=cls.author,
            text='текст'
        )

    def test_user_can_following(self):
        """Авторизованный пользователь может
        подписаться на другого пользователя"""
        count = Follow.objects.count()
        self.follower_user.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.count(), count + 1)

    def test_user_can_unfollowing(self):
        """Пользователь может отменить подписку на автора"""
        self.follower_user.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}))
        count = Follow.objects.count()
        self.follower_user.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.count(), count - 1)