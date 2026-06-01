import pytest
import json
from pathlib import Path
from src.__main__ import build_parser, main

def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])

    assert args.inbox == "data/inbox"
    assert args.out == "data"
    assert args.config == "config/categories.json"
    assert args.reports == "reports"
    assert args.copy is False
    assert args.dry_run is False

def test_parser_custom():
    parser = build_parser()
    args = parser.parse_args(["--inbox", "test_inbox", "--copy"])

    assert args.inbox == "test_inbox"
    assert args.copy is True

@pytest.fixture
def setup_env(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    out = tmp_path / "out"
    reports = tmp_path / "reports"
    log = tmp_path / "logs" / "app.log"
    config = tmp_path / "categories.json"

    config_data = {
        "unknown_folder": "unknown",
        "empty_folder": "empty",
        "categories": [
            {
                "name": "critical",
                "folder": "urgent",
                "priority": 10,
                "keywords": ["сбой"],
                "patterns": []
            }
        ]
    }
    
    with open(config, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
        
    msg_file = inbox / "test_msg.txt"
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write("у нас сбой системы")
        
    return {
        "inbox": str(inbox),
        "out": str(out),
        "reports": str(reports),
        "config": str(config),
        "log": str(log)
    }

def test_main_process(setup_env):
    args = [
        "--inbox", setup_env["inbox"],
        "--out", setup_env["out"],
        "--config", setup_env["config"],
        "--reports", setup_env["reports"],
        "--log-file", setup_env["log"]
    ]
    
    result = main(args)
    
    assert result == 0
    
    expected_file = Path(setup_env["out"]) / "urgent" / "test_msg.txt"
    assert expected_file.exists()
    
    report_file = Path(setup_env["reports"]) / "reports.json"
    assert report_file.exists()
    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)
    assert report["total"] == 1
    assert report["distribution"]["critical"] == 1


def test_main_dry_run(setup_env):
    args = [
        "--inbox", setup_env["inbox"],
        "--out", setup_env["out"],
        "--config", setup_env["config"],
        "--reports", setup_env["reports"],
        "--log-file", setup_env["log"],
        "--dry-run"
    ]

    result = main(args)

    assert result == 0
    assert (Path(setup_env["inbox"]) / "test_msg.txt").exists()
    assert not (Path(setup_env["out"]) / "urgent" / "test_msg.txt").exists()
    assert (Path(setup_env["reports"]) / "reports.json").exists()


def test_main_copy(setup_env):
    args = [
        "--inbox", setup_env["inbox"],
        "--out", setup_env["out"],
        "--config", setup_env["config"],
        "--reports", setup_env["reports"],
        "--log-file", setup_env["log"],
        "--copy"
    ]

    result = main(args)

    assert result == 0
    assert (Path(setup_env["out"]) / "urgent" / "test_msg.txt").exists()
    assert (Path(setup_env["inbox"]) / "test_msg.txt").exists()


def test_main_unknown_category(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    out = tmp_path / "out"
    reports = tmp_path / "reports"
    log = tmp_path / "logs" / "app.log"
    config = tmp_path / "categories.json"

    config_data = {
        "unknown_folder": "unknown",
        "empty_folder": "empty",
        "categories": []
    }

    with open(config, "w", encoding="utf-8") as f:
        json.dump(config_data, f)

    msg_file = inbox / "test_msg.txt"
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write("текст без ключевых слов")

    args = [
        "--inbox", str(inbox),
        "--out", str(out),
        "--config", str(config),
        "--reports", str(reports),
        "--log-file", str(log)
    ]

    result = main(args)

    assert result == 0
    assert (out / "unknown" / "test_msg.txt").exists()
    with open(reports / "reports.json", "r", encoding="utf-8") as f:
        report = json.load(f)
    assert report["total"] == 1
    assert report["distribution"]["unknown"] == 1

def test_main_empty_inbox(tmp_path):
    args = [
        "--inbox", str(tmp_path / "not_exist")
    ]
    
    result = main(args)
    
    assert result == 1