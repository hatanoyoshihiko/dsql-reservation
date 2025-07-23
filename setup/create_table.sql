-- 既存のテーブルがあれば削除
DROP TABLE IF EXISTS reservations;

-- 新しい予約テーブルを作成（reserved_date に UNIQUE 制約あり）
CREATE TABLE IF NOT EXISTS reservations (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  reserved_date DATE NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
