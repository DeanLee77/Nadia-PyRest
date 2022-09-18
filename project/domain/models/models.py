import json

from project import db
from datetime import datetime
from operator import attrgetter



class Rule(db.Model):
    __tablename__ = 'rule'

    rule_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)
    category = db.Column(db.String)
    rule_files: list = db.relationship('file', backref='rule', lazy='dynamic')
    rule_histories: list = db.relationship('history', backref='rule', lazy='dynamic')

    def __init__(self, rule_name: str = None, rule_category: str = None,
                 new_rule_files: list = None, new_rule_histories: list = None):
        self.name = rule_name
        self.category = rule_category
        self.rule_files = new_rule_files
        self.rule_histories = new_rule_histories

    def add_file(self, file):
        self.rule_files.append(file)

    def get_the_latest_file(self):
        if len(self.rule_files) > 0:
            return max(self.rule_files, attrgetter(key='created_date'))
        return None

    def get_the_latest_history(self):
        if len(self.rule_histories) > 0:
            return max(self.rule_histories, attrgetter(key='created_date'))
        return None


class File(db.Model):
    __tablename__ = 'file'

    file_id = db.Column(db.BigInteger, primary_key=True)
    rule_id = db.Column(db.BigInteger, db.ForeignKey('rule.rule_id'))
    created_date = db.Column(db.TIMESTAMP)
    files = db.Column(db.LargeBinary)

    def __init__(self, rule_id: int = None, files: bytearray = None):
        self.rule_id = rule_id
        self.files = files

    def get_date_time(self):
        return datetime.fromtimestamp(self.created_date)


class History(db.Model):
    __tablename__ = 'history'

    history_id = db.Column(db.BigInteger, primary_key=True)
    rule_id = db.Column(db.BigInteger, db.ForeignKey('rule.rule_id'))
    created_date = db.Column(db.TIMESTAMP)
    history = db.Column(db.JSON)

    def __init__(self, rule_id: int, history: json):
        self.rule_id = rule_id
        self.history = history

    def get_date_time(self):
        return datetime.fromtimestamp(self.created_date)

    def get_history_dict(self):
        history_map = dict()
        history_json = self.history
