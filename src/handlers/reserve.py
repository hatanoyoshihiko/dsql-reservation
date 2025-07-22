import json
import uuid
from datetime import datetime
from db import get_connection

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Api-Gateway-Secret"
}

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
        time = body.get("time")

        if not name or not date or not time:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "name, date, time are required"})
            }

        reserved_datetime = f"{date} {time}"
        reservation_id = str(uuid.uuid4())
        created_at = datetime.utcnow()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN")
            cursor.execute(
                """
                INSERT INTO reservations (id, name, reserved_date, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (reserved_date) DO NOTHING
                """,
                (reservation_id, name, date, created_at)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return {
                    "statusCode": 409,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "その日付はすでに予約されています"})
                }

            conn.commit()
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "予約が完了しました"})
            }

        except Exception as e:
            conn.rollback()
            raise e

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
