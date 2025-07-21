#!/bin/bash
set -euo pipefail

# === 必要な変数を指定 ===
REGION="ap-northeast-1"
DB_IDENTIFIER=$(aws dsql list-clusters --query 'clusters[0].identifier' --output text)
DB_HOST=$(aws dsql get-cluster --identifier 7qabuh36de6riilp3rdavaveem --query 'arn' --output text | awk -F'/' '{print $2}')
DB_PORT=5432
DB_NAME="postgres"
DB_USER="admin"
SQL_SCRIPT="setup/create_table.sql"

# === AWS CLI v2 で DSQL トークンを生成 ===
echo "Generating DSQL auth token..."
AUTH_TOKEN=$(aws dsql generate-db-connect-admin-auth-token \
  --hostname "$DB_HOST" \
  --region "$REGION" \
  --expires-in 300 \
  --output text)

# === SQLスクリプトの存在チェック ===
if [ ! -f "$SQL_SCRIPT" ]; then
  echo "SQLスクリプトが見つかりません: $SQL_SCRIPT"
  exit 1
fi

# === psql を実行（パスワードにトークンを使用） ===
echo "Connecting via psql and executing $SQL_SCRIPT..."
PGPASSWORD="$AUTH_TOKEN" psql \
  "host=$DB_HOST port=$DB_PORT user=$DB_USER dbname=$DB_NAME sslmode=require" \
  -f "$SQL_SCRIPT"
