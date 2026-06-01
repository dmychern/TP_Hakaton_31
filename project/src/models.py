class EmailMessage:
    def __init__(self, filename: str, subject: str, body: str):
        self.filename = filename
        self.subject = subject
        self.body = body

    def get_full_text(self) -> str:
        return f"{self.subject} {self.body}".lower()