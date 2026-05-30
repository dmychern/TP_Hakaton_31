class EmailMessage:
    def __init__(self, filename: str, suject: str, body: str):
        self.filename = filename
        self.subject = suject
        self.body = body

    def get_full_text(selfself) -> str:
        return f"{self.subject} {self.body}".lower()