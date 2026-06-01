from __future__ import annotations
import argparse
from pathlib import Path
from src.classifer import RuleBasedClassifier
from src.processor import MailProcessor

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Система обработки корпоративной почты')
    parser.add_argument("--inbox", default="data/inbox", help="Входящие")
    parser.add_argument("--out", default="data", help="Папка с разложенными файлами")
    parser.add_argument("--config", default="config/categories.json", help="Правила классификации")
    parser.add_argument("--reports", default="reports", help="Отчеты")
    parser.add_argument("--log-file", default="logs/app.log", help="Журнал приложения")
    parser.add_argument("--copy", action="store_true", help="Копировать вместо перемещения")
    parser.add_argument("--dry-run", action="store_true", help="Классификация и отчеты без изменения файлов")

    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args()
    try:
        classifier = RuleBasedClassifier(Path(args.config))
        processor = MailProcessor(
            inbox_dir=Path(args.inbox),
            outbox_dir=Path(args.out),
            classifier=classifier,
            report_dir=Path(args.reports),
            copy_dir=Path(args.copy),
            dry_run=args.dry_run
        )
        res = processor.process()
        errors = sum(1 for r in res if getattr(r, 'error', None))
        print(f"\nОбработано файлов: {len(res)} ")
        print(f"Возникло ошибок: {errors}")
        print(f"Папка с отчетами: {Path(args.reports).resolve()}")
        return 0
    except Exception as e:
        return 1

if __name__ == "__main__":
    raise SystemExit(main())