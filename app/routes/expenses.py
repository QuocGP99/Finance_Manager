from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Expense, Category

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route("/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "POST":
        # Lấy thông tin chi tiêu từ form
        expense_name = request.form.get("desc")
        expense_amount = float(request.form.get("amount", 0))
        expense_date = request.form.get("date")
        expense_method = request.form.get("method")
        category_id = request.form.get("category")
        
        if category_id:
            category_id = int(category_id)
        
        # Lưu thông tin chi tiêu vào cơ sở dữ liệu
        expense = Expense(name=expense_name, amount=expense_amount, date=expense_date, method=expense_method, category_id=category_id)
        db.session.add(expense)
        db.session.commit()

        flash("Expense added!", "success")
        return redirect(url_for("expenses"))
    
    # Lấy tất cả các danh mục từ cơ sở dữ liệu
    categories = Category.query.all()

    return render_template('expenses.html', expenses=[], categories=categories)


    # Sửa giao dịch (ví dụ qua form edit)
    edit_id = request.args.get("edit")
    if edit_id and request.method == "POST":
        exp = Expense.query.get(edit_id)
        if exp:
            exp.name = request.form.get("name")
            exp.amount = float(request.form.get("amount", 0))
            exp.date = request.form.get("date")
            exp.method = request.form.get("method")
            exp.category = request.form.get("category")
            db.session.commit()
            flash("Expense updated!", "success")
        return redirect(url_for("expenses"))

    # Xóa giao dịch
    delete_id = request.args.get("delete")
    if delete_id:
        exp = Expense.query.get(delete_id)
        if exp:
            db.session.delete(exp)
            db.session.commit()
            flash("Expense deleted!", "success")
        return redirect(url_for("expenses"))

    # Lọc theo category
    selected = request.args.get("category", "All")
    if selected != "All":
        expenses_filtered = Expense.query.filter_by(category=selected).all()
    else:
        expenses_filtered = Expense.query.all()

    total_spent = sum(-e.amount for e in expenses_filtered)
    num_transactions = len(expenses_filtered)
    avg_transaction = (total_spent / num_transactions) if num_transactions else 0

    for e in expenses_filtered:
        e.amount_str = f"{abs(e.amount):,}".replace(",", ".")

    # Lấy danh sách category từ DB
    categories = [c.name for c in Category.query.filter_by(type="expense").all()]

    return render_template(
        "expenses.html",
        title="FinanceManager · Expenses",
        active_page="expenses",
        expenses=expenses_filtered,
        selected=selected,
        total_spent=f"{total_spent:,.0f}",
        num_transactions=num_transactions,
        avg_transaction=f"{avg_transaction:,.0f}",
        categories=categories,
    )