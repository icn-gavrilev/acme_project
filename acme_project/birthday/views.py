# birthday/views.py
from django.views.generic import (
    CreateView, DeleteView,
    DetailView, ListView,
    UpdateView
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
# Нужна для проверки аутентификации при создании записи
from django.contrib.auth.mixins import LoginRequiredMixin
# Для проверки аутентификации при добавления комментариев
from django.contrib.auth.decorators import login_required
# Миксин для тестирования автора и проверки аутентификации.
# Следовательно предыдущий миксин для проверки аутентификации не нужен
# в таких операциях как редактирование и удаление записи.
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown


class OnlyAuthorMixin(UserPassesTestMixin):
    # Определяем метод test_fund() для миксина UserPAssesTestMixin:
    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return object.author == self.request.user


class BirthdayListView(ListView):
    model = Birthday
    # По умолчанию это класс
    # выполняет запрос queryset = Birthday.objects.all(),
    # но мы его переопределим:
    queryset = Birthday.objects.prefetch_related(
        'tags'
        ).select_related('author')
    ordering = 'id'
    paginate_by = 10


class BirthdayCreateView(
    LoginRequiredMixin,
    CreateView
):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить пою author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayUpdateView(
    # LoginRequiredMixin,
    OnlyAuthorMixin,
    UpdateView
):
    model = Birthday
    form_class = BirthdayForm


class BirthdayDeleteView(
    # LoginRequiredMixin,
    OnlyAuthorMixin,
    DeleteView
):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой обхект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Допольнительно подгружаем авторов комментариев,
            # чтобы избежать множесвта запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context


class CongratulationCreateView(
    LoginRequiredMixin,     # Для проверки аутентификации
    CreateView              # Инициализатор записи
):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        ''' Метод dispatch() выполняется ближе к началу обработки запроса
(полный порядок обработки запроса есть в документации
(https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#view)); он
провеяет, что в базе есть объект дня рожедния с переданным в заросе pk.
Если объект есть - он будет присвоен атрибуту self/birthday,
если же объекта нет - будет выброшена ошибка 404. '''
        self.birthday = get_object_or_404(
            Birthday,
            pk=kwargs['pk']
        )
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        ''' В методе form_valid() полям author и birthday нового
объекта присваиваетются значения. Такую опреацию вы уже описывали в CBV
BirthdayCreateView - там автор присваивается новому объекту Birthday. '''
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        ''' После отправки формы с поздварелнием надо перенаправить
пользователя на страницу записи. Это делается с помощью метода
get_success_url(). В нём применяется функция reverse(), которая из имени
маршрута и нужных аргументов собирает строку с адресом; это аналог тега
{% url "birthday:detail" pk %}, но только в Python-коде.'''
        return reverse(
            'birthday:detail',
            kwargs={
                'pk': self.birthday.pk
            }
        )

# @login_required
# def add_comment(request, pk):
#     # Получаем объект дня рождения или выбрасываем 404 ощибку.
#     birthday = get_object_or_404(Birthday, pk=pk)
#     # Функция должна обрабатывать только POST-запросы.
#     form = CongratulationForm(request.POST)
#     if form.is_valid():
#         # Создаём объект поздравления, но не сохраняем его в БД.
#         congratulation = form.save(commit=False)
#         # В поле author передаём объект автора поздравления.
#         congratulation.author = request.user
#         # В поле birthday передаём объекь дня рождения.
#         congratulation.birthday = birthday
#         # Сохраняем объект в БД.
#         congratulation.save()
#     # Перенапрвляем пользователя назад, на страницу дня рождения.
#     return redirect('birthday:detail', pk=pk)

# @login_required
# def simple_view(request):
#     return HttpResponse('Страница для залогиненных пользователей!')
# # from django.shortcuts import (
# #     render,
# #     get_object_or_404,
# #     redirect
# # )
# from .forms import BirthdayForm
# from .utils import calculate_birthday_countdown
# from .models import Birthday

# # Импортируем класс пагинатора
# # from django.core.paginator import Paginator

# # Импортируем наследуемый класс для создания класса списка объектов
# from django.views.generic import (
#     CreateView,
#     DeleteView,
#     DetailView,
#     ListView,
#     UpdateView
# )

# from django.urls import reverse_lazy


# class BirthdayMixin:
#     model = Birthday
#     success_url = reverse_lazy('birthday:list')


# class BirthdayFormMixin:
#     form_class = BirthdayForm
#     template_name = 'birthday/birthday.html'


# class BirthdayCreateView(BirthdayMixin, BirthdayFormMixin, CreateView):
#     pass


# class BirthdayUpdateView(BirthdayMixin, BirthdayFormMixin, UpdateView):
#     pass


# class BirthdayDeleteView(BirthdayMixin, DeleteView):
#     pass


# # birthday/views.py
# class BirthdayDetailView(DetailView):
#     model = Birthday

#     def get_context_data(self, **kwargs):
#         # Получаем словарь контекста:
#         context = super().get_context_data(**kwargs)
#         # Добавляем в словарь новый ключ:
#         context['birthday_countdown'] = calculate_birthday_countdown(
#             # Дату рождения берём из объекта в словаре context:
#             self.object.birthday
#         )
#         # Возвращаем словарь контекста.
#         return context


# # Наследуем класс от встроенного ListView:
# class BirthdayListView(ListView):
#     # Указываем модель, с которой работает CBV...
#     model = Birthday
#     # ...сортировку, которая будет применена при вывода списка объектов:
#     ordering = 'id'
#     # ... и даже настройки пагинации
#     paginate_by = 10


# # class BirthdayUpdateView(UpdateView):
# #     model = Birthday
# #     form_class = BirthdayForm
# #     template_name = 'birthday/birthday.html'
# #     success_url = reverse_lazy('birthday:list')


# # class BirthdayCreateView(CreateView):
# #     # Указываем модель, с которой работает CBV...
# #     model = Birthday
# #     # Этот класс сам может создать форму на основе модели!
# #     # Нет необходимости отдельно создавать форму через ModelForm.
# #     # Указываем поля, которые должны быть в форме:
# #     form_class = BirthdayForm
# #     # fields = '__all__'
# #     # Явным образом укащываем шаблон:
# #     template_name = 'birthday/birthday.html'
# #     # Укаызваем namespace:name страницы, куда будет перенаправлен пользователь
# #     # после создания объекта:
# #     success_url = reverse_lazy('birthday:list')

# # def delete_birthday(request, pk):
# #     # Получаем объект модели или выбрасываем 404 ошибку.
# #     instance = get_object_or_404(Birthday, pk=pk)
# #     # В форму передаём только объект модели;
# #     # передавать в форму параметры запроса не нужно.
# #     form = BirthdayForm(instance=instance)
# #     context = {
# #         'form': form
# #     }
# #     # Если был получен POST-запрос...
# #     if request.method == 'POST':
# #         # ... удаляем запрос:
# #         instance.delete()
# #         # ... и переадресовываем пользователя на страницу со списком записей.
# #         return redirect('birthday:list')
# #     # Если был получен GET-запрос - отображаем форму.
# #     return render(
# #         request,
# #         'birthday/birthday.html',
# #         context
# #     )


# # def edit_birthday(request, pk):
# #     # Находим запрошенный объект для редактирования по первичному ключу
# #     # или возвращаем 404 ошибку, если такогго объекта нет.
# #     instance = get_object_or_404(Birthday, pk=pk)
# #     # Связываем форму с найденными объектом: передаём его в аргумент instance.
# #     form = BirthdayForm(request.POST or None, instance=instance)
# #     # Всё остальное без изменений.
# #     context = {
# #         'form': form
# #     }
# #     # Сохраняем данные, полученные из формы, и отправляем ответ:
# #     if form.is_valid():
# #         form.save()
# #         birthday_countdown = calculate_birthday_countdown(
# #             form.cleaned_data['birthday']
# #         )
# #         context.update(
# #             {
# #                 'birtday_coutndown': birthday_countdown
# #             }
# #         )
# #     return render(
# #         request,
# #         'birthday/birthday.html',
# #         context
# #     )


# # def birthday(request, pk=None):
# #     # if request.GET:
# #     #     form = BirthdayForm(request.GET)
# #     #     if form.is_valid():
# #     #         pass
# #     # else:
# #     #     form = BirthdayForm()

# #     # Если в запросе указан pk (если получен запрос на редактирование объекта):
# #     # Получаем бъект модели или выбрасываем 404 ошибку.
# #     # Если в запросе не указан pk:
# #     # Связывать форму с объектом не нужно, установим значение None.
# #     instance = get_object_or_404(Birthday, pk=pk) if pk is not None else None
# #     # Передаём в форму либо данные из запроса, либо None.
# #     # В случае редактирования прикрепляем объект модели.
# #     form = BirthdayForm(
# #         request.POST or None,
# #         # файлы, переданные в запросе, указываются отдельно.
# #         files=request.FILES or None,
# #         instance=instance)
# #     context = {
# #         'form': form
# #     }
# #     if form.is_valid():
# #         form.save()
# #         birthday_countdown = calculate_birthday_countdown(
# #             form.cleaned_data['birthday']
# #         )
# #         context.update(
# #             {
# #                 'birthday_countdown': birthday_countdown
# #             }
# #         )
# #     return render(
# #         request,
# #         'birthday/birthday.html',
# #         context=context
# #     )


# # def birthday_list(request):
# #     # birthdays = Birthday.objects.all()

# #     # Получаем список всех объектов с сортировкой по id.
# #     birthdays = Birthday.objects.order_by('id')

# #     # Создаём объект пагинатора с кол-вом 10 записей на страницу
# #     paginator = Paginator(birthdays, 10)

# #     # Получаем из запроса значение параметра page. Номер страницы.
# #     page_number = request.GET.get('page')

# #     # Получаем запрошенную страницу пагинатора.
# #     # Если параметр page нет в запросе или его занчение не приводится к числу,
# #     # то вернётся первая страницу.
# #     page_obj = paginator.get_page(page_number)

# #     # Вместо полного списка объектов передаём в контекст
# #     # объект страницы пагинатора.
# #     context = {
# #         'page_obj': page_obj
# #     }

# #     # context = {
# #     #     'birthdays': birthdays
# #     # }

# #     return render(
# #         request,
# #         'birthday/birthday_list.html',
# #         context)
