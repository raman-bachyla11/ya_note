# test_content.py
import pytest

from django.urls import reverse

from notes.forms import NoteForm


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, note_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_notes_list_for_different_users(
        # Используем фикстуру заметки и параметры из декоратора:
        note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)
