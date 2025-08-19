from flask import Flask, render_template, request
import os
import sample_data as sd
from sample_data import get_piechart_colors

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

# Jinja helpers
app.jinja_env.filters["zip"] = zip
app.jinja_env.globals["abs"] = abs

# Currency & formatter
sd.CURRENCY = "₫"
def fmt_vnd(v: float) -> str:
    return f"{round(v):,}".replace(",", ".")

# ---------- helpers cho Dashboard ----------
def compute_pie_from_expenses(expenses):
    """
    Gom nhóm chi tiêu theo 5 category cố định trong PIECHART_ORDER.
    Bỏ qua thu nhập (amount > 0) và các category ngoài 5 nhóm -> dồn vào 'Others' (không vẽ).
    """
    sums = {k: 0 for k in sd.PIECHART_ORDER}
    for e in expenses:
        amt = e.get("amount", 0)
        if amt >= 0:   # chỉ tính chi tiêu
            continue
        cat = sd.canon_cat(e.get("category", ""), "expense")
        if cat in sums:
            sums[cat] += -amt  # amount < 0 => lấy trị tuyệt đối
    labels = sd.PIECHART_ORDER
    values = [sums[k] for k in labels]
    return labels, values

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
     # chuẩn hoá category cho sample_expenses
    normalized = []
    for t in sd.sample_expenses:
        t2 = dict(t)
        t2["category"] = sd.canon_cat(t.get("category", ""), "expense")
        normalized.append(t2)

    # Recent transactions
    def badge_of(cat, is_income):
        cat = sd.canon_cat(cat, "expense")
        color_map = {
            "Food & Dining": "blue",
            "Transportation": "green",
            "Textbooks": "yellow",
            "Entertainment": "red",
            "Housing": "purple"
        }
        if is_income:
            return ("Income", "green")
        return (cat or "Others", color_map.get(cat, "gray"))

    recent = sorted(normalized, key=lambda x: x["date"], reverse=True)[:5]
    for t in recent:
        t["is_income"] = t["amount"] > 0
        t["amount_str"] = fmt_vnd(abs(t["amount"]))
        t["badge"] = badge_of(t.get("category", ""), t["is_income"])

    # ===== Budget Overview (dùng helper chung)
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent / limit * 100, 100), 1)

    cats_raw = []
    for c in sd.budget_categories:
        c2 = dict(c)
        c2["name"] = sd.canon_cat(c.get("name", ""), "budget")
        cats_raw.append(c2)

    month_limit = 18_000_000
    month_spent = sum(c["spent"] for c in cats_raw)
    month_left = max(month_limit - month_spent, 0)
    month_pct = pct(month_spent, month_limit)

    cats = [
        {**c, "pct": pct(c["spent"], c["limit"]), "left": max(c["limit"] - c["spent"], 0)}
        for c in cats_raw
    ]
    # Savings goals
    goals = []
    for g in sd.savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p, "category": sd.canon_cat(g.get("category", ""), "savings")})

    total_target = sum(g["target"] for g in sd.savings_goals)
    total_current = sum(g["current"] for g in sd.savings_goals)
    total_pct = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)
    
    # Pie chart 5 nhóm lấy từ transactions đã chuẩn hoá
    pie_labels, pie_values = compute_pie_from_expenses(normalized)
    pie_colors = sd.get_piechart_colors(pie_labels)
    return render_template(
        "dashboard.html",
        title="FinanceManager · Dashboard",
        active_page="dashboard",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        kpis=sd.kpis,
        days=sd.days, day_values=sd.day_values,
        cat_labels=pie_labels, cat_values=pie_values, cat_colors=pie_colors,
        recent=recent,
        month_limit=fmt_vnd(month_limit), month_spent=fmt_vnd(month_spent),
        month_left=fmt_vnd(month_left), month_pct=month_pct, cats=cats,
        total_current=fmt_vnd(total_current), total_target=fmt_vnd(total_target), total_pct=total_pct
    )


@app.route("/expenses")
def expenses():
    expenses_all = []
    for e in sd.sample_expenses:
        if e["amount"] < 0:
            e2 = dict(e)
            e2["category"] = sd.canon_cat(e.get("category", ""), "expense")
            expenses_all.append(e2)

    categories = sd.EXPENSE_CATEGORIES[:]  # dùng taxonomy thống nhất
    selected = request.args.get("category", "All")

    # lọc tại server (vẫn giữ nếu bạn thích)
    if selected != "All":
        expenses_filtered = [e for e in expenses_all if e.get("category") == selected]
    else:
        expenses_filtered = expenses_all

    total_spent = sum(-e["amount"] for e in expenses_filtered)
    num_transactions = len(expenses_filtered)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0

    for e in expenses_filtered:
        e["amount_str"] = sd.fmt_vnd(-e["amount"])

    return render_template(
        "expenses.html",
        title="FinanceManager · Expenses",
        active_page="expenses",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        expenses=expenses_filtered,
        categories=categories,     # <-- danh sách chuẩn
        selected=selected,
        total_spent=fmt_vnd(total_spent),
        num_transactions=num_transactions,
        avg_transaction=fmt_vnd(avg_transaction),
    )

@app.route("/budget")
def budget():
    # chuẩn hoá tên danh mục budget
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent/limit*100, 100), 1)

    cats_norm = []
    for c in sd.budget_categories:
        c2 = dict(c)
        c2["name"] = sd.canon_cat(c.get("name", ""), "budget")
        cats_norm.append(c2)

    month_limit = sum(c["limit"] for c in cats_norm) or 18_000_000
    month_spent = sum(c["spent"] for c in cats_norm)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = pct(month_spent, month_limit)

    cats = [{**c, "pct": pct(c["spent"], c["limit"]), "left": max(c["limit"]-c["spent"], 0)} for c in cats_norm]

    return render_template(
        "budget.html",
        title="FinanceManager · Budget",
        active_page="budget",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        month_limit=month_limit,
        month_spent=month_spent,
        month_left=month_left,
        month_pct=month_pct,
        cats=cats
    )

@app.route("/analytics")
def analytics():
    exp_norm = []
    for e in sd.sample_expenses:
        if e["amount"] < 0:
            e2 = dict(e); e2["category"] = sd.canon_cat(e.get("category",""), "expense")
            exp_norm.append(e2)
    pie_labels, pie_values = compute_pie_from_expenses(exp_norm)
    pie_colors = sd.get_piechart_colors(pie_labels)
    return render_template(
        "analytics.html",
        title="FinanceManager · Analytics",
        active_page="analytics",
        CURRENCY=sd.CURRENCY, fmt=fmt_vnd,
        months=sd.months,
        income_series=sd.income_series,
        spending_series=sd.spending_series,
        cat_labels=pie_labels, cat_values=pie_values, cat_colors=pie_colors
    )

@app.route("/savings")
def savings():
    goals = []
    for g in sd.savings_goals:
        p = 0 if g["target"] <= 0 else round(min(g["current"] / g["target"] * 100, 100), 1)
        goals.append({**g, "pct": p, "category": sd.canon_cat(g.get("category", ""), "savings")})

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
    app.run(debug=True)
