import asyncio
import time
import sys
import os
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath('./src'))

class MockModel:
    """A mock model for testing async functionality"""

    async def ainvoke(self, system_prompt, user_prompt):
        """Async invocation that simulates a delay"""
        await asyncio.sleep(0.5)  # Simulate network delay
        return {
            "inference": f"Response to: {user_prompt}",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "latency_ms": 500
        }

    def invoke(self, system_prompt, user_prompt):
        """Synchronous invocation"""
        time.sleep(0.5)  # Simulate network delay
        return {
            "inference": f"Response to: {user_prompt}",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "latency_ms": 500
        }

@pytest.mark.asyncio
async def test_parallel_execution():
    """Test that async execution is faster than synchronous execution"""
    print("Testing parallel execution...")

    # Create test data
    prompts = [f"Test prompt {i}" for i in range(10)]
    model = MockModel()

    # Test synchronous execution
    start_time = time.time()
    sync_results = []
    for prompt in prompts:
        result = model.invoke("System prompt", prompt)
        sync_results.append(result)
    sync_time = time.time() - start_time

    # Test asynchronous execution
    start_time = time.time()
    tasks = []
    for prompt in prompts:
        task = model.ainvoke("System prompt", prompt)
        tasks.append(task)
    async_results = await asyncio.gather(*tasks)
    async_time = time.time() - start_time

    print(f"Synchronous execution time: {sync_time:.2f} seconds")
    print(f"Asynchronous execution time: {async_time:.2f} seconds")

    # Async should be significantly faster
    if async_time < sync_time / 2:
        print("✅ Async execution is at least 2x faster than synchronous execution")
        return True
    else:
        print("❌ Async execution is not significantly faster")
        return False

@pytest.mark.asyncio
async def main():
    """Run the tests"""
    print("Testing async implementation...")

    # Test parallel execution
    parallel_ok = await test_parallel_execution()
    if not parallel_ok:
        return

    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
