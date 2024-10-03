from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

class TestRoutes(TestCase):

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
    
    def test_availabily_for_note_detail_edit_and_delete(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code,status)



    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
   
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            ('notes:success', None),
        )
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name, args in urls:
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления тария:
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)