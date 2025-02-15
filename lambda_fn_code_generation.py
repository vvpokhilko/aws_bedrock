import boto3  # AWS SDK for interacting with AWS services
import botocore.config  # Configuration options for boto3 clients
import json  # Library for handling JSON data
from datetime import datetime  # For generating timestamps


def generate_code_using_bedrock(message: str, language: str) -> str:
    """
    Generates code using Amazon Bedrock's Claude-v2 model based on the given message and language.
    """
    prompt_text = f"""Human: Write {language} code for the following instructions: {message}.
    Assistant: 
    """
    body = {
        "prompt": prompt_text,  # Input prompt for the AI model
        "max_tokens_to_sample": 2048,  # Maximum token output limit
        "temperature": 0.1,  # Controls randomness (lower values = more deterministic output)
        "top_k": 250,  # Limits the model's choices to the top-k likely tokens
        "top_p": 0.2,  # Nucleus sampling probability threshold
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
        
        # Extract the generated code from the response
        response_content = response.get('body').read().decode('utf-8')
        response_data = json.loads(response_content)
        code = response_data['completion'].strip()
        return code

    except Exception as e:
        print(f"Error generating the code: {e}")
        return ""


def save_code_to_s3_bucket(code, s3_bucket, s3_key):
    """
    Saves the generated code to an Amazon S3 bucket.
    """
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=code)
        print(f"Code saved to S3 bucket: {s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving code to S3 bucket: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler function to generate code using Bedrock and save it to S3.
    """
    event = json.loads(event['body'])
    
    # Extract the message and programming language from the event payload
    message = event['message']
    language = event['key']  # 'key' represents the programming language
    print(message, language)

    # Generate code using Bedrock AI
    generated_code = generate_code_using_bedrock(message, language)

    # Save the generated code to an S3 bucket if successful
    if generated_code:
        current_time = datetime.now().strftime("%H%M%S")  # Generate a timestamp for the filename
        s3_bucket = 'bedrock-projects-bucket'  # Define the target S3 bucket
        s3_key = f'code-output/{current_time}.py'  # Define the S3 object key (file path)
        save_code_to_s3_bucket(generated_code, s3_bucket, s3_key)
    else:
        print("Failed to generate code.")

    # Return a response indicating the completion of the process
    return {
        'statusCode': 200,  # HTTP success status
        'body': json.dumps('Code generation completed')  # Response message
    }
