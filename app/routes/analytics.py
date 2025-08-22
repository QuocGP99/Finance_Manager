from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Expense, Category, SavingsGoal, Budget

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route("/analytics")
def analytics():
    # Lấy dữ liệu chi tiêu từ DB cho pie chart
    from collections import defaultdict
    sums = defaultdict(float)
    for e in Expense.query.filter(Expense.amount < 0).all():
        sums[e.category] += -e.amount
    sorted_cats = sorted(sums.items(), key=lambda x: x[1], reverse=True)[:5]
    pie_labels = [cat for cat, val in sorted_cats]
    pie_values = [val for cat, val in sorted_cats]
    color_map = {
        "Food & Dining": "#3b82f6",
        "Transportation": "#10b981",
        "Textbooks": "#f59e0b",
        "Entertainment": "#ef4444",
        "Housing": "#8b5cf6"
    }
    pie_colors = [color_map.get(cat, "#bab0ab") for cat, val in sorted_cats]
    if not pie_colors:
        pie_colors = ["#bab0ab"] * 5

    # Nếu muốn truyền months, income_series, spending_series thì cần lấy từ DB hoặc hardcode tạm
    months = ["Apr", "May", "Jun", "Jul", "Aug"]
    income_series = [12000000, 13500000, 11000000, 15000000, 14000000]
    spending_series = [9000000, 10000000, 9500000, 12000000, 11000000]

    return render_template(
        "analytics.html",
        title="FinanceManager · Analytics",
        active_page="analytics",
        months=months,
        income_series=income_series,
        spending_series=spending_series,
        cat_labels=pie_labels, cat_values=pie_values, cat_colors=pie_colors
    )
