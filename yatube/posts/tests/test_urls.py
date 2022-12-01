from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_not_author = User.objects.create_user(
            username='test_user_not_author'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_post_urls_status_code_authorized(self):
        """Проверяем доступность страниц для авторизированного пользователя."""
        url_names_status_code = {
            '/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK.value,
            f'/group/{self.post.group.slug}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for adress, status_code in url_names_status_code.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, status_code)

    def test_post_urls_status_code_guest_client(self):
        """Проверяем доступность страниц неавторизированному пользователю."""
        url_names_status_code = {
            '/': HTTPStatus.OK.value,
            f'/profile/{self.post.author}/': HTTPStatus.OK.value,
            f'/group/{self.post.group.slug}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND.value,
            '/create/': HTTPStatus.FOUND.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for adress, status_code in url_names_status_code.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status_code)

    def test_post_urls_redirect_guest_client_on_auth_login(self):
        """Проверяем, что страницы /posts/<post_id>/edit/ и /create/
        перенаправляют неавторизированного пользователя
        на страницу авторизации."""
        url_names_redirect_urls = {
            f'/posts/{self.post.id}/edit/': (
                f'/auth/login/?next=/posts/{self.post.id}/edit/'
            ),
            '/create/': '/auth/login/?next=/create/',
        }
        for adress, redirect_adress in url_names_redirect_urls.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect_adress)

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        """Проверяем редикрект не автора поста со страницы редактирования
        на инфо о посте."""
        not_author_client = Client()
        not_author_client.force_login(self.user_not_author)
        response = not_author_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/',
        )

    def test_post_urls_uses_correct_templates(self):
        """Тестируем соответствие страниц в приложении posts
        соответствующим шаблонам."""
        url_names_templates = {
            '/': 'posts/index.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in url_names_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
