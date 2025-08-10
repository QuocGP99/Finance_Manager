from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/expenses")
def expenses():
    return render_template("expenses.html")

@app.route("/budget")
def budget():
    return render_template("budget.html")

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/savings")
def savings():
    return render_template("savings.html")

if __name__ == "__main__":
    app.run(debug=True)
