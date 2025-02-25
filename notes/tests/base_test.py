from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

# Константные данные
NOTE_SLUG = 'note-slug'

# URL для пользователей
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')

# URL для заметок
HOME_URL = reverse('notes:list')
EDIT_NOTE_URL = reverse('notes:edit', args=[NOTE_SLUG])
NOTE_DETAIL_URL = reverse('notes:detail', args=[NOTE_SLUG])
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
NOTE_LIST_URL = reverse('notes:list')
DELETE_NOTE_URL = reverse('notes:delete', args=[NOTE_SLUG])

# Ожидаемые редиректы
EDIT_NOTE_REDIRECT = f'{LOGIN_URL}?next={EDIT_NOTE_URL}'
NOTE_DETAIL_REDIRECT = f'{LOGIN_URL}?next={NOTE_DETAIL_URL}'
DELETE_NOTE_REDIRECT = f'{LOGIN_URL}?next={DELETE_NOTE_URL}'


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
            slug=NOTE_SLUG
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        # Валидные данные для заметки
        cls.VALID_NOTE_DATA = {
            'title': 'Valid Title',
            'text': 'Valid Text',
            'slug': 'valid-slug'
        }
