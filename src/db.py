import os
import boto3
import psycopg2

def get_connection():
    region = os.environ.get("AWS_REGION", "ap-northeast-1")
    dsql = boto3.client("dsql", region_name=region)

    # DSQLトークンを生成 (位置引数で指定)
    token = dsql.generate_db_connect_admin_auth_token(
        os.environ["DB_HOST"],
        region
    )

    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=token,
        sslmode="require"
    )
    return conn
