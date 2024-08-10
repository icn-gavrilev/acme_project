from django import forms
from .models import Birthday, Congratulation
from django.core.exceptions import ValidationError
from django.core.mail import send_mail


BEATLES = {
    'Джон Леннон', 'Пол Маккарти',
    'Джордж Харрисон', 'Ринго Старр'
    }


# class BirthdayForm(forms.Form):
class BirthdayForm(forms.ModelForm):

    class Meta:
        model = Birthday
        exclude = ('author',)
        fields = '__all__'
        widgets = {
            'birthday': forms.DateInput(attrs={
                'type': 'date'
            })
        }

    def clean_first_name(self):
        # Получаем значение имени из словаря очищенных данных.
        first_name = self.cleaned_data['first_name']
        # Разбиваем полученную строку по пробелам
        # и возвращаем только первое имя.
        return first_name.split()[0]

    def clean(self):
        # Получаем имя и фамилию из очищенных полей формы
        super().clean()
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        # Проверяем вхождение сочетания имени и фамилии во множество имён.
        if f'{first_name} {last_name}' in BEATLES:
            # Отправляем письмо, если кто-то представляется
            # именем одного из участников бить лесбух.
            send_mail(
                subject='Another Beatles member',
                message=f'{first_name} {last_name} пытался опубликовать запись!',
                from_email='birthday_form@acme.not',
                recipient_list=['admin@acme.not'],
                fail_silently=True,
            )
            raise ValidationError(
                'Я не люблю бить лэсбух. Так шоо... ИДИ НА ХУЙ!'
            )


class CongratulationForm(forms.ModelForm):

    class Meta:
        model = Congratulation
        fields = ('text',)

    # first_name = forms.CharField(
    #     label='Имя', max_length=20
    # )

    # last_name = forms.CharField(
    #     label='Фамилия', required=False,
    #     help_text='Необязательное поле'
    # )

    # birthday = forms.DateField(
    #     label='Дата рождения',
    #     widget=forms.DateInput(
    #         attrs={
    #             'type': 'date'
    #         }
    #     )
    # )

    # description = forms.CharField(
    #     label='Описание',
    #     widget=forms.Textarea()
    # )

    # price = forms.IntegerField(
    #     label='Цена',
    #     min_value=10,
    #     max_value=100,
    #     help_text='Рекомендованная розничная цена'
    # )
