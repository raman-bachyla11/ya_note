import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='TestAuthor')
        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'test{index}',
                author=cls.author
            )
            # no pagination
            for index in range(settings.NOTES_COUNT_ON_HOME_PAGE)
        )

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, settings.NOTES_COUNT_ON_HOME_PAGE)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_IDs = [note.id for note in object_list]
        sorted_dates = sorted(all_IDs)
        self.assertEqual(all_IDs, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='АвторЗаметки')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
            slug=uuid.uuid4().hex
        )
        cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
