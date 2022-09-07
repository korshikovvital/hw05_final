from django.test import TestCase
from ..models import Post, Group,User

class TestModelPosts(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = TestModelPosts.post
        self.assertEqual(task.text, str(task))

        group = TestModelPosts.group
        self.assertEqual(group.title, str(group))

    def test_posts_verbose(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = TestModelPosts.post
        field_verbose = {
            'text': 'текст',
            'group': 'Выберите группу',
        }
        for field, verbose in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, verbose
                )

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = TestModelPosts.post
        field_verbose = {
            'text': 'Заполните это поле',
            'group': 'Не обязательное поле',
        }
        for field, help_text in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, help_text
                )
