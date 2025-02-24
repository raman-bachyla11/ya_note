from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .base_test import (
    ADD_NOTE_URL,
    BaseTestCase,
    DELETE_NOTE_URL,
    EDIT_NOTE_URL,
    SUCCESS_URL
)


class TestNoteManagement(BaseTestCase):
    """
    Тестирование создания, редактирования и удаления заметок,
    включая проверку уникальности/генерации слага.
    """

    def test_note_with_valid_slug(self):
        """Проверка создания заметки с валидными слагом."""
        response = self.assert_note_count_change(
            1,
            self.author_client.post,
            ADD_NOTE_URL,
            self.get_valid_data()
        )
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(title=self.get_valid_data()['title'])
        self.assert_note_fields_equal(note, {
            'title': self.get_valid_data()['title'],
            'text': self.get_valid_data()['text'],
            'slug': self.get_valid_data()['slug'],
            'author': self.author
        })

    def test_slug_must_be_unique(self):
        """
        Проверка уникальности слага заметки.
        При попытке создать заметку с уже существующим слагом
        должно выводиться сообщение об ошибке.
        """
        duplicated_slug_data = self.get_valid_data(
            title='Another Note',
            text='Another text',
            slug=self.note.slug,
        )
        initial_note_count = Note.objects.count()
        response = self.author_client.post(ADD_NOTE_URL, duplicated_slug_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.note.slug}{WARNING}'
        )
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_empty_slug_is_allowed(self):
        """
        Проверка допуска пустого слага.
        Если слаг не указан, он генерируется автоматически
        на основе названия заметки.
        """
        form_data_without_slug = self.get_valid_data()
        form_data_without_slug.pop('slug', None)
        response = self.assert_note_count_change(
            1,
            self.author_client.post,
            ADD_NOTE_URL,
            form_data_without_slug
        )
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(title=form_data_without_slug['title'])
        expected_slug = slugify(form_data_without_slug['title'])
        expected_data = {
            'title': form_data_without_slug['title'],
            'text': form_data_without_slug['text'],
            'slug': expected_slug,
            'author': self.author
        }
        self.assert_note_fields_equal(note, expected_data)

    def test_author_edit_note(self):
        """Проверка возможности редактирования заметки автором."""
        edited_data = self.get_valid_data(
            title='Edited Title',
            text='Edited Text',
            slug='edited-slug'
        )
        response = self.author_client.post(EDIT_NOTE_URL, edited_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_fields_equal(updated_note, {
            'title': edited_data['title'],
            'text': edited_data['text'],
            'slug': edited_data['slug'],
            'author': self.author
        })

    def test_not_author_cant_edit_note(self):
        """
        Проверка невозможности редактирования заметки пользователем,
        не являющимся автором.
        Данные заметки не должны изменяться, и возвращается ошибка 404.
        """
        original_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author,
        }
        edited_data = self.get_valid_data(
            title='Edited Title',
            text='Edited Text',
            slug='edited-slug'
        )
        response = self.not_author_client.post(EDIT_NOTE_URL, edited_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        unchanged_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_fields_equal(unchanged_note, original_data)

    def test_note_deletable_by_author(self):
        """Проверка возможности удаления заметки автором."""
        initial_count = Note.objects.count()
        response = self.author_client.delete(DELETE_NOTE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_not_author_cant_delete_note(self):
        """
        Проверка невозможности удаления заметки пользователем,
        не являющимся автором. Количество заметок остается неизменным.
        """
        initial_count = Note.objects.count()
        response = self.not_author_client.delete(DELETE_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        note = Note.objects.get(pk=self.note.pk)
        original_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author,
        }
        self.assert_note_fields_equal(note, original_data)
