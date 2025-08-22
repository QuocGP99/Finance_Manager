from flask import Blueprint, render_template
from app.models import Expense, Budget, SavingsGoal, Category  
from app.filters import fmt 

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')


@dashboard_bp.route("/")
def dashboard():
    # Recent transactions (5 mới nhất)
    recent = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    for t in recent:
        t.is_income = t.amount > 0
        t.amount_str = f"{abs(t.amount):,}".replace(",", ".")
        # Badge color logic (tùy chỉnh nếu cần)
        color_map = {
            "Food & Dining": "blue",
            "Transportation": "green",
            "Textbooks": "yellow",
            "Entertainment": "red",
            "Housing": "purple"
        }
        t.badge = (t.category or "Others", color_map.get(t.category, "gray"))

    # Budget overview
    budgets = Budget.query.all()
    month_limit = sum(b.limit for b in budgets)
    month_spent = sum(b.spent for b in budgets)
    month_left = max(month_limit - month_spent, 0)
    month_pct = 0 if month_limit == 0 else round(min(month_spent / month_limit * 100, 100), 1)
    cats = [
        {**b.__dict__, "pct": 0 if b.limit <= 0 else round(min(b.spent / b.limit * 100, 100), 1),
         "left": max(b.limit - b.spent, 0)}
        for b in budgets
    ]

    # Savings goals
    goals = SavingsGoal.query.all()
    total_current = sum(g.current for g in goals)
    total_target = sum(g.target for g in goals)
    total_pct = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)
    for g in goals:
        g.pct = 0 if g.target <= 0 else round(min(g.current / g.target * 100, 100), 1)

    # Pie chart (chi tiêu theo category)
    pie_labels = []
    pie_values = []
    pie_colors = []
    from collections import defaultdict
    sums = defaultdict(float)
    for e in Expense.query.filter(Expense.amount < 0).all():
        sums[e.category] += -e.amount
    sorted_cats = sorted(sums.items(), key=lambda x: x[1], reverse=True)[:5]
    color_map = {
        "Food & Dining": "#3b82f6",
        "Transportation": "#10b981",
        "Textbooks": "#f59e0b",
        "Entertainment": "#ef4444",
        "Housing": "#8b5cf6"
    }
    for cat, val in sorted_cats:
        pie_labels.append(cat)
        pie_values.append(val)
        pie_colors.append(color_map.get(cat, "#bab0ab"))
    # Nếu không có dữ liệu, truyền màu mặc định
    if not pie_colors:
        pie_colors = ["#bab0ab"] * 5

    kpis = {
        "total_balance": 0,
        "monthly_spent": 0,
        "savings_goal_value": 0,
        "ai_score": 8.2
    }

    return render_template(
        "dashboard.html",
        title="FinanceManager · Dashboard",
        active_page="dashboard",
        kpis=kpis,
        recent=recent,
        month_limit=month_limit, 
        month_spent=month_spent,
        month_left=month_left, 
        month_pct=month_pct, 
        cats=cats,
        total_current=total_current, 
        total_target=total_target, 
        total_pct=total_pct,
        savings_goals=goals,
        cat_labels=pie_labels, 
        cat_values=pie_values, 
        cat_colors=pie_colors,
        CURRENCY="₫"
    )