from http import HTTPStatus

from pytils.translit import slugify

from .base_test import (
    ADD_NOTE_URL,
    BaseTestCase,
    DELETE_NOTE_URL,
    EDIT_NOTE_URL,
    SUCCESS_URL
)
from notes.forms import WARNING
from notes.models import Note


class TestNoteManagement(BaseTestCase):
    """
    Тестирование создания, редактирования и удаления заметок,
    включая проверку уникальности/генерации слага.
    """

    def test_authorized_client_can_create_note_with_valid_slug(self):
        """Проверка создания заметки с валидным слагом."""
        self.assert_note_created_with_expected_slug(
            expected_slug=self.note_data['slug'])

    def test_duplicated_slug_is_not_allowed(self):
        """
        Проверка уникальности слага заметки.
        При попытке создать заметку с уже существующим слагом
        должно выводиться сообщение об ошибке,
        а состав записей в таблице не изменяется.
        """
        self.note_data['slug'] = self.note.slug
        notes_before = list(Note.objects.order_by('pk'))
        response = self.author_client.post(ADD_NOTE_URL, self.note_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.note.slug}{WARNING}'
        )
        notes_after = list(Note.objects.order_by('pk'))
        self.assertEqual(notes_after, notes_before)

    def test_auto_generate_slug_when_absent(self):
        """
        Проверка автоматической генерации слага, если он не указан.
        Если слаг отсутствует, он генерируется автоматически
        на основе названия заметки.
        """
        del self.note_data['slug']
        self.assert_note_created_with_expected_slug(
            expected_slug=slugify(self.note_data['title']))

    def test_author_edit_note(self):
        """Проверка возможности редактирования заметки автором."""
        response = self.author_client.post(EDIT_NOTE_URL, self.note_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.note_data['title'])
        self.assertEqual(updated_note.text, self.note_data['text'])
        self.assertEqual(updated_note.slug, self.note_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_not_author_cant_edit_note(self):
        """
        Проверка невозможности редактирования заметки пользователем,
        не являющимся автором.
        Данные заметки не должны изменяться, и возвращается ошибка 404.
        """
        self.assertEqual(
            self.not_author_client.post(
                EDIT_NOTE_URL, self.note_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        unchanged_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)

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
        не являющимся автором. Количество заметок остаётся неизменным.
        """
        notes_before = list(Note.objects.order_by('pk'))
        self.assertEqual(
            self.not_author_client.delete(DELETE_NOTE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        notes_after = list(Note.objects.order_by('pk'))
        self.assertEqual(notes_after, notes_before)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
