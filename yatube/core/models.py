from django.db import models

class CreatModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created=models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True