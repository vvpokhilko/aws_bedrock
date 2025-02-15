import json  # Library for handling JSON data
import boto3  # AWS SDK for Python to interact with AWS services
import botocore  # Provides configuration options for boto3 clients
from datetime import datetime  # For generating timestamps
import base64  # Library for encoding/decoding base64 data

def lambda_handler(event, context):
    # Parse the incoming event body (assumed to be a JSON string)
    event = json.loads(event['body'])
    message = event['message']  # Extract the message text from the event

    # Initialize the Bedrock client for interacting with Amazon Bedrock's runtime
    bedrock = boto3.client(
        service_name='bedrock-runtime',  # Specify the AWS service
        region_name='us-east-1',  # Define the AWS region
        config=botocore.config.Config(
            read_timeout=300,  # Set the read timeout to 300 seconds (5 minutes)
            retries={"max_attempts": 5}  # Configure retry mechanism
        )
    )

    # Initialize the S3 client for uploading the generated image
    s3 = boto3.client('s3')

    # Define the payload for the Bedrock model
    payload = {
        "text_prompts": [{"text": message}],  # Provide user input as a text prompt
        "cfg_scale": 10,  # Control how strongly the model follows the prompt (higher = stricter adherence)
        "seed": 0,  # Set seed for deterministic output (0 means random seed)
        "steps": 50  # Number of inference steps (higher = better quality but slower)
    }

    # Invoke the Stable Diffusion XL model on Amazon Bedrock
    response = bedrock.invoke_model(
        body=json.dumps(payload),  # Convert payload to JSON format
        modelId="stability.stable-diffusion-xl-v1",  # Specify the model ID
        accept='application/json',  # Expect JSON response format
        contentType='application/json'  # Send JSON request format
    )

    # Parse the response to extract the base64-encoded image
    response_body = json.loads(response.get('body').read())
    base_64_img_str = response_body["artifacts"][0].get('base64')  # Extract image string
    image_content = base64.decodebytes(bytes(base_64_img_str, 'utf-8'))  # Decode base64 string into binary

    # Generate a timestamp for the image filename
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
    s3_bucket = 'bedrock-projects-bucket'  # Specify the target S3 bucket
    s3_key = f"images-output/{current_time}.png"  # Define the S3 object key (path and filename)

    # Upload the generated image to the specified S3 bucket
    s3.put_object(
        Bucket=s3_bucket,  # Target bucket name
        Key=s3_key,  # Object key (file path in the bucket)
        Body=image_content,  # Image binary content
        ContentType='image/png'  # Specify content type for proper rendering
    )

    # Return a success response
    return {
        'statusCode': 200,  # HTTP success status
        'body': json.dumps('Image saved to S3')  # Response message
    }
