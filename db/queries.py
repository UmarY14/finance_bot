# ---- users ----
GET_USER = "SELECT id, name, created_at FROM users WHERE id = $1"
INSERT_USER = "INSERT INTO users (id, name) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING"

# ---- categories ----
INSERT_CATEGORY = (
    "INSERT INTO categories (user_id, name, type) VALUES ($1, $2, $3) RETURNING id"
)
GET_CATEGORIES_BY_USER = (
    "SELECT id, name, type FROM categories WHERE user_id = $1 ORDER BY type, name"
)
GET_CATEGORIES_BY_TYPE = (
    "SELECT id, name FROM categories WHERE user_id = $1 AND type = $2 ORDER BY name"
)
GET_CATEGORY = "SELECT id, name, type FROM categories WHERE id = $1 AND user_id = $2"
DELETE_CATEGORY = "DELETE FROM categories WHERE id = $1 AND user_id = $2"

# ---- transactions ----
INSERT_TRANSACTION = (
    "INSERT INTO transactions (user_id, category_id, amount, note) "
    "VALUES ($1, $2, $3, $4) RETURNING id, created_at"
)

MONTHLY_STATS = """
SELECT
    COALESCE(SUM(t.amount) FILTER (WHERE c.type = 'income'), 0)  AS income,
    COALESCE(SUM(t.amount) FILTER (WHERE c.type = 'expense'), 0) AS expense
FROM transactions t
JOIN categories c ON c.id = t.category_id
WHERE t.user_id = $1
  AND date_trunc('month', t.created_at) = date_trunc('month', CURRENT_DATE)
"""

LAST_TRANSACTIONS = """
SELECT t.created_at, t.amount, t.note, c.name AS category, c.type
FROM transactions t
LEFT JOIN categories c ON c.id = t.category_id
WHERE t.user_id = $1
ORDER BY t.created_at DESC
LIMIT 10
"""

MONTHLY_COMPARISON = """
SELECT to_char(date_trunc('month', t.created_at), 'YYYY-MM') AS month,
       COALESCE(SUM(t.amount) FILTER (WHERE c.type = 'income'), 0)  AS income,
       COALESCE(SUM(t.amount) FILTER (WHERE c.type = 'expense'), 0) AS expense
FROM transactions t
JOIN categories c ON c.id = t.category_id
WHERE t.user_id = $1
  AND t.created_at >= date_trunc('month', CURRENT_DATE) - INTERVAL '2 months'
GROUP BY 1
ORDER BY 1
"""

CURRENT_MONTH_TRANSACTIONS = """
SELECT t.created_at, c.name AS category, c.type, t.amount, t.note
FROM transactions t
LEFT JOIN categories c ON c.id = t.category_id
WHERE t.user_id = $1
  AND date_trunc('month', t.created_at) = date_trunc('month', CURRENT_DATE)
ORDER BY t.created_at
"""

CATEGORY_MONTH_SPENT = """
SELECT COALESCE(SUM(amount), 0)
FROM transactions
WHERE user_id = $1 AND category_id = $2
  AND date_trunc('month', created_at) = date_trunc('month', CURRENT_DATE)
"""

MONTHLY_EXPENSE_BY_CATEGORY = """
SELECT c.name, SUM(t.amount) AS total
FROM transactions t
JOIN categories c ON c.id = t.category_id
WHERE t.user_id = $1
  AND c.type = 'expense'
  AND date_trunc('month', t.created_at) = date_trunc('month', CURRENT_DATE)
GROUP BY c.name
ORDER BY total DESC
"""

# ---- limits (bonus) ----
UPSERT_LIMIT = (
    "INSERT INTO limits (user_id, category_id, amount) VALUES ($1, $2, $3) "
    "ON CONFLICT (user_id, category_id) DO UPDATE SET amount = EXCLUDED.amount"
)
GET_LIMIT = "SELECT amount FROM limits WHERE user_id = $1 AND category_id = $2"
DELETE_LIMIT = "DELETE FROM limits WHERE user_id = $1 AND category_id = $2"
GET_LIMITS = (
    "SELECT l.category_id, c.name, l.amount FROM limits l "
    "JOIN categories c ON c.id = l.category_id WHERE l.user_id = $1 ORDER BY c.name"
)
