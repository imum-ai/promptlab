import ollama
import asyncio
import time

from promptlab.model.model import Model
from promptlab.types import InferenceResult, ModelConfig

class Ollama(Model):

    def __init__(self, model_config: ModelConfig):

        super().__init__(model_config)

        self.model_config = model_config
        self.client = ollama

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

        chat_completion = self.client.chat(
            model=self.model_config.inference_model_deployment,
            messages=payload
        )

        latency_ms = chat_completion.total_duration
        inference = chat_completion.message.content
        prompt_token = chat_completion.eval_count
        completion_token = chat_completion.prompt_eval_count

        return InferenceResult(
            inference=inference,
            prompt_tokens=prompt_token,
            completion_tokens=completion_token,
            latency_ms=latency_ms
        )

    async def ainvoke(self, system_prompt: str, user_prompt: str) -> InferenceResult:
        """
        Asynchronous invocation of the Ollama model
        Note: Ollama doesn't have a native async API, so we run it in a thread pool
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

        # Run the synchronous Ollama call in a thread pool
        loop = asyncio.get_event_loop()
        chat_completion = await loop.run_in_executor(
            None,
            lambda: self.client.chat(
                model=self.model_config.inference_model_deployment,
                messages=payload
            )
        )

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        inference = chat_completion.message.content
        prompt_token = chat_completion.eval_count
        completion_token = chat_completion.prompt_eval_count

        return InferenceResult(
            inference=inference,
            prompt_tokens=prompt_token,
            completion_tokens=completion_token,
            latency_ms=latency_ms
        )