from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import real_age
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    tag = models.CharField('Тег', max_length=20)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.tag


class Birthday(models.Model):
    first_name = models.CharField(
        'Имя',
        max_length=20
    )

    last_name = models.CharField(
        'Фамилия',
        blank=True,  # параметр отвечающий за "необязательность"
        help_text='Необязательное поле',
        max_length=20
    )

    birthday = models.DateField(
        'Дата рождения',
        validators=(
            real_age,
        )
    )

    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='birthday_images'
    )

    author = models.ForeignKey(
        User, verbose_name='Автор записи',
        on_delete=models.CASCADE, null=True
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'first_name',
                    'last_name',
                    'birthday'
                ),
                name='Unique person constraints',
            ),
        )
        verbose_name = 'день рождения',
        verbose_name_plural = 'Дни рождения'

    def get_absolute_url(self):
        return reverse("birthday:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Congratulation(models.Model):
    text = models.TextField('Текст подздравления')
    birthday = models.ForeignKey(
        Birthday,
        on_delete=models.CASCADE,
        related_name='congratulations',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'поздравление',
        verbose_name_plural = 'Поздравления',
        ordering = (
            'created_at',
        )

    def __str__(self):
        return 'Для ' + str(self.birthday) + ' от ' + str(self.author) 

    # Если валидатор привязан к модели
    #  — валидация будет срабатывать
    # и при управлении данными через формы в админке.

    # price = models.IntegerField(
    #     validators=[
    #         MinValueValidator(10),
    #         MaxValueValidator(100),
    #     ],
    #     help_text = 'тут типо какой доп. текст для пояснений'
    # )
