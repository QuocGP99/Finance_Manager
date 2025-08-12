from flask import Flask, render_template, request
import os
import sample_data as sd

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

# Jinja helpers
app.jinja_env.filters["zip"] = zip
app.jinja_env.globals["abs"] = abs

# Currency & formatter
sd.CURRENCY = "₫"
def fmt_vnd(v: float) -> str:
    return f"{round(v):,}".replace(",", ".")

# ---------- ONE SOURCE OF TRUTH cho Budget KPI ----------
def compute_budget_totals():
    """Tính tổng ngân sách/thực chi/còn lại & % dùng."""
    month_limit = sum(c.get("limit", 0) for c in sd.budget_categories)
    month_spent = sum(c.get("spent", 0) for c in sd.budget_categories)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = 0 if month_limit == 0 else round(min(month_spent / month_limit * 100, 100), 1)
    return month_limit, month_spent, month_left, month_pct
# ---------------------------------------------------------

@app.route("/")
def dashboard():
    # Recent transactions
    def badge_of(cat, is_income):
        if cat in ("Ăn uống", "Đồ ăn", "Groceries"): return ("Ăn uống", "orange")
        if cat in ("Di chuyển", "Transport"):         return ("Di chuyển", "blue")
        if cat in ("Sách vở", "Textbooks"):           return ("Sách vở", "purple")
        if is_income:                                  return ("Thu nhập", "green")
        return (cat or "Khác", "yellow")

    recent = sorted(sd.sample_expenses, key=lambda x: x["date"], reverse=True)[:5]
    for t in recent:
        t["is_income"] = t["amount"] > 0
        t["amount_str"] = fmt_vnd(abs(t["amount"]))
        t["badge"] = badge_of(t.get("category", ""), t["is_income"])

    # ===== Budget Overview (dùng helper chung)
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    month_limit_raw, month_spent_raw, month_left_raw, month_pct = compute_budget_totals()

    cats = [
        {**c,
         "pct": pct(c.get("spent", 0), c.get("limit", 0)),
         "left": max(c.get("limit", 0) - c.get("spent", 0), 0)}
        for c in sd.budget_categories
    ]

    # Savings goals
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
        kpis=sd.kpis,
        days=sd.days, day_values=sd.day_values,
        cat_labels=sd.cat_labels, cat_values=sd.cat_values,

        # Panels (Budget overview đồng bộ)
        recent=recent,
        month_limit=fmt_vnd(month_limit_raw),
        month_spent=fmt_vnd(month_spent_raw),
        month_left=fmt_vnd(month_left_raw),
        month_pct=month_pct,
        cats=cats,

        # Raw (nếu muốn dùng ở KPI khác)
        month_limit_raw=month_limit_raw,
        month_spent_raw=month_spent_raw,
        month_left_raw=month_left_raw,

        # Savings tổng
        total_current=fmt_vnd(total_current),
        total_target=fmt_vnd(total_target),
        total_pct=total_pct,
    )

@app.route("/expenses")
def expenses():
    expenses_all = [e for e in sd.sample_expenses if e["amount"] < 0]
    categories = sorted({e.get("category", "Khác") for e in expenses_all})
    selected = request.args.get("category", "All")
    expenses_filtered = [e for e in expenses_all if selected == "All" or e.get("category") == selected]

    total_spent = sum(-e["amount"] for e in expenses_filtered)
    num_transactions = len(expenses_filtered)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0
    for e in expenses_filtered:
        e["amount_str"] = fmt_vnd(-e["amount"])

    return render_template(
        "expenses.html",
        title="FinanceManager · Expenses",
        active_page="expenses",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        expenses=expenses_filtered, categories=categories, selected=selected,
        total_spent=fmt_vnd(total_spent), num_transactions=num_transactions,
        avg_transaction=fmt_vnd(avg_transaction),
    )

@app.route("/budget")
def budget():
    month_limit_raw, month_spent_raw, month_left_raw, month_pct = compute_budget_totals()
    cats = [
        {**c,
         "pct": 0 if c["limit"]<=0 else round(min(c["spent"]/c["limit"]*100, 100), 1),
         "left": max(c["limit"] - c["spent"], 0)}
        for c in sd.budget_categories
    ]
    return render_template(
        "budget.html",
        title="FinanceManager · Budget",
        active_page="budget",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        month_limit=month_limit_raw,
        month_spent=month_spent_raw,
        month_left=month_left_raw,
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
        cat_values=sd.cat_values,
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
        total_pct=total_pct,
    )

if __name__ == "__main__":
    app.run(debug=True)
