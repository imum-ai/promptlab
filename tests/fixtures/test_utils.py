import asyncio
import time
from unittest.mock import MagicMock

class MockModel:
    """A mock model for testing async functionality"""
    
    async def ainvoke(self, system_prompt, user_prompt):
        """Async invocation that simulates a delay"""
        await asyncio.sleep(0.1)  # Simulate network delay
        return {
            "inference": f"Response to: {user_prompt}",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "latency_ms": 100
        }
    
    def invoke(self, system_prompt, user_prompt):
        """Synchronous invocation"""
        time.sleep(0.1)  # Simulate network delay
        return {
            "inference": f"Response to: {user_prompt}",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "latency_ms": 100
        }

def create_mock_experiment_config():
    """Create a mock experiment config for testing"""
    config = MagicMock()
    config.prompt_template = MagicMock()
    config.prompt_template.name = "test"
    config.prompt_template.version = "1.0"
    config.dataset = MagicMock()
    config.dataset.name = "test"
    config.dataset.version = "1.0"
    config.evaluation = []
    config.model = MagicMock()
    return config

def create_mock_tracer():
    """Create a mock tracer for testing"""
    tracer = MagicMock()
    tracer.db_client.fetch_data.return_value = [{"asset_binary": "system: test\nuser: test", "file_path": "test.jsonl"}]
    return tracer
