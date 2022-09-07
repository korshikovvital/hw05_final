import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from ..models import Post, Group, Comment, User
from django.urls import reverse
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='name_title',
            slug='slug-test',
            description='descrip_test'
        )
        cls.author = User.objects.create(username='korshikov')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.post = Post.objects.create(
            text='text_test',
            author=PostCreateFormTest.author,
            group=PostCreateFormTest.group
        )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """При отправке валидной формы создается новый post"""

        post_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'test_title',
            'group': PostCreateFormTest.group.id,
            'image': uploaded,
        }

        PostCreateFormTest.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True

        )

        self.assertEqual(
            Post.objects.count(), post_count + 1
        )

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif',
            ).exists()
        )

    def test_post_edit(self):
        """При отправке валидной формы создается  post_edit"""

        # form_data = {
        #     'text': 'test_title',
        #     'group': PostCreateFormTest.group.id,
        #     'image': self.small_gif
        # }
        #
        # response = PostCreateFormTest.auth_client.post(
        #     reverse(
        #         'posts:post_edit', kwargs={
        #             'post_id': PostCreateFormTest.post.id
        #         }
        #     ),
        #     data=form_data,
        #     follow=True
        # )
        #
        # self.assertRedirects(
        #     response, reverse(
        #         'posts:post_detail', kwargs={
        #             'post_id': PostCreateFormTest.post.id
        #         }
        #     )
        # )
        # self.assertTrue(
        #     Post.objects.filter(
        #         text='test_title',
        #         group=PostCreateFormTest.group.id
        #     ).exists()
        # )
        new_post_text = 'new text'
        new_group = Group.objects.create(
            title='name_title2',
            slug='slug-test2',
            description='descrip_test2'
        )
        form_data = {
            'text': new_post_text,
            'group': new_group.id,
        }

        PostCreateFormTest.auth_client.post(
            reverse('posts:post_edit', args=(PostCreateFormTest.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

    def test_add_comment(self):
        """При отправке валидной формы создается add_comment,
        для авториз рользователей"""

        form_data = {
            'text': 'text_test',
        }
        comment_count = Comment.objects.count()

        response = PostCreateFormTest.auth_client.post(
            reverse(
                'posts:add_comment', kwargs={
                    'post_id': PostCreateFormTest.post.id
                }),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostCreateFormTest.post.id
                }
            )
        )

        self.assertEqual(Comment.objects.count(), comment_count + 1)

        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text']
            ).exists()
        )
