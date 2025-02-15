import json  # Library for handling JSON data
import boto3  # AWS SDK for Python to interact with AWS services
import botocore.config  # Provides configuration options for boto3 clients
import base64  # Library for encoding/decoding base64 data
from datetime import datetime  # For generating timestamps
from email import message_from_bytes  # For parsing email messages

def extract_text_from_multipart(data):
    """
    Extracts plain text content from a multipart email message.
    """
    msg = message_from_bytes(data)
    text_content = ''

    if msg.is_multipart():
        # Iterate through all parts of the email message
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':  # Check if the content is plain text
                text_content += part.get_payload(decode=True).decode('utf-8') + '\n'
    else:
        # If the message is not multipart, extract plain text directly
        if msg.get_content_type() == 'text/plain':
            text_content = msg.get_payload(decode=True).decode('utf-8')

    return text_content.strip() if text_content else None  # Return extracted text or None if empty


def generate_summary_from_bedrock(content: str) -> str:
    """
    Generates a summary of the given content using Amazon Bedrock's Claude-v2 model.
    """
    prompt_text = f"""Human: Summarize the main points made by Andrej Karpathy in the following document: {content}
    Assistant:"""

    body = {
        "prompt": prompt_text,  # Input prompt for the AI model
        "max_tokens_to_sample": 5000,  # Maximum token output limit
        "temperature": 0.1,  # Controls randomness (lower values = more deterministic output)
        "top_p": 0.2,  # Nucleus sampling probability threshold
        "top_k": 250,  # Limits the model's choices to the top-k likely tokens
        "stop_sequences": ["\n\nHuman:"]  # Defines stop sequences to terminate generation
    }

    try:
        # Initialize the Bedrock client
        bedrock = boto3.client('bedrock-runtime',
                                region_name="us-east-1",
                                config=botocore.config.Config(read_timeout=300,
                                                              retries={'max_attempts': 3})
                                )
        # Invoke the Bedrock model with the constructed payload
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId='anthropic.claude-v2',
        )
        
        # Extract the generated summary from the response
        response_content = response.get('body').read().decode('utf-8')
        response_data = json.loads(response_content)
        summary = response_data['completion'].strip()
        return summary

    except Exception as e:
        print(f"Error generating the summary: {e}")
        return ""


def save_summary_to_s3_bucket(summary, s3_bucket, s3_key):
    """
    Saves the generated summary to an Amazon S3 bucket.
    """
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=summary)
        print(f"Summary saved to S3 bucket: {s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving the summary to S3 bucket: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler function to process an email, generate a summary, and store it in S3.
    """
    # Decode the base64-encoded request body
    decoded_body = base64.b64decode(event['body'])

    # Extract plain text content from the email
    text_content = extract_text_from_multipart(decoded_body)

    if not text_content:
        return {
            'statusCode': 400,
            'body': json.dumps('Failed to extract content')
        }

    # Generate summary using Bedrock AI
    summary = generate_summary_from_bedrock(text_content)

    if summary:
        # Generate a timestamp for the summary filename
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
        s3_bucket = 'bedrock-projects-bucket'  # Define the target S3 bucket
        s3_key = f"summary-output/{current_time}.txt"  # Define the S3 object key (file path)
        save_summary_to_s3_bucket(summary, s3_bucket, s3_key)
    else:
        print("No summary was generated")

    # Return a response indicating the completion of the process
    return {
        'statusCode': 200,  # HTTP success status
        'body': json.dumps('Summary generation finished')  # Response message
    }
