# AWS Bedrock
## **1. AI-Generated Image Creation and Storage**
**Project Summary**:
This project implements an AWS Lambda function that generates AI-generated images using the Stable Diffusion XL v1 model from Amazon Bedrock. The function processes user input received through an API Gateway POST request, sends the request to Bedrock for image generation, and decodes the base64-encoded response. The generated image is then stored in an Amazon S3 bucket for later retrieval.

**Workflow**:

1. Receives a request via API Gateway containing a text prompt for the image.
2. Invokes the Bedrock Stable Diffusion XL model with the provided text prompt.
3. Processes the response, extracts the generated image, and decodes it from base64.
4. Saves the image to an S3 bucket with a timestamped filename.
5. Returns a success message indicating the image has been saved.
   
**Technologies Used**:

* AWS Lambda
* Amazon Bedrock (Stable Diffusion XL v1)
* API Gateway
* Amazon S3
* Python (boto3, JSON, base64)

------------------------------------------------------------------------------------------------

## **2. AI-Powered Code Generation and Storage**
**Project Summary:**

This project enables AI-powered code generation using Anthropic Claude v2 via Amazon Bedrock. The Lambda function processes user input (programming instructions and language preference), requests AI-generated code, and stores the output in an Amazon S3 bucket for future use. The function is accessible via an API Gateway POST request.

**Workflow**:

1. Receives a POST request containing user instructions and the desired programming language.
2. Formats a prompt and sends it to Amazon Bedrock (Claude v2) for code generation.
3. Processes the AI-generated response and extracts the completed code.
4. Stores the code in an S3 bucket with a timestamped filename.
5. Returns a confirmation message indicating successful storage.

**Technologies Used**:

* AWS Lambda
* Amazon Bedrock (Claude v2)
* API Gateway
* Amazon S3
* Python (boto3, JSON)

--------------------------------------------------------------------------------------------------

## **3. AI-Powered Text Summarization**
**Project Summary**:

This Lambda function automates the extraction and summarization of text content (fake meeting minutes) using Anthropic Claude v2 via Amazon Bedrock. The function receives an encoded file as a POST request via API Gateway, extracts text from the file, generates a summary, and stores the output in an Amazon S3 bucket for later retrieval.

**Workflow**:

1. Receives a base64-encoded email via an API Gateway POST request.
2. Extracts text content from the file, handling both plain text and multipart formats.
3. Formats a summarization prompt and sends it to Amazon Bedrock (Claude v2).
4. Processes the AI-generated summary and stores it in an S3 bucket with a timestamped filename.
5. Returns a success message indicating completion.

**Technologies Used**:

* AWS Lambda
* Amazon Bedrock (Claude v2)
* API Gateway
* Amazon S3
* Python (boto3, JSON, base64, email module)

Each of these projects leverages **AWS Lambda**, **API Gateway**, and **Amazon Bedrock** to enable AI-powered automation for different use cases: image generation, code generation, and text summarization. 

