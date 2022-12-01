from django.test import TestCase

from ..models import ADMINS_POST_LENGHT, Group, Post, User


class PostModelTest(TestCase):
    """Тестируем модели в приложении posts."""

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

    def test_models_post_group_have_correct_object_name(self):
        """Проверяем, что у моделей Post, Group
        правильно работает __str__."""
        info_expected_info = {
            (
                self.post.text[:ADMINS_POST_LENGHT] + '...'
                if len(self.post.text) >= ADMINS_POST_LENGHT
                else self.post.text
            ): str(self.post),
            self.group.title: str(self.group),
        }
        for info, expected_info in info_expected_info.items():
            with self.subTest(info=info):
                self.assertEqual(info, expected_info)

    def test_post_verbose_name(self):
        """Проверяем, что у модели Post verbose_name
        в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_group_verbose_name(self):
        """Проверяем, что у модели Post verbose_name
        в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Имя',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_help_text(self):
        """Проверяем, что у модели Post
        help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку, если желаете',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
