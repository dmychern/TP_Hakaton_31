import pytest
from src.reader import EmailMessage

@pytest.fixture
def message_example():
    return EmailMessage("mail_0000.txt", "Тема", "Текст письма")

def test_message_init(message_example):
    assert message_example.filename == "mail_0000.txt"
    assert message_example.subject == "Тема"
    assert message_example.body == "Текст письма"

@pytest.mark.parametrize("subject, body, expected", [
    ("КАПС", "не капс", "капс не капс"),
    ("КАПС", "КАПС", "капс капс"),
    ("", "текст", " текст"),
    ("тема", "", "тема ")
])

def test_message_get_text(subject, body, expected):
    message = EmailMessage("mail_0000.txt", subject, body)
    
    assert message.get_full_text() == expected
