import json

from project.domain.models.models import Rule, File, History
from project import db


class RuleRepository:
    @staticmethod
    def find_id_by_name(rule_name: str) -> int:
        return Rule.query.filter_by(name=rule_name).first().rule_id

    @staticmethod
    def find_rule_by_rule_name(rule_name: str) -> Rule:
        return Rule.query.filter_by(name=rule_name).first()

    @staticmethod
    def find_rule_text_by_rule_name(rule_name: str) -> Rule:
        return Rule.query.filter_by(name=rule_name).first().getTheLatestFile()

    @staticmethod
    def find_all_rules() -> list:
        return Rule.query.all()

    @staticmethod
    def update_rule_name_and_category(old_rule_name: str, new_rule_name: str, new_category: str):
        Rule.query.filter_by(name=old_rule_name).update(dict(name=new_rule_name, category=new_category))
        db.session.commit()

    @staticmethod
    def create_new_rule(new_name: str, new_category: str):
        rule = Rule(new_name, new_category)
        db.session.add(rule)
        db.session.commit()

    @staticmethod
    def create_rule_file(rule_id: int, file: bytearray):
        file = File(rule_id, file)
        db.session.add(file)
        db.session.commit()

    @staticmethod
    def create_rule_history(rule_id: int, history: json):
        history = History(rule_id, history)
        db.session.add(history)
        db.session.commit()
