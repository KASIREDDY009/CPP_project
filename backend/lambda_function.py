import json
import boto3
import uuid
import base64
import hashlib
import hmac
import time
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key

# AWS clients
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
s3_client = boto3.client("s3", region_name="eu-west-1")
rekognition_client = boto3.client("rekognition", region_name="eu-west-1")
sns_client = boto3.client("sns", region_name="eu-west-1")

# Tables
users_table = dynamodb.Table("SmartPantryUsers")
items_table = dynamodb.Table("SmartPantryItems")

# Config
S3_BUCKET = os.environ.get("S3_BUCKET", "smartpantry-images-kasireddy")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "smartpantry-secret-key-2026")


# ─── Helpers ───

def cors_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, default=str),
    }


def create_jwt(payload):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload["exp"] = int(time.time()) + 86400
    payload_enc = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    signature = hmac.new(JWT_SECRET.encode(), f"{header}.{payload_enc}".encode(), hashlib.sha256).digest()
    sig_enc = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header}.{payload_enc}.{sig_enc}"


def decode_jwt(token):
    parts = token.split(".")
    if len(parts) != 3:
        return None
    padding = 4 - len(parts[1]) % 4
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * padding))
    if payload.get("exp", 0) < time.time():
        return None
    return payload


def get_user_from_token(headers):
    auth = headers.get("Authorization") or headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return decode_jwt(auth[7:])


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── Auth Routes ───

def register(body):
    username = body.get("username", "").strip()
    email = body.get("email", "").strip()
    password = body.get("password", "").strip()

    if not username or not email or not password:
        return cors_response(400, {"error": "All fields are required"})

    # Check if user exists
    try:
        resp = users_table.get_item(Key={"id": username})
        if "Item" in resp:
            return cors_response(400, {"error": "Username already exists"})
    except Exception:
        pass

    users_table.put_item(Item={
        "id": username,
        "email": email,
        "password": hash_password(password),
        "created_at": str(int(time.time())),
    })

    token = create_jwt({"username": username, "email": email})
    return cors_response(200, {"token": token, "username": username})


def login(body):
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()

    if not username or not password:
        return cors_response(400, {"error": "Username and password are required"})

    try:
        resp = users_table.get_item(Key={"id": username})
        item = resp.get("Item")
        if not item or item["password"] != hash_password(password):
            return cors_response(401, {"error": "Invalid credentials"})
    except Exception as e:
        return cors_response(500, {"error": str(e)})

    token = create_jwt({"username": username, "email": item.get("email", "")})
    return cors_response(200, {"token": token, "username": username})


# ─── Pantry Item Routes ───

def get_items(user):
    try:
        resp = items_table.scan(
            FilterExpression=Key("username").eq(user["username"])
        )
        items = resp.get("Items", [])
        # Convert Decimal to int/float
        for item in items:
            for k, v in item.items():
                if isinstance(v, Decimal):
                    item[k] = int(v) if v == int(v) else float(v)
        return cors_response(200, {"items": items})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def create_item(body, user):
    name = body.get("name", "").strip()
    category = body.get("category", "").strip()
    quantity = body.get("quantity", 1)
    unit = body.get("unit", "pcs").strip()
    expiry_date = body.get("expiry_date", "").strip()
    image_url = body.get("image_url", "")

    if not name:
        return cors_response(400, {"error": "Item name is required"})

    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "username": user["username"],
        "name": name,
        "category": category if category else "Other",
        "quantity": int(quantity),
        "unit": unit,
        "expiry_date": expiry_date,
        "image_url": image_url if image_url else "",
        "created_at": str(int(time.time())),
    }

    try:
        items_table.put_item(Item=item)
        return cors_response(201, {"item": item})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def update_item(item_id, body, user):
    try:
        resp = items_table.get_item(Key={"id": item_id})
        item = resp.get("Item")
        if not item or item["username"] != user["username"]:
            return cors_response(404, {"error": "Item not found"})

        update_expr = "SET #n = :n, category = :c, quantity = :q, #u = :u, expiry_date = :e, image_url = :img"
        items_table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={"#n": "name", "#u": "unit"},
            ExpressionAttributeValues={
                ":n": body.get("name", item["name"]),
                ":c": body.get("category", item["category"]),
                ":q": int(body.get("quantity", item["quantity"])),
                ":u": body.get("unit", item["unit"]),
                ":e": body.get("expiry_date", item["expiry_date"]),
                ":img": body.get("image_url", item.get("image_url", "")),
            },
        )
        return cors_response(200, {"message": "Item updated"})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def delete_item(item_id, user):
    try:
        resp = items_table.get_item(Key={"id": item_id})
        item = resp.get("Item")
        if not item or item["username"] != user["username"]:
            return cors_response(404, {"error": "Item not found"})

        items_table.delete_item(Key={"id": item_id})
        return cors_response(200, {"message": "Item deleted"})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


# ─── Image Upload & Rekognition ───

def upload_image(body, user):
    image_data = body.get("image", "")
    if not image_data:
        return cors_response(400, {"error": "No image provided"})

    try:
        # Decode base64 image
        if "," in image_data:
            image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        # Upload to S3
        image_key = f"uploads/{user['username']}/{uuid.uuid4()}.jpg"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=image_key,
            Body=image_bytes,
            ContentType="image/jpeg",
        )
        image_url = f"https://{S3_BUCKET}.s3.eu-west-1.amazonaws.com/{image_key}"

        # Rekognition - detect labels
        rekog_resp = rekognition_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=70,
        )
        labels = [label["Name"] for label in rekog_resp.get("Labels", [])]

        # Try to determine category from labels
        food_categories = {
            "Fruit": ["Fruit", "Apple", "Banana", "Orange", "Grapes", "Strawberry", "Mango", "Pineapple", "Watermelon", "Lemon", "Lime"],
            "Vegetable": ["Vegetable", "Broccoli", "Carrot", "Tomato", "Potato", "Onion", "Pepper", "Lettuce", "Spinach", "Cucumber"],
            "Dairy": ["Dairy", "Milk", "Cheese", "Yogurt", "Butter", "Cream", "Egg"],
            "Meat": ["Meat", "Chicken", "Beef", "Pork", "Fish", "Seafood", "Steak", "Sausage"],
            "Bakery": ["Bread", "Bakery", "Cake", "Cookie", "Pastry", "Muffin", "Croissant"],
            "Beverage": ["Beverage", "Drink", "Juice", "Water", "Soda", "Coffee", "Tea", "Wine", "Beer", "Bottle"],
            "Snack": ["Snack", "Chips", "Candy", "Chocolate", "Popcorn", "Nuts"],
            "Grain": ["Rice", "Pasta", "Cereal", "Grain", "Flour", "Oats"],
        }

        detected_category = "Other"
        detected_name = ""
        for cat, keywords in food_categories.items():
            for label in labels:
                if label in keywords:
                    detected_category = cat
                    if not detected_name and label not in ["Fruit", "Vegetable", "Dairy", "Meat", "Bakery", "Beverage", "Snack", "Grain"]:
                        detected_name = label
                    break

        if not detected_name and labels:
            detected_name = labels[0]

        return cors_response(200, {
            "image_url": image_url,
            "labels": labels,
            "detected_name": detected_name,
            "detected_category": detected_category,
        })
    except Exception as e:
        return cors_response(500, {"error": str(e)})


# ─── SNS Notifications ───

def subscribe_notifications(body, user):
    email = body.get("email", "").strip()
    if not email:
        return cors_response(400, {"error": "Email is required"})

    if not SNS_TOPIC_ARN:
        return cors_response(500, {"error": "SNS not configured"})

    try:
        sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email,
        )
        return cors_response(200, {"message": f"Subscription request sent to {email}. Please confirm via email."})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def check_expiry_notifications(user):
    """Check for items expiring within 3 days and send SNS notification."""
    if not SNS_TOPIC_ARN:
        return cors_response(200, {"message": "SNS not configured", "expiring": []})

    try:
        from datetime import datetime, timedelta

        resp = items_table.scan(
            FilterExpression=Key("username").eq(user["username"])
        )
        items = resp.get("Items", [])
        today = datetime.now()
        threshold = today + timedelta(days=3)

        expiring = []
        expired = []
        for item in items:
            if item.get("expiry_date"):
                try:
                    exp_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d")
                    if exp_date < today:
                        expired.append(item["name"])
                    elif exp_date <= threshold:
                        expiring.append(item["name"])
                except ValueError:
                    pass

        if expiring or expired:
            message_parts = []
            if expired:
                message_parts.append(f"EXPIRED items: {', '.join(expired)}")
            if expiring:
                message_parts.append(f"Expiring soon (within 3 days): {', '.join(expiring)}")

            message = f"SmartPantry Alert for {user['username']}!\n\n" + "\n".join(message_parts)
            message += "\n\nPlease check your pantry and take action."

            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="SmartPantry - Expiry Alert",
                Message=message,
            )

        return cors_response(200, {
            "message": "Expiry check complete",
            "expiring": expiring,
            "expired": expired,
        })
    except Exception as e:
        return cors_response(500, {"error": str(e)})


# ─── Dashboard Stats ───

def get_dashboard(user):
    try:
        from datetime import datetime, timedelta

        resp = items_table.scan(
            FilterExpression=Key("username").eq(user["username"])
        )
        items = resp.get("Items", [])
        today = datetime.now()
        threshold = today + timedelta(days=3)

        total = len(items)
        expiring_soon = 0
        expired_count = 0
        categories = {}

        for item in items:
            cat = item.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1

            if item.get("expiry_date"):
                try:
                    exp_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d")
                    if exp_date < today:
                        expired_count += 1
                    elif exp_date <= threshold:
                        expiring_soon += 1
                except ValueError:
                    pass

        return cors_response(200, {
            "total_items": total,
            "expiring_soon": expiring_soon,
            "expired": expired_count,
            "categories": categories,
        })
    except Exception as e:
        return cors_response(500, {"error": str(e)})


# ─── Lambda Handler ───

def lambda_handler(event, context):
    method = event.get("httpMethod", "GET")
    path = event.get("path", "")

    # Strip /prod prefix if present
    if path.startswith("/prod"):
        path = path[5:]

    # OPTIONS - CORS preflight
    if method == "OPTIONS":
        return cors_response(200, {"message": "OK"})

    # Parse body
    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except (json.JSONDecodeError, TypeError):
            body = {}

    headers = event.get("headers") or {}

    # ── Public routes ──
    if path == "/auth/register" and method == "POST":
        return register(body)
    if path == "/auth/login" and method == "POST":
        return login(body)

    # ── Protected routes ──
    user = get_user_from_token(headers)
    if not user:
        return cors_response(401, {"error": "Unauthorized"})

    # Items
    if path == "/items" and method == "GET":
        return get_items(user)
    if path == "/items" and method == "POST":
        return create_item(body, user)

    # Item by ID
    if path.startswith("/items/") and method == "PUT":
        item_id = path.split("/items/")[1]
        return update_item(item_id, body, user)
    if path.startswith("/items/") and method == "DELETE":
        item_id = path.split("/items/")[1]
        return delete_item(item_id, user)

    # Image upload
    if path == "/upload" and method == "POST":
        return upload_image(body, user)

    # Dashboard
    if path == "/dashboard" and method == "GET":
        return get_dashboard(user)

    # Notifications
    if path == "/notifications/subscribe" and method == "POST":
        return subscribe_notifications(body, user)
    if path == "/notifications/check" and method == "POST":
        return check_expiry_notifications(user)

    return cors_response(404, {"error": "Not found"})
