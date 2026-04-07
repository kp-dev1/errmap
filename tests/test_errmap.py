import sys
import json
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


def test_save_to_json_before_error_warns(capsys):
    errmap = ErrMap()
    errmap.save_to_json("tmp.json")
    captured = capsys.readouterr()
    assert "No errors to save" in captured.out


def test_save_to_json_saves_valid_json(tmp_path, capsys):
    errmap = ErrMap()
    errmap.install()
    
    try:
        raise ValueError("test error")
    except ValueError:
        etype, value, tb = sys.exc_info()
        errmap._draw_tree(etype, value, tb)
    
    filepath = tmp_path / "error.json"
    errmap.save_to_json(str(filepath))
    
    with open(filepath) as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["error_type"] == "ValueError"
    assert data[0]["error_message"] == "test error"
    assert isinstance(data[0]["call_tree"], list)
    assert len(data[0]["call_tree"]) > 0


def test_save_to_json_saves_multiple_errors(tmp_path, capsys):
    errmap = ErrMap()
    errmap.install()
    
    try:
        raise ValueError("first error")
    except ValueError:
        etype, value, tb = sys.exc_info()
        errmap._draw_tree(etype, value, tb)
    
    try:
        raise RuntimeError("second error")
    except RuntimeError:
        etype, value, tb = sys.exc_info()
        errmap._draw_tree(etype, value, tb)
    
    filepath = tmp_path / "errors.json"
    errmap.save_to_json(str(filepath))
    
    with open(filepath) as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0]["error_type"] == "ValueError"
    assert data[1]["error_type"] == "RuntimeError"


def test_save_to_json_call_tree_structure(tmp_path, capsys):
    errmap = ErrMap()
    errmap.install()
    
    try:
        raise RuntimeError("nested error")
    except RuntimeError:
        etype, value, tb = sys.exc_info()
        errmap._draw_tree(etype, value, tb)
    
    filepath = tmp_path / "error.json"
    errmap.save_to_json(str(filepath))
    
    with open(filepath) as f:
        data = json.load(f)
    
    for frame in data[0]["call_tree"]:
        assert "name" in frame
        assert "line" in frame
        assert "code" in frame
        assert "is_error_frame" in frame
    
    assert data[0]["call_tree"][-1]["is_error_frame"] is True


def test_save_to_json_not_stored_when_inactive(capsys):
    errmap = ErrMap()
    errmap.install()
    errmap.active = False
    
    try:
        raise ValueError("test")
    except ValueError:
        etype, value, tb = sys.exc_info()
        sys.excepthook(etype, value, tb)
    
    assert len(errmap._errors) == 0
    
    errmap.save_to_json("tmp.json")
    captured = capsys.readouterr()
    assert "No errors to save" in captured.out
