from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
POSTS_IN_TEST_PAGINATOR = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [Post(
            text=f'Тестовый текст {i}',
            author=cls.user,
            group=cls.group,
        ) for i in range(POSTS_IN_TEST_PAGINATOR)]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_in_paginator_contains_correct_records(self):
        """Проверка количества постов на странице в пагинаторе."""
        reverse_pages_sums_of_posts = {
            reverse('posts:index'): settings.POSTS_PER_PAGE,
            reverse('posts:index') + '?page=2': (
                POSTS_IN_TEST_PAGINATOR - settings.POSTS_PER_PAGE
            ),
            reverse(
                'posts:group_list', args=(self.group.slug,)
            ): settings.POSTS_PER_PAGE,
            reverse(
                'posts:group_list', args=(self.group.slug,)
            ) + '?page=2': (
                POSTS_IN_TEST_PAGINATOR - settings.POSTS_PER_PAGE
            ),
            reverse(
                'posts:profile', args=(self.user.username,)
            ): settings.POSTS_PER_PAGE,
            reverse(
                'posts:profile', args=(self.user.username,)
            ) + '?page=2': (
                POSTS_IN_TEST_PAGINATOR - settings.POSTS_PER_PAGE
            ),
        }
        for reverse_page, sum_of_post in reverse_pages_sums_of_posts.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertEqual(
                    len(response.context['page_obj']), sum_of_post
                )
