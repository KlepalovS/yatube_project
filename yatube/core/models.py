from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляем дату создания."""
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta():
        abstract = True
