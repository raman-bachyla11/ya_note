from http import HTTPStatus

from .base_test import (
    BaseTestCase,
    DELETE_NOTE_URL,
    EDIT_NOTE_URL,
    HOME_URL,
    LOGIN_URL,
    LOGOUT_URL,
    NOTE_DETAIL_URL,
    SIGNUP_URL,
    EDIT_NOTE_REDIRECT,
    NOTE_DETAIL_REDIRECT,
    DELETE_NOTE_REDIRECT
)


class TestRoutes(BaseTestCase):
    """
    Тестирование маршрутов приложения.
    Содержит тесты для проверки корректности кодов возврата и перенаправлений.
    """

    def test_status_codes(self):
        """Проверка всех кодов возврата с различными клиентами."""
        cases = (
            # Общедоступные страницы
            (HOME_URL, self.client, HTTPStatus.FOUND),
            (EDIT_NOTE_URL, self.client, HTTPStatus.FOUND),
            (NOTE_DETAIL_URL, self.client, HTTPStatus.FOUND),
            (DELETE_NOTE_URL, self.client, HTTPStatus.FOUND),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            # Маршруты заметок для автора
            (EDIT_NOTE_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (DELETE_NOTE_URL, self.author_client, HTTPStatus.OK),
            # Маршруты заметок для не-автора
            (EDIT_NOTE_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (NOTE_DETAIL_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (DELETE_NOTE_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for url, client, expected_status in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirects_for_anonymous_client(self):
        """
        Проверка перенаправлений для анонимного клиента при попытке
        доступа к защищённым маршрутам.
        """
        protected_urls = (
            (EDIT_NOTE_URL, EDIT_NOTE_REDIRECT),
            (NOTE_DETAIL_URL, NOTE_DETAIL_REDIRECT),
            (DELETE_NOTE_URL, DELETE_NOTE_REDIRECT),
        )
        for url, expected_redirect in protected_urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), expected_redirect)
