import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormCreateTests(TestCase):
    """Тестим формы в приложении Posts."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.groups = [Group(
            title=f'Тестовая группа {i}',
            slug=f'test-slag-{i}',
            description=f'Тестовое описание - {i}'
        ) for i in range(2)]
        Group.objects.bulk_create(cls.groups)
        cls.group = Group.objects.get(id=settings.TEST_GROUP_INDEX)
        cls.second_group = Group.objects.get(
            id=settings.TEST_SECOND_GROUP_INDEX
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

    def test_post_create_valid_form_create_post(self):
        """Проверяем, что валидная форма создает пост."""
        post_count_before_creation = Post.objects.count()
        form_create_data = {
            'text': 'Тестовый текст,заданый в форме',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_create_data, follow=True
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK.value
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,)
            )
        )
        post_count_after_creation = post_count_before_creation + 1
        self.assertEqual(Post.objects.count(), post_count_after_creation)
        created_post = Post.objects.first()
        created_post_values_expected_values = {
            created_post.text: 'Тестовый текст,заданый в форме',
            created_post.author: User.objects.get(id=created_post.author.id),
            created_post.group: Group.objects.get(
                id=settings.TEST_GROUP_INDEX
            ),
            created_post.image: f'posts/{self.uploaded}'
        }
        for (
            created_post_value, expected_value
        ) in created_post_values_expected_values.items():
            with self.subTest(created_post_value=created_post_value):
                self.assertEqual(created_post_value, expected_value)

    def test_post_create_guest_client_cant_create_post(self):
        """Неавторизованный пользователь при попытке создания редиректится
        на страницу логина, пост не создается."""
        post_count_before_creation = Post.objects.count()
        form_create_data = {
            'text': 'Тестовый текст,заданый в форме',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_create_data,
            follow=True,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK.value
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={reverse("posts:post_create")}',
        )
        self.assertEqual(Post.objects.count(), post_count_before_creation)

    def test_post_edit_valid_form_edit_post(self):
        """Проверяем, что валидная форма изменяет пост, не создавая нового."""
        post_count_before_edits = Post.objects.count()
        text_before_edits = Post.objects.get(id=self.post.id).text
        author_before_edits = Post.objects.get(id=self.post.id).author
        group_before_edits = Post.objects.get(id=self.post.id).group
        image_before_edits = Post.objects.get(id=self.post.id).image
        form_edit_data = {
            'text': 'Новый тестовый текст',
            'group': self.second_group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_edit_data,
            follow=True,
        )
        text_after_edits = Post.objects.get(id=self.post.id).text
        author_after_edits = Post.objects.get(id=self.post.id).author
        group_after_edits = Post.objects.get(id=self.post.id).group
        image_after_edits = Post.objects.get(id=self.post.id).image
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.pk,)),
        )
        self.assertNotEqual(text_before_edits, text_after_edits)
        self.assertEqual(author_before_edits, author_after_edits)
        self.assertNotEqual(group_before_edits, group_after_edits)
        self.assertNotEqual(image_before_edits, image_after_edits)
        self.assertEqual(post_count_before_edits, Post.objects.count())

    def test_post_edit_guest_client_cant_edit_post(self):
        """Неавторизованный пользователь не может редактировать пост,
        редирект на страницу входа."""
        post_count_before_edits = Post.objects.count()
        text_before_edits = Post.objects.get(id=self.post.id).text
        author_before_edits = Post.objects.get(id=self.post.id).author
        group_before_edits = Post.objects.get(id=self.post.id).group
        image_before_edits = Post.objects.get(id=self.post.id).image
        form_edit_data = {
            'text': 'Новый тестовый текст',
            'group': self.second_group.id,
            'image': self.uploaded,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_edit_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertRedirects(
            response,
            (
                f'{reverse("users:login")}?next='
                f'{reverse("posts:post_edit", args=(self.post.pk,))}'
            ),
        )
        self.assertEqual(Post.objects.count(), post_count_before_edits)
        text_after_edits = Post.objects.get(id=self.post.id).text
        author_after_edits = Post.objects.get(id=self.post.id).author
        group_after_edits = Post.objects.get(id=self.post.id).group
        image_after_edits = Post.objects.get(id=self.post.id).image
        self.assertEqual(text_before_edits, text_after_edits)
        self.assertEqual(author_before_edits, author_after_edits)
        self.assertEqual(group_before_edits, group_after_edits)
        self.assertEqual(image_before_edits, image_after_edits)

    def test_comment_form_add_new_comment(self):
        """Проверяем, в валидной форме создания комменария
        авторизированный пользователь добавляет новый комментарий к посту,
        гость редиректится на страницу входа, коммент не добавляется."""
        comment_count = Comment.objects.filter(post=self.post).count()
        form_comment_data = {
            'text': 'Тестовый текст,заданый в форме',
        }
        if self.guest_client:
            response = self.guest_client.post(
                reverse('posts:add_comment', args=(self.post.pk,)),
                data=form_comment_data,
                follow=True,
            )
            self.assertEqual(
                response.status_code,
                HTTPStatus.OK.value,
            )
            self.assertRedirects(
                response,
                f'{reverse("users:login")}?next='
                f'{reverse("posts:add_comment", args=(self.post.pk,))}'
            )
            self.assertEqual(
                Comment.objects.filter(post=self.post).count(),
                comment_count,
            )
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_comment_data,
            follow=True,
        )
        comment_count += 1
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK.value,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(self.post.pk,)
            ),
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(),
            comment_count,
        )
