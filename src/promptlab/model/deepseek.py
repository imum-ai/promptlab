import time
from openai import OpenAI
from openai import AsyncOpenAI

from promptlab.model.model import Model
from promptlab.types import InferenceResult, ModelConfig


class DeepSeek(Model):
    def __init__(self, model_config: ModelConfig):
        super().__init__(model_config)

        self.model_config = model_config
        self.deployment = model_config.inference_model_deployment
        self.client = OpenAI(api_key=model_config.api_key, base_url=str(model_config.endpoint))
        self.async_client = AsyncOpenAI(api_key=model_config.api_key, base_url=str(model_config.endpoint))

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
        chat_completion = self.client.chat.completions.create(
            model=self.deployment,
            messages=payload
        )
        inference = chat_completion.choices[0].message.content
        prompt_token = chat_completion.usage.prompt_tokens
        completion_token = chat_completion.usage.completion_tokens

        # Calculate latency
        latency_ms = 0  # Not provided by the API directly

        return InferenceResult(
            inference=inference,
            prompt_tokens=prompt_token,
            completion_tokens=completion_token,
            latency_ms=latency_ms
        )

    async def ainvoke(self, system_prompt: str, user_prompt: str) -> InferenceResult:
        """
        Asynchronous invocation of the DeepSeek model
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
            model=self.deployment,
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