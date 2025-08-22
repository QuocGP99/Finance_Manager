from app import db
from app.models import Category

def ensure_default_categories():
    expenses_lists = [
        "Food & Dining", "Transportation", "Textbooks", "Entertainment",
        "Housing", "Utilities", "Healthcare", "Shopping", "Others"
    ]
    for cat in expenses_lists:
        if not Category.query.filter_by(name=cat).first():
            db.session.add(Category(name=cat, type="expense"))
    db.session.commit()
    