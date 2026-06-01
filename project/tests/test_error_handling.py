import json
import shutil
from pathlib import Path
import pytest
from src.classifier import RuleBasedClassifier
from src.processor import MailProcessor

@pytest.fixture
def basic_config(tmp_path):
    config = tmp_path / "categories.json"
    data = {
        "unknown_folder": "unknown",
        "empty_folder": "empty",
        "categories": []
    }
    config.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(config)

def test_blocked_extension(tmp_path, basic_config):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    img = inbox / "photo.jpg"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")

    processor = MailProcessor(
        inbox_dir=str(inbox),
        outbox_dir=str(tmp_path / "out"),
        classifier=RuleBasedClassifier(Path(basic_config)),
        report_dir=str(tmp_path / "reports")
    )

    msg = processor._read_one(img)
    
    assert getattr(msg, "blocked", False) is True
    assert msg.subject == ""
    assert msg.body == ""

def test_unreadable_text_file(tmp_path, basic_config, monkeypatch):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    bad = inbox / "bad.txt"
    bad.write_text("some content", encoding="utf-8")

    original_read_text = Path.read_text

    def raise_oserror(self, encoding=None):
        if self == bad:
            raise OSError()
        return original_read_text(self, encoding=encoding)

    monkeypatch.setattr(Path, "read_text", raise_oserror)

    processor = MailProcessor(
        inbox_dir=str(inbox),
        outbox_dir=str(tmp_path / "out"),
        classifier=RuleBasedClassifier(Path(basic_config)),
        report_dir=str(tmp_path / "reports")
    )

    msg = processor._read_one(bad)
    
    assert getattr(msg, "blocked", False) is True

def test_move_permission_error(tmp_path, basic_config, monkeypatch):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    msgf = inbox / "mail.txt"
    msgf.write_text("Subject: hi\n\nhello", encoding="utf-8")

    classifier = RuleBasedClassifier(Path(basic_config))
    processor = MailProcessor(
        inbox_dir=str(inbox), 
        outbox_dir=str(out),
        classifier=classifier, 
        report_dir=str(tmp_path / "reports")
    )

    def fake_move(src, dst, *args, **kwargs):
        raise PermissionError()

    monkeypatch.setattr(shutil, "move", fake_move)

    results = processor.process()
    
    assert len(results) == 1
    assert getattr(results[0], "error", None) is not None