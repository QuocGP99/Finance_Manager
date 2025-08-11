from flask import Flask, render_template, request
from datetime import datetime
import sample_data as sd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # TODO: đặt qua biến môi trường khi deploy

# Cho Jinja dùng zip/abs nếu cần
app.jinja_env.filters['zip'] = zip
app.jinja_env.globals['abs'] = abs

# --- Định dạng VNĐ ---
sd.CURRENCY = "₫"

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

    recent = sorted(sd.sample_expenses, key=lambda x: x["date"], reverse=True)[:5]
    for t in recent:
        t["is_income"] = t["amount"] > 0
        t["amount_str"] = fmt_vnd(abs(t["amount"]))
        t["badge"] = badge_of(t.get("category", ""), t["is_income"])

    # Budget Overview
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit = 18_000_000
    month_spent = sum(c["spent"] for c in sd.budget_categories)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = pct(month_spent, month_limit)

    cats = [
        {**c, "pct": pct(c["spent"], c["limit"]), "left": max(c["limit"] - c["spent"], 0)}
        for c in sd.budget_categories
    ]

    # Savings Goals
    goals = []
    for g in sd.savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p})

    total_target  = sum(g["target"] for g in sd.savings_goals)
    total_current = sum(g["current"] for g in sd.savings_goals)
    total_pct     = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "dashboard.html",
        title="FinanceManager · Dashboard",
        active_page="dashboard",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        # KPIs + charts
        kpis=sd.kpis, days=sd.days, day_values=sd.day_values,
        cat_labels=sd.cat_labels, cat_values=sd.cat_values,
        # panels
        recent=recent,
        month_limit=fmt_vnd(month_limit), month_spent=fmt_vnd(month_spent),
        month_left=fmt_vnd(month_left), month_pct=month_pct, cats=cats,
        total_current=fmt_vnd(total_current), total_target=fmt_vnd(total_target), total_pct=total_pct
    )

@app.route("/expenses")
def expenses():
    # chỉ lấy các khoản CHI (amount < 0)
    expenses_all = [e for e in sd.sample_expenses if e["amount"] < 0]

    # danh mục duy nhất
    categories = sorted({e.get("category", "Khác") for e in expenses_all})
    selected = request.args.get("category", "All")

    # lọc theo ?category=
    if selected != "All":
        expenses_filtered = [e for e in expenses_all if e.get("category") == selected]
    else:
        expenses_filtered = expenses_all

    # KPI theo danh sách đã lọc
    total_spent = sum(-e["amount"] for e in expenses_filtered)
    num_transactions = len(expenses_filtered)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0

    # format tiền cho từng item
    for e in expenses_filtered:
        e["amount_str"] = sd.fmt_vnd(-e["amount"])

    return render_template(
        "expenses.html",
        title="FinanceManager · Expenses",
        active_page="expenses",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        expenses=expenses_filtered,
        categories=categories,
        selected=selected,
        total_spent=fmt_vnd(total_spent),
        num_transactions=num_transactions,
        avg_transaction=fmt_vnd(avg_transaction),
    )

@app.route("/budget")
def budget():
    import sample_data as sd

    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent/limit*100, 100), 1)

    month_limit = 18_000_000
    month_spent = sum(c["spent"] for c in sd.budget_categories)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = pct(month_spent, month_limit)

    cats = [{**c, "pct": pct(c["spent"], c["limit"]), "left": max(c["limit"]-c["spent"], 0)} for c in sd.budget_categories]

    return render_template(
        "budget.html",
        title="FinanceManager · Budget",
        active_page="budget",
        CURRENCY=sd.CURRENCY, fmt=sd.fmt_vnd,
        month_limit=month_limit,
        month_spent=month_spent,
        month_left=month_left,
        month_pct=month_pct,
        cats=cats
    )

@app.route("/analytics")
def analytics():
    return render_template(
        "analytics.html",
        title="FinanceManager · Analytics",
        active_page="analytics",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        months=sd.months,
        income_series=sd.income_series,
        spending_series=sd.spending_series,
        cat_labels=sd.cat_labels,
        cat_values=sd.cat_values
    )

@app.route("/savings")
def savings():
    goals = []
    for g in sd.savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p})

    total_target  = sum(g["target"] for g in sd.savings_goals)
    total_current = sum(g["current"] for g in sd.savings_goals)
    total_pct     = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)

    return render_template(
        "savings.html",
        title="FinanceManager · Savings",
        active_page="savings",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        goals=goals,
        total_current=fmt_vnd(total_current),
        total_target=fmt_vnd(total_target),
        total_pct=total_pct
    )

if __name__ == "__main__":
    app.run(debug=True)
