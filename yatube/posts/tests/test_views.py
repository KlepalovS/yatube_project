import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm

from ..models import Comment, Follow, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
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
            id=settings.TEST_SECOND_GROUP_INDEX,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.posts = [Post(
            text=f'Тестовый текст {i}',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        ) for i in range(settings.POSTS_IN_PAGE)]
        Post.objects.bulk_create(cls.posts)
        cls.post = Post.objects.get(id=settings.TEST_POST_INDEX)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_post_pages_uses_correct_templates(self):
        """Проверяем, что reverse(namespace:name)
        использует правильный шаблон"""
        reverse_page_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', args=(self.post.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=(self.post.author.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=(self.post.pk,)
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ): 'posts/create_post.html',
        }
        for reverse_name, template in reverse_page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_test(self, test_post):
        """Результат проверки поста на соответствие ожидаемому."""
        post_atributes = {
            test_post.text: self.post.text,
            test_post.author: self.user,
            test_post.group: self.group,
            test_post.image: f'posts/{self.uploaded}'
        }
        for value, expected_value in post_atributes.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected_value)

    def test_index_group_list_profile_post_detail_with_correct_context(self):
        """Проверяем, что передаем правильный контекст на страницы
        posts:index, posts:group_list, posts:profile, posts:post_detail."""
        pages_reverse = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.post.group.slug,)),
            reverse('posts:profile', args=(self.post.author.username,)),
            reverse('posts:post_detail', args=(self.post.pk,)),
        )
        for reverse_page in pages_reverse:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                if reverse_page != reverse(
                    'posts:post_detail', args=(self.post.pk,)
                ):
                    test_post = response.context.get(
                        'page_obj'
                    )[settings.TEST_POST_INDEX]
                    self.post_test(test_post)
                    self.assertEqual(
                        len(response.context.get('page_obj')),
                        settings.POSTS_IN_PAGE,
                    )
                else:
                    test_post = response.context.get('post')
                    self.post_test(test_post)

    def test_post_edit_with_correct_context(self):
        """Проверяем контекст формы редактирования поста."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)
        ))
        form_fields = {
            'text': self.post.text,
            'group': self.post.group.id,
            'image': self.post.image,
        }
        for value, expected_value in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].initial[value]
                self.assertEqual(form_field, expected_value)
        self.assertEqual(response.context.get('form').instance, self.post)
        self.assertIsInstance(response.context['is_edit'], bool)
        self.assertTrue(response.context['is_edit'])

    def test_post_create_with_correct_context(self):
        """Проверяем контекст формы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected_value in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected_value)
        self.assertIsInstance(
            response.context.get('form'),
            PostForm,
        )
        is_edit = bool(response.context.get('is_edit'))
        self.assertFalse(is_edit)

    def test_post_with_group_show_correct_in_index_profile_groups_pages(self):
        """Проверяем, что, если посту задать группу,
        он корректно отображается на страницах index, profile, group_list."""
        pages_reverse = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.post.group.slug,)),
            reverse('posts:profile', args=(self.post.author.username,)),
        )
        for reverse_page_name in pages_reverse:
            with self.subTest(reverse_page_name=reverse_page_name):
                response = self.authorized_client.get(reverse_page_name)
                self.assertIn(self.post, response.context.get('page_obj'))

    def test_post_with_group_dont_show_in_other_group(self):
        """Проверяем, что пост с группой не отображается в другой группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.second_group.slug,))
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_post_comment_correct_show_in_post_detail(self):
        """Проверяем, что комментарии к посту отображаются на
        странице post_detail."""
        form_comment_data = {
            'text': 'Тестовый текст,заданый в форме',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_comment_data,
            follow=True,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.pk,))
        )
        comment = Comment.objects.get(post=self.post)
        self.assertIn(comment, response.context['comments'])

    def test_post_index_cache_correct_working(self):
        """Проверяем работу кэша на странице index."""
        response_first = self.authorized_client.get(
            reverse('posts:index')
        )
        post = Post.objects.get(pk=settings.TEST_POST_INDEX)
        post.text = 'Измененный текст'
        post.save()
        response_second = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response_first.content, response_second.content)
        cache.clear()
        response_third = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response_first.content, response_third.content)

    def test_following_working_correct(self):
        """Проверяем, что подписка работает правильно."""
        author = User.objects.create_user(username='test_user_author')
        user = self.user
        follow_count_before_following = Follow.objects.filter(
            author=author,
            user=user,
        ).count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', args=(author.username,)
        ))
        follow_count_after_following = Follow.objects.filter(
            author=author,
            user=user,
        ).count()
        self.assertNotEqual(
            follow_count_before_following,
            follow_count_after_following,
        )

    def test_unfollowing_working_correct(self):
        """Проверяем, что отписка работает правильно."""
        author = User.objects.create_user(username='test_user_author')
        user = self.user
        self.authorized_client.get(reverse(
            'posts:profile_follow', args=(author.username,)
        ))
        follow_count_after_following = Follow.objects.filter(
            author=author,
            user=user,
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', args=(author.username,)
        ))
        follow_count_after_unfollowing = Follow.objects.filter(
            author=author,
            user=user,
        )
        self.assertNotEqual(
            follow_count_after_following,
            follow_count_after_unfollowing,
        )

    def test_post_correct_show_on_followers(self):
        """Проверяем, что пост отображается только у подписанных пользователей
        и не отображается у тех, кто не подписан на автора."""
        user_follower = User.objects.create_user(username='follower')
        authorized_user_follower = Client()
        authorized_user_follower.force_login(user_follower)
        response_user_follower_before_following = authorized_user_follower.get(
            reverse('posts:follow_index'),
        )
        self.assertNotIn(
            self.post,
            response_user_follower_before_following.context['page_obj'],
        )
        authorized_user_follower.get(reverse(
            'posts:profile_follow',
            args=(self.user.username,),
        ))
        response_user_follower_after_following = authorized_user_follower.get(
            reverse('posts:follow_index'),
        )
        self.assertIn(
            self.post,
            response_user_follower_after_following.context['page_obj'],
        )

    def test_post_dont_show_on_not_follower(self):
        """Проверяем, что новый пост не отображается
        у неподписанного пользователя."""
        user_not_follower = User.objects.create_user(username='not_follower')
        authorized_user_not_follower = Client()
        authorized_user_not_follower.force_login(user_not_follower)
        test_post = Post.objects.create(
            author=self.user,
        )
        response_user_not_follower = authorized_user_not_follower.get(
            reverse('posts:follow_index'),
        )
        self.assertNotIn(
            test_post,
            response_user_not_follower.context['page_obj'],
        )
        self.assertFalse(
            Follow.objects.filter(
                user=user_not_follower,
                author=self.user,
            ).exists()
        )

