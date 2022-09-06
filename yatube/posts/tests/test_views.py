from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Group, Post, Follow
from django import forms
from django.core.cache import cache

User = get_user_model()


class TestViews(TestCase):
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
            author=TestViews.author,
            group=TestViews.group
        )
        cls.follow = Follow.objects.create(
            user=cls.author,
            author=cls.post.author
        )

    def test_index_cache(self):
        """Тест кэширование главной страницы"""
        post_new = Post.objects.create(
            text='cache_text',
            author=TestViews.author,
            group=TestViews.group
        )
        response = self.auth_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]

        self.assertEqual(first_post.text, post_new.text)
        post_new.delete()
        cache.clear()
        response = self.auth_client.get(reverse('posts:index'))
        self.assertNotEqual(post_new.text, response.content)

    def test_vies_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': TestViews.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': TestViews.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': TestViews.post.id}
            ): 'posts/create_post.html',

        }

        for address, template in templates_pages_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_correct_context(self):
        """Шаблон index  сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.text, TestViews.post.text
        )
        self.assertEqual(
            first_post.author, TestViews.post.author
        )
        self.assertEqual(
            first_post.group, TestViews.post.group
        )
        self.assertEqual(
            first_post.image, TestViews.post.image
        )

    def test_post_group_list_page_correct_context(self):
        """Шаблон group_list  сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_group = response.context['group']
        self.assertEqual(
            first_group.title, TestViews.group.title
        )
        self.assertEqual(
            first_group.slug, TestViews.group.slug
        )
        self.assertEqual(
            first_group.description, TestViews.group.description
        )

        first_post = response.context['page_obj'][0]

        self.assertEqual(
            first_post.image, TestViews.post.image
        )

    def test_post_profile_page_correct_context(self):
        """Шаблон profile  сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': TestViews.author})
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.text, TestViews.post.text
        )
        self.assertEqual(
            first_post.author, TestViews.post.author
        )
        self.assertEqual(
            first_post.group, TestViews.post.group
        )
        self.assertEqual(
            first_post.image, TestViews.post.image
        )

    def test_post_post_detail_page_correct_context(self):
        """Шаблон post_detail  сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': TestViews.post.id})
        )

        self.assertEqual(
            response.context.get('posts').text, TestViews.post.text
        )
        self.assertEqual(
            response.context.get('posts').author, TestViews.post.author
        )
        self.assertEqual(
            response.context.get('posts').group, TestViews.post.group
        )
        self.assertEqual(
            response.context.get('posts').image, TestViews.post.image
        )

    form_fields = {
        'text': forms.fields.CharField,
        'group': forms.fields.ChoiceField,
    }

    def test_post_post_create_page_correct_context(self):
        """Шаблон  post_create  сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:post_create')
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_post_edit_page_correct_context(self):
        """Шаблон  post_edit сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': TestViews.post.id})
        )

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertTrue(response.context['is_edit'])

    def test_follow_unfollow(self):
        follow_count = Follow.objects.count()
        new_post = Post.objects.create(
            text='New post',
            author=TestViews.author,
        )
        self.auth_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TestViews.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0], new_post)

        self.auth_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestViews.author}
        )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response.context['page_obj'], new_post)


class TestPaginatorViews(TestCase):

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
        posts = [
            Post(
                text=f'Test post{post_num}',
                author=TestPaginatorViews.author,
                group=TestPaginatorViews.group,
            )
            for post_num in range(1, 14)
        ]

        Post.objects.bulk_create(posts)

    def test_first_page_contains_ten_records(self):
        """Проверка количества постов на первой странице"""
        url_name = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile', kwargs={'username': TestPaginatorViews.author}
            )
        ]
        for url in url_name:
            response = self.auth_client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        """Проверка количества постов на второй странице"""
        url_name = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile', kwargs={'username': TestPaginatorViews.author}
            )
        ]
        for url in url_name:
            response = self.auth_client.get(url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
