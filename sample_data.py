# sample_data.py
# DỮ LIỆU MẪU (VNĐ)

# --- Dashboard: chuỗi ngày & giá trị chi/thu theo ngày ---
days = list(range(1, 16))
day_values = [320_000, -140_000, -250_000, 500_000, -190_000, -120_000, 360_000,
              -180_000, 210_000, -150_000, 420_000, -160_000, 280_000, -130_000, 340_000]

# --- Phân bổ theo danh mục (dùng số dương để vẽ pie/doughnut) ---
cat_labels = ["Ăn uống", "Di chuyển", "Sách vở", "Giải trí", "Nhà ở"]
cat_values = [4_500_000, 2_800_000, 2_000_000, 1_400_000, 6_000_000]

# --- KPI tổng quan ---
kpis = {
    "total_balance": 68_450_000,
    "monthly_spent": 12_540_000,
    "savings_goal_value": 24_780_000,
    "ai_score": 8.2,
}

# --- Giao dịch mẫu (thu/chi) ---
sample_expenses = [
    {"name": "Cà phê Starbucks", "amount": -49_000, "date": "2025-08-01", "method": "Thẻ tín dụng", "category": "Ăn uống"},
    {"name": "Vé xe buýt tháng",  "amount": -350_000, "date": "2025-08-02", "method": "Thẻ ghi nợ", "category": "Di chuyển"},
    {"name": "Giáo trình Vật lý", "amount": -320_000, "date": "2025-08-03", "method": "Thẻ tín dụng", "category": "Sách vở"},
    {"name": "Lương part‑time",   "amount": 3_800_000, "date": "2025-08-04", "method": "Chuyển khoản", "category": "Thu nhập"},
]

# --- Ngân sách theo danh mục ---
budget_categories = [
    {"name": "Ăn uống",   "spent": 4_500_000, "limit": 5_000_000, "color": "red"},
    {"name": "Di chuyển", "spent": 2_800_000, "limit": 3_000_000, "color": "red"},
    {"name": "Sách vở",   "spent": 2_000_000, "limit": 2_500_000, "color": "yellow"},
    {"name": "Giải trí",  "spent": 1_400_000, "limit": 2_000_000, "color": "blue"},
    {"name": "Nhà ở",     "spent": 6_000_000, "limit": 8_000_000, "color": "green"},
]

# --- Mục tiêu tiết kiệm ---
savings_goals = [
    {"name": "Quỹ khẩn cấp", "current": 8_470_000, "target": 20_000_000, "priority": "high",   "due": "2025-12-31"},
    {"name": "Laptop mới",   "current": 4_000_000, "target": 12_000_000, "priority": "medium", "due": "2025-08-15"},
    {"name": "Du lịch xuân", "current": 2_500_000, "target": 8_000_000,  "priority": "low",    "due": "2026-03-01"},
]

# --- Analytics: chuỗi tháng và series ---
months = ["Apr", "May", "Jun", "Jul", "Aug"]
income_series   = [12_000_000, 13_500_000, 11_000_000, 15_000_000, 14_000_000]
spending_series = [9_000_000,  10_000_000,  9_500_000, 12_000_000, 11_000_000]
