from notes.forms import NoteForm
from .base_test import HOME_URL, EDIT_NOTE_URL, BaseTestCase, ADD_NOTE_URL


class TestNoteViews(BaseTestCase):
    def test_add_note_view_has_form(self):
        """
        Проверяет, что на странице создания заметки для
        авторизованного пользователя передаётся форма.
        """
        self.assertIn(
            'form',
            self.author_client.get(ADD_NOTE_URL).context
        )
        self.assertIsInstance(
            self.author_client.get(ADD_NOTE_URL).context['form'],
            NoteForm
        )

    def test_edit_note_view_has_form_for_author(self):
        """
        Проверяет, что на странице редактирования заметки для
        автора передаётся форма.
        """
        self.assertIn(
            'form',
            self.author_client.get(EDIT_NOTE_URL).context
        )
        self.assertIsInstance(
            self.author_client.get(EDIT_NOTE_URL).context['form'],
            NoteForm
        )

    def test_author_note_list_contains_note(self):
        """
        Проверяет, что заметка автора присутствует в списке заметок на
        главной странице и её поля передаются корректно.
        """
        notes = self.author_client.get(HOME_URL).context['object_list']
        self.assertIn(self.note, notes)
        test_note = notes.get(pk=self.note.pk)
        self.assert_note_fields_equal(
            test_note,
            {
                'title': self.note.title,
                'text': self.note.text,
                'slug': self.note.slug,
                'author': self.note.author,
            }
        )

    def test_non_author_note_list_does_not_contain_note(self):
        """
        Проверяет, что заметка автора не попадает в список заметок для
        другого пользователя.
        """
        self.assertEqual(
            self.not_author_client.get(
                HOME_URL
            ).context['object_list'].count(),
            0
        )

    def test_add_note_view_no_form_for_unauthenticated(self):
        """
        Проверяет, что незалогиненный пользователь не получает форму на
        странице создания заметки.
        """
        response = self.client.get(ADD_NOTE_URL)
        self.assertNotIn(
            'form',
            response.context if response.context else {}
        )

    def test_edit_note_view_no_form_for_unauthenticated(self):
        """
        Проверяет, что незалогиненный пользователь не получает форму на
        странице редактирования заметки.
        """
        response = self.client.get(EDIT_NOTE_URL)
        self.assertNotIn(
            'form',
            response.context if response.context else {}
        )
