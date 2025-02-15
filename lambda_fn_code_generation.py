import boto3
import botocore.config
import json
from datetime import datetime


def generate_code_using_bedrock(message: str, language: str) -> str:
    prompt_text = f"""Human: Write {language} code for the following instructions: {message}.
    Assistant: 
    """
    body = {
        "prompt": prompt_text,
        "max_tokens_to_sample": 2048,
        "temperature": 0.1,
        "top_k": 250,
        "top_p": 0.2,
        "stop_sequences": ["\n\nHuman:"]
    }

    try:
        bedrock = boto3.client('bedrock-runtime',
                               region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300,
                                                             retries={'max_attempts': 3})
                               )
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId='anthropic.claude-v2',
        )
        response_content = response.get('body').read().decode('utf-8')
        response_data = json.loads(response_content)
        code = response_data['completion'].strip()
        return code

    except Exception as e:
        print(f"Error generating the code: {e}")
        print("")


def save_code_to_s3_bucket(code, s3_bucket, s3_key):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=code)
        print(f"Code saved to S3 bucket: {s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving code to S3 bucket: {e}")
        print("")


def lambda_handler(event, context):
    event = json.loads(event['body'])
    # Extract the message from the event
    message = event['message']
    language = event['key']
    print(message, language)

    # Generate code using Bedrock
    generated_code = generate_code_using_bedrock(message, language)

    # Save the generated code to S3 bucket
    if generated_code:
        current_time = datetime.now().strftime("%H%M%S")
        s3_bucket = 'bedrock-projects-bucket'
        s3_key = f'code-output/{current_time}.py'
        save_code_to_s3_bucket(generated_code, s3_bucket, s3_key)
    else:
        print("Failed to generate code.")

    # Return the generated code
    return {
        'statusCode': 200,
        'body': json.dumps('Code generation completed')
        # 'body': json.dumps(generated_code)
    }

