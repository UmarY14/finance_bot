CREATE TABLE IF NOT EXISTS users (
    id          BIGINT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(50) NOT NULL,
    type        VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id           SERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id  INT REFERENCES categories(id) ON DELETE SET NULL,
    amount       NUMERIC(12, 2) NOT NULL,
    note         TEXT,
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS limits (
    id           SERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id  INT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    amount       NUMERIC(12, 2) NOT NULL,
    UNIQUE (user_id, category_id)
);

CREATE INDEX IF NOT EXISTS idx_tx_user_created ON transactions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_cat_user_type   ON categories(user_id, type);
