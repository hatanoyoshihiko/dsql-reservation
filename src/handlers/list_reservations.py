import json
from db import get_connection

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Api-Gateway-Secret"
}

def lambda_handler(event, context):
    print("headers:", event.get("headers"))

    try:
        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}
        date = params.get('date')

        conn = get_connection()
        cur = conn.cursor()

        if date:
            cur.execute(
                "SELECT name, reserved_date FROM reservations WHERE DATE(reserved_date) = %s ORDER BY reserved_date",
                (date,)
            )
        else:
            cur.execute("SELECT name, reserved_date FROM reservations ORDER BY reserved_date")

        reservations = [
            {
                "name": row[0],
                "reserved_date": row[1].isoformat()
            }
            for row in cur.fetchall()
        ]

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(reservations)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
