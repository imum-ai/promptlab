import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath('./src'))

@pytest.fixture
def mock_model_config():
    """Create a mock model config for testing"""
    from promptlab.types import ModelConfig
    
    return ModelConfig(
        type="mock",
        inference_model_deployment="mock-model",
        embedding_model_deployment="mock-model"
    )

@pytest.fixture
def mock_tracer():
    """Create a mock tracer for testing"""
    tracer = MagicMock()
    tracer.db_client.fetch_data.return_value = [{"asset_binary": "system: test\nuser: test", "file_path": "test.jsonl"}]
    return tracer

@pytest.fixture
def mock_experiment_config():
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
