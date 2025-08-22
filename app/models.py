from app import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(32), nullable=False)
    method = db.Column(db.String(64))
    category = db.Column(db.String(64))

class Category(db.Model):
    __tablename__ = 'category'  # Optional, can be added to specify table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64))

    # Add this line to resolve the error
    __table_args__ = {'extend_existing': True}

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    spent = db.Column(db.Float, default=0)
    limit = db.Column(db.Float, default=0)
    color = db.Column(db.String(32))

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    current = db.Column(db.Float, default=0)
    target = db.Column(db.Float, default=0)
    priority = db.Column(db.String(16), default="medium")
    due = db.Column(db.String(32))
    category = db.Column(db.String(64))
