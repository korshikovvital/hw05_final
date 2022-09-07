from django.test import TestCase, Client
from ..models import Group, Post, User
from django.urls import reverse
from http import HTTPStatus


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
        cls.guest_client = Client()

        cls.post = Post.objects.create(
            text='Test post',
            author=StaticURLTests.author,
            group=StaticURLTests.group
        )

        cls.template_auth_client = {

            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': StaticURLTests.post.id}
            ): 'posts/create_post.html',

        }
        cls.template_guest_client = {
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

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_get_status_page_auth_client(self):
        """Проверка доступности страниц для авториз пользователей"""

        for address in StaticURLTests.template_auth_client:
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_status_page_guest_client(self):
        """Проверка доступности страниц для неавториз пользователей"""

        for address in self.template_guest_client:
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_404(self):
        """Проврека к несуществующей странице 404
        и нужного шаблона"""

        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_post_gust_template(self):
        """Проврека страницы и соответсвующий шаблон"""
        """для неавторизир пользователей"""

        for address, template in self.template_guest_client.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_auth_template(self):
        """Проврека страницы и соответсвующий шаблон
         для авторизир пользователей"""

        for address, template in self.template_auth_client.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)
