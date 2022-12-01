from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания нового поста."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Напишите пост, не стесняйтесь 🙂'
        )
        self.fields['group'].empty_label = (
            'А здесь можно выбрать группу'
        )

    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image',
        )
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картика к посту',
        }


class CommentForm(forms.ModelForm):
    """Форма создания нового комментария."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Напишите коммент, не стесняйтесь 😉'
        )

    class Meta:
        model = Comment
        fields = (
            'text',
        )
        labels = {
            'text': 'Текст коммента',
        }
