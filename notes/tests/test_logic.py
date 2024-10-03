from django.conf import settings
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from datetime import datetime, timedelta

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING, NoteForm

User = get_user_model()


class TestLogicCase(TestCase):
    EDIT_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        
        
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.author)
        #Создаём объект.
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note1',
            author=cls.author
        )
        cls.form_note = {
            'title':'Заголовок2',
            'text':'Текст2',
            'slug':'note1'
        }
        
        cls.form_slug_note = {
            'title':'Заголовок2',
            'text':'Текст2',
            'slug':'note1'
        }
        
        cls.notes_count = Note.objects.count()
        
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.detail_url = reverse('notes:detail',args=(cls.notes.slug,))
        cls.succes_url = reverse('notes:success', None)
        
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_text = {'text':cls.EDIT_TEXT}

    def test_user_create_note(self):
        user_client = (self.author_client, self.client)
        for client in user_client:
            with self.subTest(client=client):
                client.post(self.add_url, title='Заголовок2', text=self.form_text, slug='note1')
                note_count = Note.objects.count()
                self.assertEqual(note_count, self.notes_count)

    # def test_slug_note(self):
    #     self.author_client.post(self.url_add, data=self.form_note)
    #     self.author_client.post(self.url_add, data=self.slug_note)
    #     note_add_count = Note.objects.count()
    #     self.assertEqual(note_add_count, self.notes_count)
    def test_slug_note(self):
        
        self.author_client.post(self.add_url, data=self.form_note)
        self.author_client.post(self.add_url, data=self.form_slug_note)
        note_count_after_edit = Note.objects.count()
        self.assertEqual( note_count_after_edit, self.notes_count)

    def test_note_slug_is_generated(self):
        notes = Note.objects.all()
        notes.delete()
        data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
        }
        slug = slugify(data['title'])
        response = self.author_client.post(self.add_url, data=data)
        self.assertRedirects(response, self.succes_url)
        note = Note.objects.get()
        self.assertEqual(note.slug, slug)
        
    def test_author__delete_note(self):
        response = self.author_client.delete(self.delete_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_anonymous_delete_note(self):
        response = self.client.delete(self.delete_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_count)

    def test_another_user_not_edit_note(self):
        edit_txt = {'text':'Новый текст'}
        response = self.reader_client.post(self.edit_url, data=edit_txt)
        self.notes.refresh_from_db()
        self.assertNotEqual(self.notes.text, self.form_text)
