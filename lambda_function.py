import json
import requests
import csv
import time
import jwt
import os
import base64
import io

def lambda_handler(event, context):

    print("query string parameters: " + json.dumps(event['queryStringParameters']))

    if(event['queryStringParameters']['secret'] is None or event['queryStringParameters']['secret'] != os.environ['REQUEST_SECRET_TOKEN']):
        return {
            'statusCode': 401,
            'body': 'FORBIDDEN'
        }

    fetch_all = False

    if event['queryStringParameters']['fetchAll'] is not None:
        fetch_all = event['queryStringParameters']['fetchAll'] == 'true'

    key_id = os.environ['APP_STORE_KEY_ID']  # Use your Key ID you get from App Store Connect
    issuer_id = os.environ['KEY_ISSUER_ID']  # Use your Issuer ID you get from App Store Connect
    private_key_path = os.environ['PRIVATE_KEY_PATH']  # The path of your AutKey you have downloaded from App Store Connect
    app_id = os.environ['MOBILE_APP_ID']

    jwt_token = generate_token(key_id, issuer_id, private_key_path)
    print('get jwt token: ' + jwt_token)

    reviews = get_reviews(app_id, jwt_token, fetch_all)
    
    csv = ""
    filename = 'appstore_reviews.csv'

    if reviews:
        print('Reviews type: ' + str(type(reviews)))
        csv = save_to_csv(reviews)
        """ if output_format in ('json', 'both'):
            save_to_json(reviews)
        if output_format in ('csv', 'both'):
            save_to_csv(reviews)"""
    else:
        print("No reviews fetched.")
    
    return {
        "statusCode":200, 
            "headers":{
                "Content-Type":"text/csv",
                "Content-Disposition":"attachment;filename={}".format(filename) 
            },
        "body": base64.b64encode(csv.encode()).decode("utf-8"),
        "isBase64Encoded": True
    }

def generate_token(key_id, issuer_id, private_key_path):
    with open(private_key_path, 'r') as key_file:
        private_key = key_file.read()

    headers = {
        "alg": "ES256",
        "kid": key_id,
        "typ": "JWT"
    }

    payload = {
        "iss": issuer_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 20 * 60, # 60 minutes
        "aud": "appstoreconnect-v1"
    }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token

def get_reviews(app_id, jwt_token, fetch_all):
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/customerReviews?limit=200&sort=-createdDate"
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    all_reviews = []
    total_reviews = None
    fetched_reviews = 0

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.text)
            return []

        data = response.json()

        # Get the total number of reviews from the meta field if not already obtained
        if total_reviews is None:
            total_reviews = data.get('meta', {}).get('paging', {}).get('total', None)

        all_reviews.extend(data['data'])
        fetched_reviews += len(data['data'])

        # Show progress
        if total_reviews:
            print(
                f"Fetched {fetched_reviews} of {total_reviews} reviews ({(fetched_reviews / total_reviews) * 100:.2f}%)")

        if fetch_all is False:
            break

        # Check if there's a next page
        url = data.get('links', {}).get('next', None)

    return all_reviews


def save_to_csv(reviews):
    output = io.StringIO()
    writer = csv.writer(output)
    # Write the header
    writer.writerow(['id', 'rating', 'title', 'body', 'reviewerNickname', 'createdDate', 'territory'])
    # Write the data
    for review in reviews:
        attributes = review['attributes']
        writer.writerow([
            review['id'],
            attributes.get('rating'),
            attributes.get('title'),
            attributes.get('body'),
            attributes.get('reviewerNickname'),
            attributes.get('createdDate'),
            attributes.get('territory')
        ])
    return output.getvalue()
