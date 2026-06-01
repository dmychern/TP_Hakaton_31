import pytest
from src.__main__ import build_parser

def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])

    assert args.inbox == "data/inbox"
    assert args.out == "data"
    assert args.config == "config/categories.json"
    assert args.reports == "reports"
    assert args.copy is False

def test_parser_custom():
    parser = build_parser()
    args = parser.parse_args(["--inbox", "test_inbox", "--out", "test_out", "--copy"])

    assert args.inbox == "test_inbox"
    assert args.out == "test_out"
    assert args.copy is True