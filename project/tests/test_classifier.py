import pytest
import json
from src.classifier import RuleBasedClassifier
from src.reader import EmailMessage

@pytest.fixture
def temporary_config(tmp_path):
    config_data = {
        "unknown_folder": "unrecognized",
        "empty_folder": "blank",
        "categories": [
            {
                "name": "critical",
                "folder": "urgent",
                "priority": 10,
                "keywords": ["сбой", "ошибка"],
                "patterns": [r"упал\s+сервер"]
            },
            {
                "name": "access",
                "folder": "requests",
                "priority": 5,
                "keywords": ["пароль", "вход"],
                "patterns": []
            },
            {
                "name": "access_high_priority",
                "folder": "request_urgent",
                "priority": 20,
                "keywords": ["пароль"],
                "patterns": []
            },
        ]
    }
    config_file = tmp_path / "test_categories.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return config_file

@pytest.fixture
def test_classifier(temporary_config):
    return RuleBasedClassifier(temporary_config)

def test_prepare_text(test_classifier):
    text = "Ёё   ёё\n\nАааа"
    assert test_classifier.prepare_text(text) == "ее ее аааа"

@pytest.mark.parametrize("text, word, expected", [
    ("ааасбойаааа", "сбой", True),
    ("ааа сбойааа", "сбой", False),
    ("пароль от аааа", "пароль от", True)
])
def test_has_word(test_classifier, text, word, expected):
    assert test_classifier.has_word(text, word) is expected

@pytest.mark.parametrize("subject, body, expected_category, expected_folder", [
    ("Срочно", "Упал сервер и сбой", "critical", "urgent"),
    ("Письмо стандартное", "Ничего важное", "unknown", "unrecognized"),
    ("", "   ", "empty", "blank")
])
def test_classify_one_base(test_classifier, subject, body, expected_category, expected_folder):
    message = EmailMessage("mail_0000.txt", subject, body)
    result = test_classifier.classify_one(message)

    assert result.category == expected_category
    assert result.folder == expected_folder

def test_classify_one_priority(test_classifier):
    message = EmailMessage("mail_0000.txt", "Доступ", "Забыл пароль")
    result = test_classifier.classify_one(message)

    assert result.category == "access_high_priority"
    assert result.folder == "request_urgent"


    