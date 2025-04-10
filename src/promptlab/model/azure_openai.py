import time
import asyncio
from openai import AzureOpenAI
from openai import AsyncAzureOpenAI

from promptlab.model.model import Model
from promptlab.types import InferenceResult, ModelConfig


class AzOpenAI(Model):

    def __init__(self, model_config: ModelConfig):

        super().__init__(model_config)

        self.model_config = model_config
        self.client = AzureOpenAI(
            api_key=model_config.api_key,
            api_version=model_config.api_version,
            azure_endpoint=str(model_config.endpoint)
        )

        self.async_client = AsyncAzureOpenAI(
            api_key=model_config.api_key,
            api_version=model_config.api_version,
            azure_endpoint=str(model_config.endpoint)
        )

    def invoke(self, system_prompt: str, user_prompt: str):

        payload = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        start_time = time.time()

        chat_completion = self.client.chat.completions.create(
            model=self.model_config.inference_model_deployment,
            messages=payload
        )

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        inference = chat_completion.choices[0].message.content
        prompt_token = chat_completion.usage.prompt_tokens
        completion_token = chat_completion.usage.completion_tokens

        return InferenceResult(
            inference=inference,
            prompt_tokens=prompt_token,
            completion_tokens=completion_token,
            latency_ms=latency_ms
        )

    async def ainvoke(self, system_prompt: str, user_prompt: str) -> InferenceResult:
        """
        Asynchronous invocation of the Azure OpenAI model
        """
        payload = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        start_time = time.time()

        chat_completion = await self.async_client.chat.completions.create(
            model=self.model_config.inference_model_deployment,
            messages=payload
        )

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        inference = chat_completion.choices[0].message.content
        prompt_token = chat_completion.usage.prompt_tokens
        completion_token = chat_completion.usage.completion_tokens

        return InferenceResult(
            inference=inference,
            prompt_tokens=prompt_token,
            completion_tokens=completion_token,
            latency_ms=latency_ms
        )