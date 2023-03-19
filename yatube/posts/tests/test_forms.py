from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='NewTestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

    def test_post_form_create_new_post(self):
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст из формы',
            group=self.group.id
        ).exists())
        post_request = self.authorized_client.get(reverse('posts:index'))
        first_object = post_request.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый текст из формы')
        self.assertEqual(first_object.group.title, 'Тестовая группа')

    def test_post_edit_correct(self):
        self.post = Post.objects.create(
            author=self.author,
            text='Тестовый пост',
            group=self.group
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id
        }))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=form_data['text'],
            ).exists()
        )
