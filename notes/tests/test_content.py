from notes.forms import NoteForm
from .base_test import NOTE_LIST_URL, EDIT_NOTE_URL, BaseTestCase, ADD_NOTE_URL


class TestNoteViews(BaseTestCase):
    def test_views_has_form_for_author(self):
        """
        Проверяет, что на страницах создания и редактирования заметки
        для автора передаётся форма NoteForm.
        """
        urls = (ADD_NOTE_URL, EDIT_NOTE_URL)
        for url in urls:
            with self.subTest(url=url):
                self.assertIn(
                    'form',
                    self.author_client.get(url).context
                )
                self.assertIsInstance(
                    self.author_client.get(url).context['form'],
                    NoteForm
                )

    def test_author_note_list_contains_note(self):
        """
        Проверяет, что заметка автора присутствует в списке заметок на
        главной странице и её поля передаются корректно.
        """
        notes = self.author_client.get(NOTE_LIST_URL).context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_non_author_note_list_does_not_contain_note(self):
        """
        Проверяет, что заметка автора не попадает в список заметок
        для другого пользователя.
        """
        self.assertNotIn(
            self.note,
            self.not_author_client.get(NOTE_LIST_URL).context['object_list']
        )
