"""
AWS Bedrock Client Wrapper

Simplifies calling Claude on AWS Bedrock
"""

import boto3
import botocore.exceptions
import json
import os
from typing import Dict, List, Optional
import logging

from src.resilience import RetryHandler, RetryConfig

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Wrapper for AWS Bedrock Runtime

    Makes it easy to call Claude models on Bedrock
    """

    def __init__(
        self,
        region_name: str = None,
        model_id: str = None
    ):
        """
        Initialize Bedrock client

        Args:
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var)
            model_id: Model to use (defaults to BEDROCK_MODEL env var)
        """
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.model_id = model_id or os.getenv(
            'BEDROCK_MODEL',
            'us.anthropic.claude-3-5-haiku-20241022-v1:0'
        )

        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name
            )
            logger.info(f"Bedrock client initialized: {self.model_id} in {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

        # Retry handler for transient API errors
        self._retry_handler = RetryHandler(RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            retryable_exceptions=(
                botocore.exceptions.ReadTimeoutError,
                botocore.exceptions.ConnectTimeoutError,
                self.client.exceptions.ThrottlingException,
                self.client.exceptions.ServiceUnavailableException,
            ),
        ))

    def invoke(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Dict:
        """
        Invoke Claude model on Bedrock

        Args:
            messages: List of messages (role + content)
            system: System prompt (instructions)
            max_tokens: Max tokens to generate
            temperature: Creativity (0-1)

        Returns:
            {
                'content': str (response text),
                'usage': {
                    'input_tokens': int,
                    'output_tokens': int
                },
                'stop_reason': str
            }
        """
        # Build request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        # Add system prompt if provided
        if system:
            body["system"] = system

        try:
            # Call Bedrock with retry on transient errors
            response = self._retry_handler.execute_with_retry(
                self.client.invoke_model,
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract text
            content = response_body['content'][0]['text']

            # Return structured response
            result = {
                'content': content,
                'usage': response_body['usage'],
                'stop_reason': response_body.get('stop_reason', 'end_turn'),
            }

            # Attach retry info if retries occurred
            if self._retry_handler.retry_history:
                result['retries'] = list(self._retry_handler.retry_history)
                self._retry_handler.retry_history.clear()

            return result

        except Exception as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise

    def invoke_with_system(
        self,
        user_message: str,
        system_prompt: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Simple helper: invoke with system prompt and single user message

        Args:
            user_message: What to ask
            system_prompt: Instructions for Claude
            max_tokens: Max response length

        Returns:
            Response text
        """
        messages = [
            {"role": "user", "content": user_message}
        ]

        result = self.invoke(
            messages=messages,
            system=system_prompt,
            max_tokens=max_tokens
        )

        return result['content']


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    client = BedrockClient()

    response = client.invoke_with_system(
        user_message="Say 'Bedrock client is working!' and nothing else.",
        system_prompt="You are a helpful assistant."
    )

    print(f"[OK] Response: {response}")
