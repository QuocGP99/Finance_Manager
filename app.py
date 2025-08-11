from flask import Flask, render_template
from sample_data import (
    days, day_values, cat_labels, cat_values, kpis,
    sample_expenses, budget_categories, savings_goals,
    months, income_series, spending_series
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # TODO: đặt qua biến môi trường khi deploy

# Cho Jinja dùng zip/abs nếu cần
app.jinja_env.filters['zip'] = zip
app.jinja_env.globals['abs'] = abs

# --- Định dạng VNĐ ---
CURRENCY = "₫"

def fmt_vnd(v: float) -> str:
    """Format số kiểu VNĐ: không thập phân, dùng dấu . phân tách nghìn."""
    return f"{round(v):,}".replace(",", ".")

# -------------------- ROUTES --------------------
@app.route("/")
def dashboard():
    """Dashboard + Recent Transactions, Budget Overview, Savings Goals"""

    # Recent transactions
    def badge_of(cat, is_income):
        if cat in ("Ăn uống", "Đồ ăn", "Groceries"):
            return ("Ăn uống", "orange")
        if cat in ("Di chuyển", "Transport"):
            return ("Di chuyển", "blue")
        if cat in ("Sách vở", "Textbooks"):
            return ("Sách vở", "purple")
        if is_income:
            return ("Thu nhập", "green")
        return (cat or "Khác", "yellow")

    recent = sorted(sample_expenses, key=lambda x: x["date"], reverse=True)[:5]
    for t in recent:
        t["is_income"] = t["amount"] > 0
        t["amount_str"] = fmt_vnd(abs(t["amount"]))
        t["badge"] = badge_of(t.get("category", ""), t["is_income"])

    # Budget Overview
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit = 18_000_000
    month_spent = sum(c["spent"] for c in budget_categories)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = pct(month_spent, month_limit)

    cats = [
        {**c, "pct": pct(c["spent"], c["limit"]), "left": max(c["limit"] - c["spent"], 0)}
        for c in budget_categories
    ]

    # Savings Goals
    goals = []
    for g in savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p})

    total_target  = sum(g["target"] for g in savings_goals)
    total_current = sum(g["current"] for g in savings_goals)
    total_pct     = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "dashboard.html",
        title="FinanceManager · Dashboard",
        active_page="dashboard",
        CURRENCY=CURRENCY, fmt=fmt_vnd,
        # KPIs + charts
        kpis=kpis, days=days, day_values=day_values,
        cat_labels=cat_labels, cat_values=cat_values,
        # panels
        recent=recent,
        month_limit=fmt_vnd(month_limit), month_spent=fmt_vnd(month_spent),
        month_left=fmt_vnd(month_left), month_pct=month_pct, cats=cats,
        total_current=fmt_vnd(total_current), total_target=fmt_vnd(total_target), total_pct=total_pct
    )

@app.route("/expenses")
def expenses():
    expenses_only = [e for e in sample_expenses if e["amount"] < 0]
    total_spent = sum(-e["amount"] for e in expenses_only)
    num_transactions = len(expenses_only)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0

    for e in expenses_only:
        e["amount_str"] = fmt_vnd(-e["amount"])

    return render_template(
        "expenses.html",
        title="FinanceManager · Expenses",
        active_page="expenses",
        CURRENCY=CURRENCY, fmt=fmt_vnd,
        expenses=expenses_only,
        total_spent=fmt_vnd(total_spent),
        num_transactions=num_transactions,
        avg_transaction=fmt_vnd(avg_transaction)
    )

@app.route("/budget")
def budget():
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit = 18_000_000
    month_spent = sum(c["spent"] for c in budget_categories)
    month_pct = pct(month_spent, month_limit)
    month_left = max(month_limit - month_spent, 0)

    cats = [{**c, "pct": pct(c["spent"], c["limit"])} for c in budget_categories]

    return render_template(
        "budget.html",
        title="FinanceManager · Budget",
        active_page="budget",
        CURRENCY=CURRENCY, fmt=fmt_vnd,
        month_limit=fmt_vnd(month_limit),
        month_spent=fmt_vnd(month_spent),
        month_pct=month_pct,
        month_left=fmt_vnd(month_left),
        cats=cats
    )

@app.route("/analytics")
def analytics():
    return render_template(
        "analytics.html",
        title="FinanceManager · Analytics",
        active_page="analytics",
        CURRENCY=CURRENCY, fmt=fmt_vnd,
        months=months,
        income_series=income_series,
        spending_series=spending_series,
        cat_labels=cat_labels,
        cat_values=cat_values
    )

@app.route("/savings")
def savings():
    goals = []
    for g in savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p})

    total_target  = sum(g["target"] for g in savings_goals)
    total_current = sum(g["current"] for g in savings_goals)
    total_pct     = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "savings.html",
        title="FinanceManager · Savings",
        active_page="savings",
        CURRENCY=CURRENCY, fmt=fmt_vnd,
        goals=goals,
        total_current=fmt_vnd(total_current),
        total_target=fmt_vnd(total_target),
        total_pct=total_pct
    )

if __name__ == "__main__":
    app.run(debug=True)
