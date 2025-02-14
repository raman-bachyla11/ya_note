import uuid
from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class BaseNoteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='TestAuthor')
        cls.not_author = User.objects.create(username='NotAuthor')
        cls.url_success = reverse('notes:success')

    def get_client(self, user):
        """Return a new Client instance logged in as the given user."""
        client = Client()
        client.force_login(user)
        return client

    def post_note_form(self, client, url, data, follow=False):
        """Helper to post form data to the given URL."""
        return client.post(url, data=data, follow=follow)


class TestSlugNaming(BaseNoteTestCase):
    VALID_SLUG = uuid.uuid4().hex

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='TestNote',
            text='TestText',
            slug=cls.VALID_SLUG,
            author=cls.author
        )
        cls.url_note_add = reverse('notes:add')
        cls.url_note_list = reverse('notes:list')
        cls.form_data = {
            'title': 'New Note',
            'text': 'New Text',
            'slug': uuid.uuid4().hex,
        }

    def setUp(self):
        # Set up an authenticated client for the author
        self.auth_client = self.get_client(self.author)

    def test_note_with_valid_slug(self):
        response = self.post_note_form(self.auth_client, self.url_note_add, self.form_data)
        self.assertRedirects(response, self.url_success)

    def test_slug_must_be_unique(self):
        response = self.post_note_form(self.auth_client, self.url_note_add, {'slug': self.VALID_SLUG})
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=f'{self.VALID_SLUG}{WARNING}'
        )

    def test_empty_slug_is_allowed(self):
        data_with_empty_slug = {
            'title': 'new_title',
            'text': 'Some text',
            'slug': ''
        }
        response = self.post_note_form(self.auth_client, self.url_note_add, data_with_empty_slug)
        self.assertRedirects(response, self.url_success)

        note = Note.objects.get(title='new_title')
        expected_slug = slugify('new_title')
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(BaseNoteTestCase):
    VALID_SLUG = uuid.uuid4().hex
    UPDATED_TITLE = 'Updated title'
    UPDATED_TEXT = 'Updated text'
    ORIGINAL_TEST_TITLE = 'TestTitle'
    ORIGINAL_TEST_TEXT = 'TestText'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=cls.ORIGINAL_TEST_TITLE,
            text=cls.ORIGINAL_TEST_TEXT,
            slug=cls.VALID_SLUG,
            author=cls.author
        )
        cls.edited_form_data = {
            'title': cls.UPDATED_TITLE,
            'text': cls.UPDATED_TEXT,
            'slug': cls.note.slug
        }
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete_note = reverse('notes:delete', args=(cls.note.slug,))

    def setUp(self):
        self.auth_client = self.get_client(self.author)
        self.unauth_client = self.get_client(self.not_author)

    def test_author_edit_note(self):
        response = self.post_note_form(self.auth_client, self.url_edit_note, self.edited_form_data, follow=True)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.UPDATED_TITLE)
        self.assertEqual(self.note.text, self.UPDATED_TEXT)

    def test_not_author_cant_edit_note(self):
        response = self.post_note_form(self.unauth_client, self.url_edit_note, self.edited_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.ORIGINAL_TEST_TITLE)
        self.assertEqual(self.note.text, self.ORIGINAL_TEST_TEXT)

    def test_note_deletable_by_author(self):
        response = self.auth_client.delete(self.url_delete_note)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_author_cant_delete_note(self):
        response = self.unauth_client.delete(self.url_delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
