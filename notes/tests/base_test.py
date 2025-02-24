from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

# Константные данные
TEST_NOTE_SLUG = 'test-note-slug'

# URL для пользователей
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')

# URL для заметок
HOME_URL = reverse('notes:list')
EDIT_NOTE_URL = reverse('notes:edit', args=[TEST_NOTE_SLUG])
NOTE_DETAIL_URL = reverse('notes:detail', args=[TEST_NOTE_SLUG])
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
NOTE_LIST_URL = reverse('notes:list')
DELETE_NOTE_URL = reverse('notes:delete', args=[TEST_NOTE_SLUG])


class BaseTestCase(TestCase):
    """Базовый класс для тестирования с преднастройкой данных и клиентов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='TestAuthor')
        cls.not_author = User.objects.create(username='NotAuthor')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
            slug=TEST_NOTE_SLUG
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

    def get_expected_redirect(self, url):
        """Возвращает ожидаемый URL перенаправления для анонимного клиента."""
        return f'{LOGIN_URL}?next={url}'

    def get_valid_data(self, **kwargs):
        """
        Генерирует базовый словарь данных для создания
        и редактирования заметки.
        """
        data = {
            'title': 'Valid Title',
            'text': 'Valid Text',
            'slug': 'valid-slug'
        }
        data.update(kwargs)
        return data

    def assert_note_count_change(self, delta, callable_obj, *args, **kwargs):
        """
        Проверяет изменение количества заметок на delta.
        Возвращает результат вызова callable_obj.
        """
        initial_count = Note.objects.count()
        response = callable_obj(*args, **kwargs)
        self.assertEqual(Note.objects.count() - initial_count, delta)
        return response

    def assert_note_fields_equal(self, note, expected_data):
        """Проверяет предметные поля заметки: title, text, slug, author."""
        self.assertEqual(note.title, expected_data.get('title'))
        self.assertEqual(note.text, expected_data.get('text'))
        self.assertEqual(note.slug, expected_data.get('slug'))
        self.assertEqual(note.author, expected_data.get('author'))
