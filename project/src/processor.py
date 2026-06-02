import shutil
import logging
import json
from pathlib import Path
from typing import List

from .reader import EmailMessage, ClassificationResult

logger = logging.getLogger(__name__)

BLOCKED: dict = {
    ".jpeg": "изображение JPEG", ".jpg": "изображение JPEG",
    ".png":  "изображение PNG",  ".gif": "изображение GIF",
    ".bmp":  "изображение BMP",  ".webp": "изображение WebP",
    ".svg":  "векторное SVG",    ".json": "данные JSON",
    ".xml":  "данные XML",       ".csv":  "таблица CSV",
    ".xlsx": "таблица Excel",    ".xls":  "таблица Excel",
    ".pdf":  "документ PDF",     ".doc":  "документ Word",
    ".docx": "документ Word",    ".zip":  "архив ZIP",
    ".tar":  "архив TAR",        ".gz":   "архив GZ",
    ".rar":  "архив RAR",        ".7z":   "архив 7-Zip",
    ".mp3":  "аудио MP3",        ".mp4":  "видео MP4",
    ".avi":  "видео AVI",        ".mov":  "видео MOV",
    ".exe":  "исполняемый файл", ".sh":   "shell-скрипт",
    ".py":   "скрипт Python",    ".htm":  "HTML-страница",
    ".html": "HTML-страница",    ".bin":  "бинарный файл",
}


class MailProcessor:
    def __init__(self, inbox_dir, outbox_dir, classifier, report_dir, copy_dir=False, dry_run=False):
        self.inbox_dir = Path(inbox_dir)
        self.outbox_dir = Path(outbox_dir)
        self.classifier = classifier
        self.report_dir = Path(report_dir)
        self.copy = bool(copy_dir)
        self.dry_run = dry_run

    def process(self) -> List[ClassificationResult]:
        messages = self._read_inbox()
        logger.info(f"Прочитано писем: {len(messages)}")

        results = self.classifier.classify(messages)

        if not self.dry_run:
            for msg, result in zip(messages, results):
                self._place(msg, result)

        self._write_report(messages, results)
        return results

    def _read_inbox(self) -> List[EmailMessage]:
        messages = []
        for path in sorted(self.inbox_dir.iterdir()):
            if not path.is_file():
                continue
            msg = self._read_one(path)
            messages.append(msg)
        return messages

    def _read_one(self, path: Path) -> EmailMessage:
        ext = path.suffix.lower()

        if ext in BLOCKED:
            logger.warning(f"Заблокирован файл: {path.name} — {BLOCKED[ext]}")
            return EmailMessage(filename=path.name, subject="", body="", path=path, blocked=True)

        if ext != ".txt":
            logger.warning(f"Неизвестный формат: {path.name}")
            return EmailMessage(filename=path.name, subject="", body="", path=path, blocked=True)

        content = self._read_text(path)
        if content is None:
            logger.error(f"Не удалось прочитать: {path.name}")
            return EmailMessage(filename=path.name, subject="", body="", path=path, blocked=True)

        subject, body = self._parse(content)
        return EmailMessage(filename=path.name, subject=subject, body=body, path=path)

    def _read_text(self, path: Path):
        for enc in ("utf-8", "latin-1"):
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
            except OSError:
                return None
        return None

    def _parse(self, content: str):
        lines = content.strip().splitlines()
        subject = ""
        body_lines = []
        in_body = False
        for line in lines:
            if not in_body and line.lower().startswith("subject:"):
                subject = line[8:].strip()
            elif not in_body and line.strip() == "":
                in_body = True
            else:
                body_lines.append(line)
        body = "\n".join(body_lines) if body_lines else content
        return subject, body

    def _place(self, msg: EmailMessage, result: ClassificationResult) -> None:
        target_dir = self.outbox_dir / result.folder
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = target_dir / msg.filename
        counter = 1
        while destination.exists():
            stem = Path(msg.filename).stem
            suffix = Path(msg.filename).suffix
            destination = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            if self.copy:
                shutil.copy2(str(msg.path), str(destination))
            else:
                shutil.move(str(msg.path), str(destination))
            logger.info(f"{msg.filename} → {result.folder}")
        except PermissionError as exc:
            logger.error(f"Нет прав: {msg.filename}: {exc}")
            result.error = str(exc)
        except OSError as exc:
            logger.error(f"Ошибка перемещения {msg.filename}: {exc}")
            result.error = str(exc)

    def _write_report(self, messages, results) -> None:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.report_dir / "reports.json"

        items = []
        distribution = {}
        for msg, res in zip(messages, results):
            items.append({
                "file": msg.filename,
                "category": res.category,
                "folder": res.folder,
                "score": res.score,
                "matched_terms": res.matched_terms,
                "reason": res.reason,
                "error": getattr(res, "error", None),
            })
            distribution[res.category] = distribution.get(res.category, 0) + 1

        report = {
            "total": len(items),
            "distribution": distribution,
            "items": items
        }

        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"Отчёт сохранён: {report_path}")
