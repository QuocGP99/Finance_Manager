from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # TODO: đặt qua biến môi trường khi deploy

# Cho Jinja dùng zip/abs nếu cần (tránh lỗi trên Jinja/Flask mới)
app.jinja_env.filters['zip'] = zip
app.jinja_env.globals['abs'] = abs

# -------------------- DATA MẪU GIỮ UI --------------------
# Dashboard (biểu đồ đầu trang)
days = list(range(1, 16))
day_values = [120, -40, -55, 200, -90, -30, 150, -80, 60, -45, 180, -60, 90, -35, 140]
cat_labels = ["Food & Dining", "Transportation", "Textbooks", "Entertainment", "Housing"]
cat_values = [450, 280, 200, 140, 600]  # trị dương để vẽ pie
kpis = {
    "total_balance": 2847.50,
    "monthly_spent": 1254.30,
    "savings_goal_value": 1247.80,
    "ai_score": 8.2,
}

# Expenses (thu/chi)
sample_expenses = [
    {"name": "Starbucks Coffee", "amount": -4.95, "date": "2025-08-01", "method": "Credit Card", "category": "Food & Dining"},
    {"name": "Bus Pass Monthly", "amount": -75.00, "date": "2025-08-02", "method": "Debit Card", "category": "Transportation"},
    {"name": "Textbook – Physics", "amount": -89.99, "date": "2025-08-03", "method": "Credit Card", "category": "Textbooks"},
    {"name": "Part‑time Job", "amount": 350.00, "date": "2025-08-04", "method": "Bank Transfer", "category": "Income"},
]

# Budget
budget_categories = [
    {"name": "Food & Dining", "spent": 450, "limit": 500, "color": "red"},
    {"name": "Transportation", "spent": 280, "limit": 300, "color": "red"},
    {"name": "Textbooks", "spent": 200, "limit": 250, "color": "yellow"},
    {"name": "Entertainment", "spent": 140, "limit": 200, "color": "blue"},
    {"name": "Housing", "spent": 600, "limit": 800, "color": "green"},
]

# Savings
savings_goals = [
    {"name": "Emergency Fund", "current": 847, "target": 2000, "priority": "high", "due": "2025-12-31"},
    {"name": "New Laptop", "current": 400, "target": 1200, "priority": "medium", "due": "2025-08-15"},
    {"name": "Spring Break Trip", "current": 250, "target": 800, "priority": "low", "due": "2026-03-01"},
]

# Helper chung
def fmt(v: float) -> str:
    return f"{v:,.2f}"


# -------------------- ROUTES --------------------
@app.route("/")
def dashboard():
    """Dashboard + 3 panel mới: Recent Transactions, Budget Overview, Savings Goals"""

    # Recent Transactions (5 gần nhất)
    recent = sorted(sample_expenses, key=lambda x: x["date"], reverse=True)[:5]
    for t in recent:
        t["is_income"] = t["amount"] > 0
        t["amount_str"] = fmt(abs(t["amount"]))
        cat = t.get("category", "")
        if cat in ("Food & Dining", "Groceries"):
            t["badge"] = ("Food & Dining", "orange")
        elif cat in ("Transportation", "Transport"):
            t["badge"] = ("Transportation", "blue")
        elif cat in ("Textbooks",):
            t["badge"] = ("Textbooks", "purple")
        elif t["is_income"]:
            t["badge"] = ("Income", "green")
        else:
            t["badge"] = (cat or "Other", "yellow")

    # Budget Overview
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit = 1800
    month_spent = sum(c["spent"] for c in budget_categories)
    month_left = max(month_limit - month_spent, 0)
    month_pct = pct(month_spent, month_limit)

    cats = []
    for c in budget_categories:
        cats.append({
            **c,
            "pct": pct(c["spent"], c["limit"]),
            "left": max(c["limit"] - c["spent"], 0)
        })

    # Savings Goals
    goals = []
    for g in savings_goals:
        gpct = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": gpct})

    total_target = sum(g["target"] for g in savings_goals)
    total_current = sum(g["current"] for g in savings_goals)
    total_pct = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "dashboard.html",
        title="StudentFinance · Dashboard",
        active_page="dashboard",
        # KPI + charts
        kpis=kpis, days=days, day_values=day_values,
        cat_labels=cat_labels, cat_values=cat_values,
        # Panels
        recent=recent,
        month_limit=fmt(month_limit), month_spent=fmt(month_spent),
        month_left=fmt(month_left), month_pct=month_pct, cats=cats,
        total_current=fmt(total_current), total_target=fmt(total_target), total_pct=total_pct,
        fmt=fmt
    )


@app.route("/expenses")
def expenses():
    expenses_only = [e for e in sample_expenses if e["amount"] < 0]
    total_spent = sum(-e["amount"] for e in expenses_only)
    num_transactions = len(expenses_only)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0

    for e in expenses_only:
        e["amount_str"] = fmt(-e["amount"])  # hiển thị số dương cho chi

    return render_template(
        "expenses.html",
        title="StudentFinance · Expenses",
        active_page="expenses",
        expenses=expenses_only,
        total_spent=fmt(total_spent),
        num_transactions=num_transactions,
        avg_transaction=fmt(avg_transaction)
    )


@app.route("/budget")
def budget():
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit = 1800
    month_spent = sum(c["spent"] for c in budget_categories)
    month_pct = pct(month_spent, month_limit)
    month_left = max(month_limit - month_spent, 0)

    cats = []
    for c in budget_categories:
        cats.append({**c, "pct": pct(c["spent"], c["limit"])})

    return render_template(
        "budget.html",
        title="StudentFinance · Budget",
        active_page="budget",
        month_limit=fmt(month_limit),
        month_spent=fmt(month_spent),
        month_pct=month_pct,
        month_left=fmt(month_left),
        cats=cats
    )


@app.route("/analytics")
def analytics():
    months = ["Apr", "May", "Jun", "Jul", "Aug"]
    income_series = [1200, 1300, 1100, 1500, 1400]
    spending_series = [900, 1000, 950, 1200, 1100]

    return render_template(
        "analytics.html",
        title="StudentFinance · Analytics",
        active_page="analytics",
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

    total_target = sum(g["target"] for g in savings_goals)
    total_current = sum(g["current"] for g in savings_goals)
    total_pct = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "savings.html",
        title="StudentFinance · Savings",
        active_page="savings",
        goals=goals,
        total_current=fmt(total_current),
        total_target=fmt(total_target),
        total_pct=total_pct
    )


if __name__ == "__main__":
    app.run(debug=True)
