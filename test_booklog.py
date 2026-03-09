import pytest
from unittest.mock import MagicMock, patch

from camera_isbn import normalize_isbn
from booklog_auto_add import add_book_by_isbn


# --- normalize_isbn tests ---

class TestNormalizeIsbn:
    def test_converts_isbn10_to_isbn13(self):
        # ISBN-10 "4003101014" -> ISBN-13 "9784003101018"
        assert normalize_isbn("4003101014") == "9784003101018"

    def test_returns_none_for_invalid_isbn(self):
        assert normalize_isbn("12345") is None
        assert normalize_isbn("") is None
        assert normalize_isbn("abc") is None


# --- add_book_by_isbn tests ---

class TestAddBookByIsbn:
    def _make_page(self, *, add_btn=None, first_item=None, add_btn_after_click=None):
        """Build a mock Playwright page.

        Args:
            add_btn: element returned for the add-to-shelf selector on first call.
            first_item: element returned for the item-title selector.
            add_btn_after_click: element returned for add-to-shelf after clicking
                the first item (second query_selector call with that selector).
        """
        page = MagicMock()
        page.goto = MagicMock()
        page.fill = MagicMock()
        page.click = MagicMock()
        page.wait_for_load_state = MagicMock()
        page.wait_for_timeout = MagicMock()

        add_shelf_selector = (
            "a.add-to-shelf, button.add-to-shelf, "
            "a[data-add-shelf], button[data-add-shelf]"
        )
        item_selector = "a.item-title, a[href*='/items/'], div.item a"

        # Track successive calls to query_selector per selector
        add_shelf_calls = iter(
            [add_btn] if add_btn_after_click is None else [add_btn, add_btn_after_click]
        )

        def query_selector_side_effect(sel):
            if sel == add_shelf_selector:
                return next(add_shelf_calls, None)
            if sel == item_selector:
                return first_item
            return None

        page.query_selector = MagicMock(side_effect=query_selector_side_effect)
        return page

    @patch("booklog_auto_add.time")
    def test_add_book_directly_with_add_to_shelf_button(self, mock_time):
        btn = MagicMock()
        page = self._make_page(add_btn=btn)

        result = add_book_by_isbn(page, "9784003101018")

        assert result is True
        btn.click.assert_called_once()

    @patch("booklog_auto_add.time")
    def test_add_book_after_clicking_first_item(self, mock_time):
        first_item = MagicMock()
        btn = MagicMock()
        page = self._make_page(
            add_btn=None, first_item=first_item, add_btn_after_click=btn
        )

        result = add_book_by_isbn(page, "9784003101018")

        assert result is True
        first_item.click.assert_called_once()
        btn.click.assert_called_once()

    @patch("booklog_auto_add.time")
    def test_returns_false_when_no_button_or_item(self, mock_time):
        page = self._make_page(add_btn=None, first_item=None)

        result = add_book_by_isbn(page, "9784003101018")

        assert result is False
