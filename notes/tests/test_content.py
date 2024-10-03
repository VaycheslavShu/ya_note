from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from datetime import datetime, timedelta

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()



class TestHomePage(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )
        
        cls.list_url = reverse('notes:list')

    
    def test_notes_in_context(self):
        # Загружаем главную страницу.
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Проверяем наличие заметки в списке заметок
        self.assertIn(self.notes, object_list)
    
    def test_notes_user_in_list(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)
   
      
    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,))
        )
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        #self.assertIsInstance(response.context['form'], NoteForm)