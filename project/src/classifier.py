import json
import re
from .models import CategoryRule, ClassificationResult
class RuleBasedClassifier:
    def __init__(self, config_path):
        self.rules = []
        self.unknown_folder = "unknown"
        self.empty_folder = "empty"
        self.load_rules(config_path)
    def load_rules(self, config_path):
        data = json.loads(open(config_path, encoding="utf-8").read())
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
    def classify(self, message):
        text = self.prepare_text(message.text_for_classification)
        if text.strip() == "":
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
            return ClassificationResult(
                category="unknown",
                folder=self.unknown_folder,
                score=0,
                matched_terms=[],
                reason="Категория не найдена."
            )
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
        pattern = r"(?<![\wа-я])" + re.escape(word) + r"(?![\wа-я])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
        return False