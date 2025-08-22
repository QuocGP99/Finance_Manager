from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Expense, Category, SavingsGoal

savings_bp = Blueprint('savings', __name__, url_prefix='/savings')

@savings_bp.route("/savings", methods=["GET", "POST"])
def savings():
    if request.method == "POST":
        # Thêm hoặc sửa mục tiêu tiết kiệm
        name = request.form.get("title")
        current = float(request.form.get("current", 0))
        target = float(request.form.get("target", 0))
        priority = request.form.get("priority", "medium")
        due = request.form.get("due", "")
        category = request.form.get("category", "General")
        edit_id = request.form.get("edit_id")
        if edit_id:
            goal = SavingsGoal.query.get(edit_id)
            if goal:
                goal.name = name
                goal.current = current
                goal.target = target
                goal.priority = priority
                goal.due = due
                goal.category = category
                db.session.commit()
                flash("Goal updated!", "success")
        else:
            goal = SavingsGoal(name=name, current=current, target=target, priority=priority, due=due, category=category)
            db.session.add(goal)
            db.session.commit()
            flash("Goal added!", "success")
        return redirect(url_for("savings"))

    # Xóa mục tiêu tiết kiệm
    delete_id = request.args.get("delete")
    if delete_id:
        goal = SavingsGoal.query.get(delete_id)
        if goal:
            db.session.delete(goal)
            db.session.commit()
            flash("Goal deleted!", "success")
        return redirect(url_for("savings"))

    goals = SavingsGoal.query.all()
    total_target  = sum(g.target for g in goals)
    total_current = sum(g.current for g in goals)
    total_pct     = 0 if total_target == 0 else round(min(total_current / total_target * 100, 100), 1)
    for g in goals:
        g.pct = 0 if g.target <= 0 else round(min(g.current / g.target * 100, 100), 1)

    return render_template(
        "savings.html",
        title="FinanceManager · Savings",
        active_page="savings",
        goals=goals,
        total_current=f"{total_current:,.0f}",
        total_target=f"{total_target:,.0f}",
        total_pct=total_pct
    )
