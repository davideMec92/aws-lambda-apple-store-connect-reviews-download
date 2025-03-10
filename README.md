# AWS LAMBDA apple-store-connect-reviews-download
AWS Lambda script for download application reviews using Apple Store connect API

# Introduction
This script refers to these links:
- Medium https://medium.com/@bhatia.sandeep/importing-python-libraries-in-aws-lambda-f6e8b2a31a24
- Dev.to https://dev.to/hasone/generate-jwt-token-for-apple-store-connect-api-using-python-3j5h

This is a Python script that runs with Python version 3.9.x, so you need to create a new aws lambda based on Python 3.9.
After you need to generate an API KEY from Apple store connect and put the .p8 file into a valid location into the lambda project.

# Env variables
In the script you can see the following environment variables:
- APP_STORE_KEY_ID: Use your Key ID you get from App Store Connect
- KEY_ISSUER_ID: similar to a UUID, use your Issuer ID you get from App Store Connect
- MOBILE_APP_ID: is a numeric value that identify you application, you can find it in apple store connect
- PRIVATE_KEY_PATH: the path where that .p8 file is located in your lambda project
- REQUEST_SECRET_TOKEN: this is a secret token to authorize the request

Environment variables must be defined in the lambda environment section.

# Layer
In order to use imported libraries you need to add a layer to your lambda. I used this article: https://medium.com/@bhatia.sandeep/importing-python-libraries-in-aws-lambda-f6e8b2a31a24, so this is the way I found:
1. Start an EC2 instance with AWS Linux AMI
2. Connect to console with ssh
3. Check that Python 3.9 is the installed version
4. Start python env with: ```python3 -m venv venv_pytz```
5. Enable python env with: ```source venv_pytz/bin/activate```
6. Create a folder "python", with: ```mkdir python```
7. Install libraries into "python" folder with: ```pip3 install requests cryptography==3.4.8 pyjwt python-csv==0.0.10 -t python```
8. Make a zip file of "python" folder with: ```zip -r python.zip python/*```
9. Deactivate python virtual env with: ```deactivate```
10. Download zip file from EC2 with scp: ```scp -i <your_ssh_key>.pem ec2-user@<your_ec2_istance_address>:/home/ec2-user/python.zip .```
11. Upload python.zip to S3 bucket (Important! You need to upload the zip file into a bucket that is in the same aws region of your lambda)
12. Go to Lambda > Layers
13. Create new layer and select upload from S3, copy and past the address of the uplaoded .zip file
14. Select the language version to Python 3.9 and choose the lambda architecture
15. Create layer
16. Go to your lambda function, select layers and add the created layer with its version

# Call lambda
1. To call your lambda use the syntax: ```<your_lambda_enpoint_address>/?secret=<your_env_secret>&fetchAll=<true|false>```
2. You should see the CSV file download starting from your browser
