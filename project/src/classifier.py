import json
import logging
import re
from .reader import CategoryRule, ClassificationResult

logger = logging.getLogger(__name__)

class RuleBasedClassifier:
    def __init__(self, config_path):
        self.rules = []
        self.unknown_folder = "unknown"
        self.empty_folder = "empty"
        self.load_rules(config_path)

    def load_rules(self, config_path):
        logger.info(f"Загрузка правил классификации из {config_path}")
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        self.unknown_folder = data.get("unknown_folder", "unknown")
        self.empty_folder = data.get("empty_folder", "empty")
        for item in data["categories"]:
            rule = CategoryRule(
                name=item["name"],
                folder=item["folder"],
                description=item.get("description", ""),
                priority=int(item.get("priority", 0)),
                keywords=item.get("keywords", []),
                patterns=item.get("patterns", [])
            )
            self.rules.append(rule)
        self.rules.sort(key=lambda rule: rule.priority, reverse=True)
        logger.info(f"Задано категорий: {len(self.rules)}")

    def classify(self, messages):
        logger.info(f"Начало классификации сообщений")
        results = []
        for message in messages:
            result = self.classify_one(message)
            results.append(result)
        return results

    def classify_one(self, message):
        msg = getattr(message, 'filename', 'unknown_msg')
        text = message.get_full_text()
        text = self.prepare_text(text)
        if text.strip() == "":
            logger.warning(f"Письмо '{msg}' классифицировано как пустое")
            return ClassificationResult(
                category="empty",
                folder=self.empty_folder,
                score=0,
                matched_terms=[],
                reason="Письмо пустое или не содержит текста."
            )
        best_rule = None
        best_score = 0
        best_words = []
        for rule in self.rules:
            score, words = self.check_rule(text, rule)
            if score > best_score:
                best_score = score
                best_rule = rule
                best_words = words
            elif score == best_score and best_rule is not None:
                if rule.priority > best_rule.priority:
                    best_rule = rule
                    best_words = words
        if best_rule is None or best_score == 0:
            logger.warning(f"Письмо '{msg}' не подошло ни под одно правило. Отправлено в '{self.unknown_folder}'")
            return ClassificationResult(
                category="unknown",
                folder=self.unknown_folder,
                score=0,
                matched_terms=[],
                reason="Категория не найдена."
            )
        logger.info(f"Письму {msg} присвоена категория '{best_rule.name}'")
        return ClassificationResult(
            category=best_rule.name,
            folder=best_rule.folder,
            score=best_score,
            matched_terms=best_words,
            reason="Категория выбрана по совпадениям: " + ", ".join(best_words[:6])
        )

    def check_rule(self, text, rule):
        score = 0
        words = []
        for keyword in rule.keywords:
            word = self.prepare_text(keyword)
            if word == "":
                continue
            if self.has_word(text, word):
                score += 2
                words.append(keyword)
        for pattern in rule.patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                score += 3
                words.append(pattern)
        return score, words

    def prepare_text(self, text):
        text = text.lower()
        text = text.replace("ё", "е")
        text = re.sub(r"\s+", " ", text)
        return text

    def has_word(self, text, word):
        if " " in word:
            return word in text
        for m in re.finditer(re.escape(word), text, flags=re.IGNORECASE):
            start, end = m.start(), m.end()
            before = text[start - 1] if start > 0 else None
            after = text[end] if end < len(text) else None
            before_is_space = before is None or before.isspace()
            after_is_space = after is None or after.isspace()
            if before_is_space and after_is_space:
                return True
            before_is_letter = before is not None and not before.isspace()
            after_is_letter = after is not None and not after.isspace()
            if before_is_letter and after_is_letter:
                return True
        return False
