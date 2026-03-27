"""
CloudChef Recipe Manager - Lambda Function
==========================================
Single Lambda function handling all API routes via API Gateway REST API.
Manages recipes in DynamoDB with S3 image storage, Rekognition image analysis,
and SNS for recipe update notifications.

Region: eu-west-1
"""

import json
import uuid
import base64
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Configuration from environment variables
# ---------------------------------------------------------------------------
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'cloudchef-recipes-prod')
S3_BUCKET = os.environ.get('S3_BUCKET', 'cloudchef-images-prod')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
REGION = os.environ.get('REGION', 'eu-west-1')

# ---------------------------------------------------------------------------
# AWS service clients (created once per Lambda cold start for reuse)
# ---------------------------------------------------------------------------
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
s3 = boto3.client('s3', region_name=REGION)
rekognition = boto3.client('rekognition', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# ---------------------------------------------------------------------------
# CORS headers - attached to every response so the frontend can call the API
# ---------------------------------------------------------------------------
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
}


# ===========================================================================
# Helper functions
# ===========================================================================

def build_response(status_code, body):
    """Build a properly formatted API Gateway response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, default=str)
    }


def convert_floats(obj):
    """Recursively convert float/int values to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, int) and not isinstance(obj, bool):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    return obj


def parse_body(event):
    """Safely parse the JSON body from the API Gateway event."""
    body = event.get('body')
    if not body:
        return {}
    try:
        parsed = json.loads(body)
        return convert_floats(parsed)
    except (json.JSONDecodeError, TypeError):
        return {}


def upload_image_to_s3(image_base64, image_key):
    """Decode a base64 image string and upload it to S3."""
    try:
        image_bytes = base64.b64decode(image_base64)
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=image_key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        return image_key
    except Exception as e:
        print(f'[ERROR] Failed to upload image to S3: {e}')
        return None


def delete_image_from_s3(image_key):
    """Delete an image from S3. Fails silently if the object does not exist."""
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=image_key)
    except ClientError as e:
        print(f'[WARN] Failed to delete S3 object {image_key}: {e}')


def detect_labels_from_s3(image_key):
    """Run Rekognition detect_labels on an image stored in S3."""
    try:
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': S3_BUCKET, 'Name': image_key}},
            MaxLabels=15,
            MinConfidence=70
        )
        labels = [
            {'name': label['Name'], 'confidence': round(label['Confidence'], 2)}
            for label in response.get('Labels', [])
        ]
        return labels
    except ClientError as e:
        print(f'[ERROR] Rekognition detect_labels failed: {e}')
        return []


def publish_sns_notification(subject, message):
    """Publish a notification to the CloudChef SNS topic."""
    if not SNS_TOPIC_ARN:
        print('[WARN] SNS_TOPIC_ARN not set, skipping notification')
        return
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=message
        )
        print(f'[INFO] SNS notification sent: {subject}')
    except Exception as e:
        print(f'[ERROR] SNS publish failed: {e}')


# ===========================================================================
# Route handlers
# ===========================================================================

def get_all_recipes():
    """GET /recipes - Scan DynamoDB and return all recipes."""
    try:
        response = table.scan()
        recipes = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            recipes.extend(response.get('Items', []))
        return build_response(200, {'recipes': recipes})
    except ClientError as e:
        print(f'[ERROR] DynamoDB scan failed: {e}')
        return build_response(500, {'error': 'Failed to fetch recipes'})


def create_recipe(event):
    """POST /recipes - Create a new recipe in DynamoDB."""
    body = parse_body(event)
    if not body.get('title'):
        return build_response(400, {'error': 'Recipe title is required'})

    recipe_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    recipe = {
        'recipeId': recipe_id,
        'title': body.get('title', ''),
        'description': body.get('description', ''),
        'instructions': body.get('instructions', ''),
        'ingredients': body.get('ingredients', []),
        'cuisine': body.get('cuisine', ''),
        'difficulty': body.get('difficulty', 'medium'),
        'prepTime': body.get('prepTime', ''),
        'cookTime': body.get('cookTime', ''),
        'servings': body.get('servings', 0),
        'createdAt': now,
        'updatedAt': now
    }

    # If an image is provided, upload to S3 and analyse with Rekognition
    image_base64 = body.get('image')
    if image_base64:
        image_key = f'recipes/{recipe_id}/image.jpg'
        uploaded_key = upload_image_to_s3(image_base64, image_key)
        if uploaded_key:
            recipe['imageKey'] = uploaded_key
            recipe['imageUrl'] = f'https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{uploaded_key}'
            labels = detect_labels_from_s3(uploaded_key)
            recipe['detectedLabels'] = labels

    try:
        table.put_item(Item=recipe)

        # Send SNS notification about new recipe
        publish_sns_notification(
            f'New Recipe: {recipe["title"]}',
            f'A new recipe has been added to CloudChef!\n\n'
            f'Title: {recipe["title"]}\n'
            f'Category: {recipe.get("cuisine", "N/A")}\n'
            f'Prep Time: {recipe.get("prepTime", "N/A")} min\n'
            f'Cook Time: {recipe.get("cookTime", "N/A")} min\n'
            f'Servings: {recipe.get("servings", "N/A")}\n\n'
            f'Description: {recipe.get("description", "No description")}\n\n'
            f'Visit CloudChef to view the full recipe!'
        )

        return build_response(201, {'recipe': recipe})
    except ClientError as e:
        print(f'[ERROR] DynamoDB put_item failed: {e}')
        return build_response(500, {'error': 'Failed to create recipe'})


def get_recipe(recipe_id):
    """GET /recipes/{id} - Fetch a single recipe by its recipeId."""
    try:
        response = table.get_item(Key={'recipeId': recipe_id})
        recipe = response.get('Item')
        if not recipe:
            return build_response(404, {'error': 'Recipe not found'})
        return build_response(200, {'recipe': recipe})
    except ClientError as e:
        print(f'[ERROR] DynamoDB get_item failed: {e}')
        return build_response(500, {'error': 'Failed to fetch recipe'})


def update_recipe(recipe_id, event):
    """PUT /recipes/{id} - Update specified fields of an existing recipe."""
    body = parse_body(event)
    if not body:
        return build_response(400, {'error': 'Request body is empty'})

    try:
        existing = table.get_item(Key={'recipeId': recipe_id})
        if 'Item' not in existing:
            return build_response(404, {'error': 'Recipe not found'})
    except ClientError as e:
        print(f'[ERROR] DynamoDB get_item failed: {e}')
        return build_response(500, {'error': 'Failed to fetch recipe for update'})

    protected_fields = {'recipeId', 'createdAt'}
    body['updatedAt'] = datetime.now(timezone.utc).isoformat()

    update_parts = []
    expression_names = {}
    expression_values = {}

    for key, value in body.items():
        if key in protected_fields:
            continue
        attr_name = f'#f_{key}'
        attr_value = f':v_{key}'
        update_parts.append(f'{attr_name} = {attr_value}')
        expression_names[attr_name] = key
        expression_values[attr_value] = value

    if not update_parts:
        return build_response(400, {'error': 'No updatable fields provided'})

    update_expression = 'SET ' + ', '.join(update_parts)

    try:
        response = table.update_item(
            Key={'recipeId': recipe_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        return build_response(200, {'recipe': response['Attributes']})
    except ClientError as e:
        print(f'[ERROR] DynamoDB update_item failed: {e}')
        return build_response(500, {'error': 'Failed to update recipe'})


def delete_recipe(recipe_id):
    """DELETE /recipes/{id} - Delete a recipe and its S3 image."""
    try:
        response = table.get_item(Key={'recipeId': recipe_id})
        recipe = response.get('Item')
        if not recipe:
            return build_response(404, {'error': 'Recipe not found'})
    except ClientError as e:
        print(f'[ERROR] DynamoDB get_item failed: {e}')
        return build_response(500, {'error': 'Failed to fetch recipe for deletion'})

    image_key = recipe.get('imageKey')
    if image_key:
        delete_image_from_s3(image_key)

    try:
        table.delete_item(Key={'recipeId': recipe_id})

        # Send SNS notification about deleted recipe
        publish_sns_notification(
            f'Recipe Deleted: {recipe.get("title", "Unknown")}',
            f'A recipe has been removed from CloudChef.\n\nTitle: {recipe.get("title", "Unknown")}'
        )

        return build_response(200, {'message': 'Recipe deleted successfully', 'recipeId': recipe_id})
    except ClientError as e:
        print(f'[ERROR] DynamoDB delete_item failed: {e}')
        return build_response(500, {'error': 'Failed to delete recipe'})


def subscribe_email(event):
    """POST /subscribe - Subscribe an email address to recipe notifications."""
    body = parse_body(event)
    email = body.get('email', '')
    if not email or '@' not in str(email):
        return build_response(400, {'error': 'Valid email address is required'})

    if not SNS_TOPIC_ARN:
        return build_response(500, {'error': 'Notification service not configured'})

    try:
        response = sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=str(email),
            ReturnSubscriptionArn=True
        )
        return build_response(200, {
            'message': f'Confirmation email sent to {email}. Please check your inbox and confirm the subscription.',
            'subscriptionArn': response.get('SubscriptionArn', 'pending confirmation')
        })
    except ClientError as e:
        print(f'[ERROR] SNS subscribe failed: {e}')
        return build_response(500, {'error': 'Failed to subscribe email'})


def get_subscription_count():
    """GET /subscribers - Get the count of confirmed subscribers."""
    if not SNS_TOPIC_ARN:
        return build_response(200, {'count': 0})

    try:
        response = sns.get_topic_attributes(TopicArn=SNS_TOPIC_ARN)
        count = int(response['Attributes'].get('SubscriptionsConfirmed', 0))
        return build_response(200, {'count': count})
    except ClientError as e:
        print(f'[ERROR] SNS get_topic_attributes failed: {e}')
        return build_response(200, {'count': 0})


def analyze_image(event):
    """POST /recipes/analyze-image - Upload image to S3 and run Rekognition."""
    body = parse_body(event)
    image_base64 = body.get('image')
    if not image_base64:
        return build_response(400, {'error': 'image (base64 string) is required'})

    image_key = f'analysis/{uuid.uuid4()}.jpg'
    uploaded_key = upload_image_to_s3(image_base64, image_key)
    if not uploaded_key:
        return build_response(500, {'error': 'Failed to upload image for analysis'})

    labels = detect_labels_from_s3(uploaded_key)

    return build_response(200, {
        'labels': labels,
        'imageKey': uploaded_key,
        'imageUrl': f'https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{uploaded_key}'
    })


# ===========================================================================
# Main Lambda handler - routes requests to the correct handler function
# ===========================================================================

def lambda_handler(event, context):
    """Entry point for AWS Lambda. Routes API Gateway requests to handlers."""
    print(f'[INFO] Received event: {json.dumps(event)}')

    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters') or {}

    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return build_response(200, {'message': 'CORS preflight OK'})

    # Route: POST /recipes/analyze-image (must be before /recipes/{id})
    if http_method == 'POST' and path == '/recipes/analyze-image':
        return analyze_image(event)

    # Route: POST /subscribe
    if http_method == 'POST' and path == '/subscribe':
        return subscribe_email(event)

    # Route: GET /subscribers
    if http_method == 'GET' and path == '/subscribers':
        return get_subscription_count()

    # Route: GET /recipes
    if http_method == 'GET' and path == '/recipes':
        return get_all_recipes()

    # Route: POST /recipes
    if http_method == 'POST' and path == '/recipes':
        return create_recipe(event)

    # Routes that require a recipe ID
    recipe_id = path_parameters.get('id')
    if not recipe_id:
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'recipes':
            recipe_id = parts[1]

    if not recipe_id:
        return build_response(400, {'error': 'Recipe ID is required'})

    # Route: GET /recipes/{id}
    if http_method == 'GET':
        return get_recipe(recipe_id)

    # Route: PUT /recipes/{id}
    if http_method == 'PUT':
        return update_recipe(recipe_id, event)

    # Route: DELETE /recipes/{id}
    if http_method == 'DELETE':
        return delete_recipe(recipe_id)

    return build_response(404, {'error': 'Route not found', 'method': http_method, 'path': path})
