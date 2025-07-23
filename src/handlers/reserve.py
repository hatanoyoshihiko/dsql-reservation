import json
import uuid
from datetime import datetime
from db import get_connection
import time
from psycopg2.errors import UniqueViolation

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Api-Gateway-Secret"
}

def get_sleep_by_name_length(name: str, scale: float = 1.0, max_sleep: int = 10) -> float:
    char_len = len(name)
    return min(char_len * scale, max_sleep)

def lambda_handler(event, context):
    print("headers:", event.get("headers"))
    print("method:", event.get("httpMethod"))

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "CORS preflight passed"})
        }

    try:
        body = json.loads(event["body"])
        name = body.get("name")
        date = body.get("date")
        time_str = body.get("time")

        if not name or not date or not time_str:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "name, date, time are required"})
            }

        reserved_datetime = f"{date} {time_str}"
        reservation_id = str(uuid.uuid4())
        created_at = datetime.utcnow()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN")

            sleep_sec = get_sleep_by_name_length(name)
            print(f"{name=} の文字数による遅延: {sleep_sec:.1f} 秒")
            time.sleep(sleep_sec)

            try:
                cursor.execute(
                    """
                    INSERT INTO reservations (id, name, reserved_date, created_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (reservation_id, name, date, created_at)
                )
                conn.commit()
                return {
                    "statusCode": 200,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"message": "予約が完了しました"})
                }

            except UniqueViolation:
                conn.rollback()
                return {
                    "statusCode": 409,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "その日付はすでに予約されています（予約競合）"})
                }
            except Exception as e:
                conn.rollback()
                if 'duplicate key' in str(e).lower():
                    return {
                        "statusCode": 409,
                        "headers": CORS_HEADERS,
                        "body": json.dumps({"error": "その日付はすでに予約されています（競合）"})
                    }
                return {
                    "statusCode": 500,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": str(e)})
                }

        except Exception as e:
            conn.rollback()
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": str(e)})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
