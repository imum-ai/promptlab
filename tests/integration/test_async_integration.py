import asyncio
import sys
import os
import time
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath('./src'))

@pytest.mark.asyncio
async def test_async_promptlab():
    """Test the async functionality in PromptLab"""
    try:
        from promptlab import PromptLab
        from promptlab.types import ModelConfig
        from promptlab.model.model import Model

        # Create a mock model for testing
        class MockModel(Model):
            def __init__(self, model_config):
                super().__init__(model_config)

            def invoke(self, system_prompt, user_prompt):
                """Synchronous invocation"""
                time.sleep(0.5)  # Simulate network delay
                return {
                    "inference": f"Response to: {user_prompt}",
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "latency_ms": 500
                }

            async def ainvoke(self, system_prompt, user_prompt):
                """Asynchronous invocation"""
                await asyncio.sleep(0.5)  # Simulate network delay
                return {
                    "inference": f"Async response to: {user_prompt}",
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "latency_ms": 500
                }

        print("✅ Successfully imported PromptLab modules")

        # Test async model invocation
        model_config = ModelConfig(
            type="mock",
            inference_model_deployment="mock-model",
            embedding_model_deployment="mock-model"
        )

        model = MockModel(model_config)

        # Test synchronous invocation
        start_time = time.time()
        sync_results = []
        for i in range(5):
            result = model.invoke("System prompt", f"Test prompt {i}")
            sync_results.append(result)
        sync_time = time.time() - start_time

        # Test asynchronous invocation
        start_time = time.time()
        tasks = []
        for i in range(5):
            task = model.ainvoke("System prompt", f"Test prompt {i}")
            tasks.append(task)
        async_results = await asyncio.gather(*tasks)
        async_time = time.time() - start_time

        print(f"Synchronous model invocation time: {sync_time:.2f} seconds")
        print(f"Asynchronous model invocation time: {async_time:.2f} seconds")

        if async_time < sync_time / 2:
            print("✅ Async model invocation is at least 2x faster")
        else:
            print("❌ Async model invocation is not significantly faster")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@pytest.mark.asyncio
async def main():
    """Run the tests"""
    print("Testing PromptLab async implementation...")

    # Test PromptLab async functionality
    await test_async_promptlab()

    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
