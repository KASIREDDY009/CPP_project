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
recipes_table = dynamodb.Table("SmartPantryRecipes")

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


# ─── Recipe Routes ───

def get_recipes(user):
    try:
        resp = recipes_table.scan(
            FilterExpression=Key("username").eq(user["username"])
        )
        recipes = resp.get("Items", [])
        for recipe in recipes:
            for k, v in recipe.items():
                if isinstance(v, Decimal):
                    recipe[k] = int(v) if v == int(v) else float(v)
        return cors_response(200, {"recipes": recipes})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def create_recipe(body, user):
    title = body.get("title", "").strip()
    ingredients = body.get("ingredients", "").strip()
    instructions = body.get("instructions", "").strip()
    prep_time = body.get("prep_time", "").strip()
    category = body.get("category", "").strip()

    if not title:
        return cors_response(400, {"error": "Recipe title is required"})
    if not ingredients:
        return cors_response(400, {"error": "Ingredients are required"})
    if not instructions:
        return cors_response(400, {"error": "Instructions are required"})

    recipe_id = str(uuid.uuid4())
    recipe = {
        "id": recipe_id,
        "username": user["username"],
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time": prep_time if prep_time else "",
        "category": category if category else "General",
        "created_at": str(int(time.time())),
    }

    try:
        recipes_table.put_item(Item=recipe)
        return cors_response(201, {"recipe": recipe})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def get_recipe(recipe_id, user):
    try:
        resp = recipes_table.get_item(Key={"id": recipe_id})
        recipe = resp.get("Item")
        if not recipe or recipe["username"] != user["username"]:
            return cors_response(404, {"error": "Recipe not found"})
        for k, v in recipe.items():
            if isinstance(v, Decimal):
                recipe[k] = int(v) if v == int(v) else float(v)
        return cors_response(200, {"recipe": recipe})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def update_recipe(recipe_id, body, user):
    try:
        resp = recipes_table.get_item(Key={"id": recipe_id})
        recipe = resp.get("Item")
        if not recipe or recipe["username"] != user["username"]:
            return cors_response(404, {"error": "Recipe not found"})

        update_expr = "SET title = :t, ingredients = :i, instructions = :ins, prep_time = :p, category = :c"
        recipes_table.update_item(
            Key={"id": recipe_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues={
                ":t": body.get("title", recipe["title"]),
                ":i": body.get("ingredients", recipe["ingredients"]),
                ":ins": body.get("instructions", recipe["instructions"]),
                ":p": body.get("prep_time", recipe.get("prep_time", "")),
                ":c": body.get("category", recipe.get("category", "General")),
            },
        )
        return cors_response(200, {"message": "Recipe updated"})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


def delete_recipe(recipe_id, user):
    try:
        resp = recipes_table.get_item(Key={"id": recipe_id})
        recipe = resp.get("Item")
        if not recipe or recipe["username"] != user["username"]:
            return cors_response(404, {"error": "Recipe not found"})

        recipes_table.delete_item(Key={"id": recipe_id})
        return cors_response(200, {"message": "Recipe deleted"})
    except Exception as e:
        return cors_response(500, {"error": str(e)})


# ─── Lambda Handler ───

def seed_demo_data():
    """POST /auth/seed — create demo user with pantry items and recipes."""
    demo_user = "demo"
    demo_email = "demo@smartpantry.com"
    demo_pass = "Demo1234!"

    try:
        resp = users_table.get_item(Key={"id": demo_user})
        if "Item" in resp:
            return cors_response(200, {"message": "Demo data already exists", "username": demo_user, "password": demo_pass})
    except Exception:
        pass

    # Create demo user
    users_table.put_item(Item={
        "id": demo_user, "email": demo_email,
        "password": hash_password(demo_pass), "created_at": str(int(time.time())),
    })

    now = str(int(time.time()))
    # Create pantry items
    pantry_items = [
        {"name": "Chicken Breast", "category": "Meat", "quantity": 4, "unit": "pcs", "expiry_date": "2026-04-18"},
        {"name": "Basmati Rice", "category": "Grains", "quantity": 2, "unit": "kg", "expiry_date": "2026-12-01"},
        {"name": "Olive Oil", "category": "Oils", "quantity": 1, "unit": "bottle", "expiry_date": "2027-03-15"},
        {"name": "Fresh Tomatoes", "category": "Vegetables", "quantity": 6, "unit": "pcs", "expiry_date": "2026-04-15"},
        {"name": "Eggs (Free Range)", "category": "Dairy", "quantity": 12, "unit": "pcs", "expiry_date": "2026-04-20"},
        {"name": "Whole Milk", "category": "Dairy", "quantity": 2, "unit": "litres", "expiry_date": "2026-04-16"},
        {"name": "Garlic Cloves", "category": "Vegetables", "quantity": 10, "unit": "pcs", "expiry_date": "2026-05-01"},
        {"name": "Cheddar Cheese", "category": "Dairy", "quantity": 1, "unit": "block", "expiry_date": "2026-04-25"},
        {"name": "Pasta Penne", "category": "Grains", "quantity": 3, "unit": "packs", "expiry_date": "2027-01-10"},
        {"name": "Bell Peppers", "category": "Vegetables", "quantity": 4, "unit": "pcs", "expiry_date": "2026-04-17"},
        {"name": "Greek Yoghurt", "category": "Dairy", "quantity": 2, "unit": "tubs", "expiry_date": "2026-04-19"},
        {"name": "Soy Sauce", "category": "Condiments", "quantity": 1, "unit": "bottle", "expiry_date": "2027-06-01"},
    ]
    for item in pantry_items:
        items_table.put_item(Item={
            "id": str(uuid.uuid4()), "username": demo_user,
            "name": item["name"], "category": item["category"],
            "quantity": item["quantity"], "unit": item["unit"],
            "expiry_date": item["expiry_date"], "created_at": now,
        })

    # Create recipes
    recipes = [
        {"name": "Chicken Stir Fry", "ingredients": "Chicken Breast, Bell Peppers, Soy Sauce, Garlic, Olive Oil, Basmati Rice",
         "instructions": "1. Dice chicken into cubes\n2. Slice bell peppers\n3. Heat olive oil, sauté garlic\n4. Cook chicken until golden\n5. Add peppers and soy sauce\n6. Serve over rice",
         "cook_time": "25 mins", "servings": 2, "category": "Main Course"},
        {"name": "Classic Omelette", "ingredients": "Eggs, Cheddar Cheese, Bell Peppers, Whole Milk",
         "instructions": "1. Whisk 3 eggs with splash of milk\n2. Heat pan with butter\n3. Pour eggs, cook on low\n4. Add cheese and diced peppers\n5. Fold and serve",
         "cook_time": "10 mins", "servings": 1, "category": "Breakfast"},
        {"name": "Tomato Pasta", "ingredients": "Pasta Penne, Fresh Tomatoes, Garlic, Olive Oil, Cheddar Cheese",
         "instructions": "1. Boil pasta until al dente\n2. Sauté garlic in olive oil\n3. Add chopped tomatoes, simmer 15 mins\n4. Toss with pasta\n5. Top with grated cheese",
         "cook_time": "20 mins", "servings": 3, "category": "Main Course"},
        {"name": "Yoghurt Parfait", "ingredients": "Greek Yoghurt, Fresh Tomatoes",
         "instructions": "1. Layer yoghurt in a glass\n2. Add diced tomatoes (or any available fruit)\n3. Repeat layers\n4. Serve chilled",
         "cook_time": "5 mins", "servings": 1, "category": "Dessert"},
    ]
    for r in recipes:
        recipes_table.put_item(Item={
            "id": str(uuid.uuid4()), "username": demo_user,
            "name": r["name"], "ingredients": r["ingredients"],
            "instructions": r["instructions"], "cook_time": r.get("cook_time", ""),
            "servings": r.get("servings", 1), "category": r.get("category", ""),
            "created_at": now,
        })

    return cors_response(201, {
        "message": "Demo data seeded",
        "username": demo_user, "password": demo_pass,
        "items": len(pantry_items), "recipes": len(recipes),
    })


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
    if path == "/auth/seed" and method == "POST":
        return seed_demo_data()

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

    # Recipes
    if path == "/recipes" and method == "GET":
        return get_recipes(user)
    if path == "/recipes" and method == "POST":
        return create_recipe(body, user)
    if path.startswith("/recipes/") and method == "GET":
        recipe_id = path.split("/recipes/")[1]
        return get_recipe(recipe_id, user)
    if path.startswith("/recipes/") and method == "PUT":
        recipe_id = path.split("/recipes/")[1]
        return update_recipe(recipe_id, body, user)
    if path.startswith("/recipes/") and method == "DELETE":
        recipe_id = path.split("/recipes/")[1]
        return delete_recipe(recipe_id, user)

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
