# sample_data.py — dữ liệu mẫu đầy đủ cho mọi trang (VNĐ)

# Ký hiệu tiền tệ
CURRENCY = "₫"

# ===== Dashboard =====
days = list(range(1, 16))
# dương = thu, âm = chi theo ngày
day_values = [320_000, -140_000, -250_000, 500_000, -190_000, -120_000, 360_000,
              -180_000, 210_000, -150_000, 420_000, -160_000, 280_000, -130_000, 340_000]

# Phân bổ theo danh mục (số dương để vẽ pie/doughnut)
cat_labels = ["Ăn uống", "Di chuyển", "Sách vở", "Giải trí", "Nhà ở"]
cat_values = [4_500_000, 2_800_000, 2_000_000, 1_400_000, 6_000_000]

kpis = {
    "total_balance": 68_450_000,
    "monthly_spent": 12_540_000,
    "savings_goal_value": 24_780_000,
    "ai_score": 8.2,
}

# ===== Expenses =====
# Quy ước: amount < 0 là CHI, amount > 0 là THU
sample_expenses = [
    {"name": "Cà phê Starbucks", "amount": -49_000,  "date": "2025-08-01", "method": "Thẻ tín dụng", "category": "Ăn uống"},
    {"name": "Vé xe buýt tháng", "amount": -350_000, "date": "2025-08-02", "method": "Thẻ ghi nợ",   "category": "Di chuyển"},
    {"name": "Giáo trình Vật lý","amount": -320_000, "date": "2025-08-03", "method": "Thẻ tín dụng", "category": "Sách vở"},
    {"name": "Lương part‑time",  "amount": 3_800_000,"date": "2025-08-04", "method": "Chuyển khoản", "category": "Thu nhập"},
]

# ===== Budget =====
budget_categories = [
    {"name": "Ăn uống",   "spent": 4_500_000, "limit": 5_000_000, "color": "red"},
    {"name": "Di chuyển", "spent": 2_800_000, "limit": 3_000_000, "color": "red"},
    {"name": "Sách vở",   "spent": 2_000_000, "limit": 2_500_000, "color": "yellow"},
    {"name": "Giải trí",  "spent": 1_400_000, "limit": 2_000_000, "color": "blue"},
    {"name": "Nhà ở",     "spent": 6_000_000, "limit": 8_000_000, "color": "green"},
]

# ===== Savings =====
savings_goals = [
    {"name": "Quỹ khẩn cấp", "current": 8_470_000, "target": 20_000_000, "priority": "high",   "due": "2025-12-31"},
    {"name": "Laptop mới",   "current": 4_000_000, "target": 12_000_000, "priority": "medium", "due": "2025-08-15"},
    {"name": "Du lịch xuân", "current": 2_500_000, "target": 8_000_000,  "priority": "low",    "due": "2026-03-01"},
]

# ===== Analytics =====
months = ["Apr", "May", "Jun", "Jul", "Aug"]
income_series   = [12_000_000, 13_500_000, 11_000_000, 15_000_000, 14_000_000]
spending_series = [ 9_000_000, 10_000_000,  9_500_000, 12_000_000, 11_000_000]

# ===== Helper format tiền VNĐ =====
def fmt_vnd(v: float) -> str:
    # Không dùng thập phân; dùng dấu . cho nhóm nghìn
    return f"{round(v):,}".replace(",", ".")

# ===== Unified taxonomy =====
# Nhóm danh mục cho Expenses (chi tiêu)
EXPENSE_CATEGORIES = [
    "Food & Dining", "Transportation", "Textbooks", "Entertainment",
    "Housing", "Utilities", "Healthcare", "Shopping", "Others"
]

# Nhóm danh mục cho Savings (mục tiêu tiết kiệm)
SAVINGS_CATEGORIES = [
    "Emergency", "Technology", "Travel", "Education",
    "Housing", "Transportation", "Personal"
]

# Nhóm danh mục cho Budget
BUDGET_CATEGORIES = [
    "Utilities", "Healthcare", "Shopping", "Personal Care",
    "Subscriptions", "Other"
]

# Alias ↔ tên chuẩn (tiếng Việt/Anh…)
ALIASES = {
    # Expenses
    "ăn uống": "Food & Dining", "food & dining": "Food & Dining", "food-dining": "Food & Dining",
    "di chuyển": "Transportation", "transportation": "Transportation", "transport": "Transportation",
    "sách vở": "Textbooks", "textbooks": "Textbooks",
    "giải trí": "Entertainment", "entertainment": "Entertainment",
    "nhà ở": "Housing", "housing": "Housing",
    "hóa đơn": "Utilities", "utilities": "Utilities", "bills": "Utilities",
    "y tế": "Healthcare", "healthcare": "Healthcare",
    "mua sắm": "Shopping", "shopping": "Shopping",
    "khác": "Others", "other": "Others", "others": "Others",
    # Budget
    "subscriptions": "Subscriptions", "subcriptions": "Subscriptions",  # sửa chính tả
    "personal care": "Personal Care",
    # Savings
    "emergency": "Emergency", "technology": "Technology", "travel": "Travel",
    "education": "Education", "personal": "Personal",
}

# 5 danh mục sẽ vẽ Pie chart (theo thứ tự cố định)
PIECHART_ORDER = ["Food & Dining", "Transportation", "Textbooks", "Entertainment", "Housing"]


def canon_cat(name: str, domain: str) -> str:
    """
    Chuẩn hoá tên danh mục theo domain: 'expense' | 'budget' | 'savings'.
    Nếu không khớp, trả về fallback ('Others' / 'Other' / 'Personal').
    """
    if not name:
        name = ""
    key = str(name).strip().lower()
    std = ALIASES.get(key)
    if domain == "expense":
        if std in EXPENSE_CATEGORIES:
            return std
        # nếu chưa map được, thử so khớp nguyên văn
        if name in EXPENSE_CATEGORIES:
            return name
        return "Others"
    elif domain == "budget":
        if std in BUDGET_CATEGORIES:
            return std
        if name in BUDGET_CATEGORIES:
            return name
        return "Other"
    elif domain == "savings":
        if std in SAVINGS_CATEGORIES:
            return std
        if name in SAVINGS_CATEGORIES:
            return name
        # savings không bắt buộc category, rơi về 'Personal'
        return "Personal"
    return name


def month_from_iso(d: str) -> str:
    # helper nếu muốn lọc theo tháng (YYYY-MM)
    return (d or "")[:7]

