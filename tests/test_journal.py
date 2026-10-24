from __future__ import annotations

from aiu.journal import check_append_only


def test_no_head_content_is_allowed() -> None:
    assert check_append_only(None, "anything\n") is True


def test_appended_content_is_allowed() -> None:
    old = "## Entry 0\n- a\n"
    new = old + "\n## Entry 1\n- b\n"
    assert check_append_only(old, new) is True


def test_edited_middle_is_rejected() -> None:
    old = "## Entry 0\n- a\n## Entry 1\n- b\n"
    new = "## Entry 0\n- changed\n## Entry 1\n- b\n"
    assert check_append_only(old, new) is False


def test_crlf_and_lf_only_is_allowed() -> None:
    old = "## Entry 0\r\n- a\r\n"
    new = "## Entry 0\n- a\n\n## Entry 1\n- b\n"
    assert check_append_only(old, new) is True
