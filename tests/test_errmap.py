import sys
import pytest
from errmap import ErrMap


def test_install_replaces_excepthook():
    errmap = ErrMap()
    errmap.install()
    assert sys.excepthook != sys.__excepthook__


def test_active_default_true():
    errmap = ErrMap()
    assert errmap.active is True


def test_active_can_be_disabled():
    errmap = ErrMap()
    errmap.active = False
    assert errmap.active is False


def test_install_uses_default_when_inactive(capsys):
    errmap = ErrMap()
    errmap.install()
    errmap.active = False
    try:
        raise ValueError("test")
    except ValueError:
        etype, value, tb = sys.exc_info()
        sys.excepthook(etype, value, tb)
    captured = capsys.readouterr()
    assert "[ERR-MAP]" not in captured.out


def test_draw_tree_output(capsys):
    errmap = ErrMap()
    errmap.install()
    try:
        raise ZeroDivisionError("division by zero")
    except ZeroDivisionError:
        etype, value, tb = sys.exc_info()
        errmap._draw_tree(etype, value, tb)
    captured = capsys.readouterr()
    assert "[ERR-MAP]" in captured.out
    assert "ZeroDivisionError" in captured.out


def test_branch_and_vertical_defaults():
    errmap = ErrMap()
    assert errmap.branch == " └── "
    assert errmap.vertical == " │   "
