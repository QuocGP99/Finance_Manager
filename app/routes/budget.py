from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Expense, Category, SavingsGoal, Budget

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')

@budget_bp.route("/budget", methods=["GET", "POST"])
def budget():
    if request.method == "POST":
        # Thêm mới ngân sách
        name = request.form.get("name")
        spent = float(request.form.get("spent", 0))
        limit = float(request.form.get("limit", 0))
        color = request.form.get("color")
        bud = Budget(name=name, spent=spent, limit=limit, color=color)
        db.session.add(bud)
        db.session.commit()
        flash("Budget added!", "success")
        return redirect(url_for("budget"))

    # Xóa ngân sách
    delete_id = request.args.get("delete")
    if delete_id:
        bud = Budget.query.get(delete_id)
        if bud:
            db.session.delete(bud)
            db.session.commit()
            flash("Budget deleted!", "success")
        return redirect(url_for("budget"))

    # Sửa ngân sách
    edit_id = request.args.get("edit")
    if edit_id and request.method == "POST":
        bud = Budget.query.get(edit_id)
        if bud:
            bud.name = request.form.get("name")
            bud.spent = float(request.form.get("spent", 0))
            bud.limit = float(request.form.get("limit", 0))
            bud.color = request.form.get("color")
            db.session.commit()
            flash("Budget updated!", "success")
        return redirect(url_for("budget"))

    budgets = Budget.query.all()

    # chuẩn hoá tên danh mục budget
    def pct(spent, limit):
        return 0 if limit <= 0 else round(min(spent/limit*100, 100), 1)

    month_limit = sum(b.limit for b in budgets)
    month_spent = sum(b.spent for b in budgets)
    month_left  = max(month_limit - month_spent, 0)
    month_pct   = pct(month_spent, month_limit)

    cats = [
        {**b.__dict__, "pct": pct(b.spent, b.limit), "left": max(b.limit - b.spent, 0)}
        for b in budgets
    ]

    return render_template(
        "budget.html",
        title="FinanceManager · Budget",
        active_page="budget",
        month_limit=month_limit,
        month_spent=month_spent,
        month_left=month_left,
        month_pct=month_pct,
        cats=cats
    )