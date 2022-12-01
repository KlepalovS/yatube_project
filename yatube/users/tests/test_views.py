from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from ..forms import CreationForm

User = get_user_model()


class UsersViewTest(TestCase):
    """Тестим View в приложении Users."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_uses_correct_templates(self):
        """Проверяем, что reverse(namespace:name)
        использует правильный шаблон"""
        reverse_page_names_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': urlsafe_base64_decode(
                        urlsafe_base64_encode(
                            force_bytes(self.user.pk)
                        )).decode(),
                    'token': default_token_generator.check_token(
                        self.user,
                        default_token_generator.make_token(self.user))
                }
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        for reverse_page, template in reverse_page_names_templates.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertTemplateUsed(response, template)

    def test_signup_page_correct_context(self):
        """Проверяем, что на страницу signup передана
        форма создания нового пользователя."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected_value in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected_value)
        self.assertIsInstance(
            response.context.get('form'),
            CreationForm,
        )
