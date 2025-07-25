#!/bin/bash
set -euo pipefail

# === パラメータ ===
STACK_NAME="dsql-reservation-system"
REGION="ap-northeast-1"
FRONT_DIR="frontend"
CONFIG_JSON="${FRONT_DIR}/config.json"
CONTENTS_FILE="${FRONT_DIR}/index.html ${FRONT_DIR}/script.js ${CONFIG_JSON}"

# === CloudFormation から出力値を取得 ===
echo "Retrieving outputs from CloudFormation stack: $STACK_NAME"

API_BASE=$(aws cloudformation describe-stacks \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text)

S3_BUCKET=$(aws cloudformation describe-stacks \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='UiBucket'].OutputValue" \
  --output text)

# === config.json を frontend/ 配下に生成 ===
echo "Generating $CONFIG_JSON with API_BASE=$API_BASE"
mkdir -p "$FRONT_DIR"
cat > "$CONFIG_JSON" <<EOF
{
  "API_BASE": "${API_BASE%/}"
}
EOF

# === S3にアップロード ===
for FILE in $CONTENTS_FILE; do
  if [[ ! -f "$FILE" ]]; then
    echo " File not found: $FILE"
    exit 1
  fi
  BASENAME=$(basename "$FILE")
  echo "☁️ Uploading $BASENAME to s3://${S3_BUCKET}/"
  aws s3 cp "$FILE" "s3://${S3_BUCKET}/${BASENAME}" --region "$REGION"
done

