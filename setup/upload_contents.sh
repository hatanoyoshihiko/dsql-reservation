#!/bin/bash
set -euo pipefail

# === パラメータ ===
STACK_NAME="dsql-reservation-system"
REGION="ap-northeast-1"
CONFIG_JSON="config.json"

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

# === config.json を生成 ===
echo "Generating $CONFIG_JSON with API_BASE=$API_BASE"
cat > "$CONFIG_JSON" <<EOF
{
  "API_BASE": "${API_BASE%/}"
}
EOF

# === S3にアップロード ===
echo "☁️ Uploading $CONFIG_JSON to s3://${S3_BUCKET}/config.json"
aws s3 cp "$CONFIG_JSON" "s3://${S3_BUCKET}/config.json" --region "$REGION"

