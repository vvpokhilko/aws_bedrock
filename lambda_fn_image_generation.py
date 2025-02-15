import json
import boto3
import botocore
from datetime import datetime
import base64

def lambda_handler(event, context):

    event = json.loads(event['body'])
    message = event['message']

    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        config=botocore.config.Config(
            read_timeout=300,
            retries={"max_attempts":5}
        )
    )

    s3 = boto3.client('s3')

    payload = {
        "text_prompts": [{"text": message}],
        "cfg_scale": 10,
        "seed": 0,
        "steps": 50
    }

    response = bedrock.invoke_model(
        body=json.dumps(payload),
        modelId="stability.stable-diffusion-xl-v1",
        accept='application/json',
        contentType='application/json'
    )

    response_body = json.loads(response.get('body').read())
    base_64_img_str = response_body["artifacts"][0].get('base64')
    image_content = base64.decodebytes(bytes(base_64_img_str,'utf-8'))

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S') # UTC time, not necessarily your timezone
    s3_bucket = 'bedrock-projects-bucket'
    s3_key = f"images-output/{current_time}.png"

    s3.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=image_content,
        ContentType='image/png'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Image saved to s3')
    }
