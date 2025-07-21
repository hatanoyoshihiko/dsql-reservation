#!/bin/bash

set -euo pipefail

# ===== 変数定義 =====
PYTHON_VERSION="python3.13"
LAYER_BASE="layers/python"
LAYER_PATH="${LAYER_BASE}"
REQUIREMENTS_FILE="requirements.txt"
PACKAGE="psycopg2-binary==2.9.10"

# ===== Layerディレクトリを初期化 =====
echo "[1/3] Layer ディレクトリを初期化: ${LAYER_PATH}"
rm -rf "$LAYER_PATH"
mkdir -p "$LAYER_PATH"

# ===== psycopg2-binary をインストール =====
echo "[2/3] pip をアップグレードして psycopg2-binary をインストール"
python3 -m pip install --upgrade pip
python3 -m pip install "$PACKAGE" -t "$LAYER_PATH"

# ===== 結果確認 =====
echo "[3/3] インストール済みファイル:"
ls "$LAYER_PATH" | head

echo "psycopg2 layer を ${LAYER_PATH} に構築完了"
