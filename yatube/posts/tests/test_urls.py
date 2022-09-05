from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.author = User.objects.create(username='korshikov')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.post = Post.objects.create(
            text='Test post',
            author=StaticURLTests.author,
            group=StaticURLTests.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_get_home_page(self):
        """Проверка доступности домашний страницы"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_404(self):
        """Проврека к несуществующей странице 404
        и нужного шаблона"""

        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response,'core/404.html')


    def test_post_gust_template(self):
        """Проврека страницы и соответсвующий шаблон"""
        """для неавторизир пользователей"""
        template_name = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': StaticURLTests.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': StaticURLTests.post.id}
            ): 'posts/post_detail.html',
        }
        for address, template in template_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_auth_template(self):
        """Проврека страницы и соответсвующий шаблон
         для авторизир пользователей"""
        template_name = {

            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': StaticURLTests.post.id}
            ): 'posts/create_post.html',

        }
        for address, template in template_name.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)
