from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rule(db.Model):
    __tablename__ = 'rule'

    rule_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)
    category = db.Column(db.String)
    rule_files: list = db.relationship('file', backref='rule', lazy='dynamic')
    rule_histories: list = db.relationship('history', backref='rule', lazy='dynamic')

    def add_file(self, file):
        self.rule_files.append(file)

    def get_the_latest_file(self):





class File(db.Model):
    __tablename__ = 'file'

    file_id = db.Column(db.BigInteger, primary_key=True)
    rule_id = db.Column(db.BigInteger, db.ForeignKey('rule.rule_id'))
    created_date = db.Column(db.TIMESTAMP)
    files = db.Column(db.LargeBinary)


class History(db.Model):
    __tablename__ = 'history'

    history_id = db.Column(db.BigInteger, primary_key=True)
    rule_id = db.Column(db.BigInteger, db.ForeignKey('rule.rule_id'))
    created_date = db.Column(db.TIMESTAMP)
    history = db.Column(db.JSON)



