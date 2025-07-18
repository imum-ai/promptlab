import asyncio
import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath("./src"))


@pytest.mark.asyncio
async def test_async_model_invocation():
    """Test async model invocation"""
    from promptlab.model.model import Model
    from promptlab.types import ModelConfig, ModelResponse

    # Create a mock model
    class MockModel(Model):
        def __init__(self, model_config):
            super().__init__(model_config)

        def invoke(self, system_prompt, user_prompt):
            """Synchronous invocation"""
            time.sleep(0.1)
            return ModelResponse(
                completion=f"Response to: {user_prompt}",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=100,
            )

        async def ainvoke(self, system_prompt, user_prompt):
            """Asynchronous invocation"""
            await asyncio.sleep(0.1)
            return ModelResponse(
                completion=f"Async response to: {user_prompt}",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=100,
            )  # Create a model config

    model_config = ModelConfig(
        model_deployment="mock-model",
    )

    # Create a model instance
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

    # Async should be significantly faster
    assert async_time < sync_time / 2

    # Check that the results are correct
    for i, result in enumerate(async_results):
        assert result.completion == f"Async response to: Test prompt {i}"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.latency_ms == 100


@pytest.mark.asyncio
async def test_experiment_async_execution():
    """Test async experiment execution"""
    from promptlab._experiment import Experiment

    # Create a mock tracer
    tracer = MagicMock()
    tracer.db_client.fetch_data.return_value = [
        {"asset_binary": "system: test\nuser: test", "file_path": "test.jsonl"}
    ]  # Create a mock dataset
    dataset = [{"id": 1, "text": "test"}]

    # Mock the Utils.load_dataset method
    with patch("promptlab._utils.Utils") as mockUtils:
        mockUtils.load_dataset.return_value = dataset
        mockUtils.split_prompt_template.return_value = (
            "system: test",
            "user: test",
            [],
        )  # Mock the ExperimentConfig validation
        with patch("promptlab._config.ExperimentConfig") as mock_config_class:
            # Make the mock return itself when called with **kwargs
            mock_instance = MagicMock()
            mock_config_class.return_value = mock_instance
            mock_instance.prompt_template.name = "test"
            mock_instance.prompt_template.version = "1.0"
            mock_instance.dataset.name = "test"
            mock_instance.dataset.version = "1.0"
            mock_instance.evaluation = []
            mock_instance.model = MagicMock()

            # Create a mock experiment config
            experiment_config = {}
            # We'll patch the validation in the Experiment class            # Create an experiment instance
            experiment = Experiment(tracer)

            # Mock the _init_batch_eval_async method (note the leading underscore)
            with patch.object(experiment, "_init_batch_eval_async") as mock_batch_eval:
                mock_batch_eval.return_value = asyncio.Future()
                mock_batch_eval.return_value.set_result([{"experiment_id": "test"}])

                # Test async run
                await experiment.run_async(experiment_config)

                # Check that init_batch_eval_async was called
                mock_batch_eval.assert_called_once()

                # Check that tracer.trace was called
                tracer.trace.assert_called_once()


@pytest.mark.asyncio
async def test_async_studio():
    """Test async studio"""
    from promptlab.studio.studio import Studio

    # Create a mock tracer config
    tracer_config = MagicMock()

    # Create a studio instance
    studio = Studio(tracer_config)

    # Mock the start_web_server method
    with patch.object(studio, "start_web_server") as mock_web_server:
        # Mock the start_api_server_async method
        with patch.object(studio, "start_api_server_async") as mock_api_server:
            mock_api_server.return_value = asyncio.Future()
            mock_api_server.return_value.set_result(None)

            # Create a task that will be cancelled
            task = asyncio.create_task(studio.start_async(8000))

            # Wait a bit for the task to start
            await asyncio.sleep(0.1)

            # Cancel the task
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Check that start_web_server was called
            mock_web_server.assert_called_once_with(8000)

            # Check that start_api_server_async was called
            mock_api_server.assert_called_once_with(8001)


@pytest.mark.asyncio
async def test_promptlab_async_methods():
    """Test PromptLab async methods"""
    from promptlab.core import PromptLab

    # Create a mock tracer config
    tracer_config = {"type": "sqlite", "db_file": ":memory:"}

    # Mock the TracerFactory
    with patch("promptlab.core.TracerFactory"):
        pass  # Explicitly do nothing with the patch context
        # Mock the ConfigValidator
        with patch("promptlab.core.ConfigValidator"):
            pass  # Explicitly do nothing with the patch context
            # Create a PromptLab instance
            promptlab = PromptLab(tracer_config)

            # Mock the experiment.run_async method
            with patch.object(promptlab.experiment, "run_async") as mock_run_async:
                mock_run_async.return_value = asyncio.Future()
                mock_run_async.return_value.set_result(None)

                # Test experiment.run_async
                experiment_config = {"test": "config"}
                await promptlab.experiment.run_async(experiment_config)

                # Check that experiment.run_async was called
                mock_run_async.assert_called_once_with(experiment_config)

            # Mock the studio.start_async method
            with patch.object(promptlab.studio, "start_async") as mock_start_async:
                mock_start_async.return_value = asyncio.Future()
                mock_start_async.return_value.set_result(None)

                # Test studio.start_async
                await promptlab.studio.start_async(8000)

                # Check that studio.start_async was called
                mock_start_async.assert_called_once_with(8000)


@pytest.mark.asyncio
async def test_model_max_concurrent_tasks():
    """Test the max_concurrent_tasks parameter in Model class"""
    from promptlab.model.model import Model
    from promptlab.types import ModelConfig, ModelResponse
    import time

    # Create a mock model with a delay
    class DelayedMockModel(Model):
        def __init__(self, model_config):
            super().__init__(model_config)
            self.invocation_times = []

        def invoke(self, system_prompt, user_prompt):
            """Synchronous invocation"""
            time.sleep(0.1)
            return ModelResponse(
                completion=f"Response to: {user_prompt}",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=100,
            )

        async def ainvoke(self, system_prompt, user_prompt):
            """Asynchronous invocation with recording start time"""
            self.invocation_times.append(time.time())
            await asyncio.sleep(0.5)  # Simulate a slow API call
            return ModelResponse(
                completion=f"Async response to: {user_prompt}",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=500,
            )

    # The test for max_concurrent_tasks is not directly testable in this way
    # because the Model class itself doesn't implement the concurrency limit
    # The concurrency limit is implemented in the Experiment class
    # So we'll just verify that the max_concurrent_tasks attribute is set correctly    # Test with default max_concurrent_tasks (5)
    model_config_default = ModelConfig(
        model_deployment="mock-model",
    )
    model_default = DelayedMockModel(model_config_default)

    # Test with custom max_concurrent_tasks (2)
    model_config_limited = ModelConfig(
        model_deployment="mock-model", max_concurrent_tasks=2
    )
    model_limited = DelayedMockModel(model_config_limited)

    # Verify that the max_concurrent_tasks attribute is set correctly
    assert model_default.max_concurrent_tasks == 5
    assert model_limited.max_concurrent_tasks == 2


@pytest.mark.asyncio
async def test_experiment_concurrency_limit():
    """Test the concurrency limit in experiment async execution"""
    from promptlab._experiment import Experiment
    from promptlab.model.model import Model
    from promptlab.types import ModelConfig, ModelResponse
    import time

    # Create a mock model with a delay and tracking
    class TrackedModel(Model):
        def __init__(self, model_config):
            super().__init__(model_config)
            self.invocation_times = []
            self.active_count = 0
            self.max_observed_concurrency = 0

        def invoke(self, system_prompt, user_prompt):
            return ModelResponse(
                completion="Test response",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=100,
            )

        async def ainvoke(self, system_prompt, user_prompt):
            # Track concurrency
            self.active_count += 1
            self.max_observed_concurrency = max(
                self.max_observed_concurrency, self.active_count
            )
            self.invocation_times.append(time.time())

            # Simulate work
            await asyncio.sleep(0.2)

            # Reduce active count
            self.active_count -= 1

            return ModelResponse(
                completion="Test async response",
                prompt_tokens=10,
                completion_tokens=20,
                latency_ms=200,
            )

    # Create a mock tracer
    tracer = MagicMock()
    tracer.db_client.fetch_data.return_value = [
        {"asset_binary": "system: test\nuser: test", "file_path": "test.jsonl"}
    ]  # Create a mock dataset with multiple records
    dataset = [{"id": i, "text": f"test {i}"} for i in range(10)]

    # Mock the Utils.load_dataset method
    with patch("promptlab._utils.Utils") as mockUtils:
        mockUtils.load_dataset.return_value = dataset
        mockUtils.split_prompt_template.return_value = (
            "system: test",
            "user: test",
            [],
        )
        mockUtils.prepare_prompts = lambda item, sys, usr, vars: (
            sys,
            usr,
        )  # Create a model with limited concurrency
        model_config = ModelConfig(
            model_deployment="mock-model",
            max_concurrent_tasks=3,  # Limit to 3 concurrent tasks
        )
        model = TrackedModel(model_config)

        # Create an experiment instance
        experiment = Experiment(tracer)

        # Create a mock experiment config
        experiment_config = MagicMock()
        # Set up the nested attributes
        prompt_template = MagicMock()
        prompt_template.name = "test"
        prompt_template.version = 1
        dataset = MagicMock()
        dataset.name = "test"
        dataset.version = 1

        # Attach the mocks to the experiment_config
        experiment_config.prompt_template = prompt_template
        experiment_config.dataset = dataset
        experiment_config.completion_model = model
        experiment_config.evaluation = []  # Run the experiment asynchronously
        await experiment._init_batch_eval_async(
            dataset, "system: test", "user: test", [], experiment_config
        )

        # Check that the concurrency limit was respected
        assert model.max_observed_concurrency <= 3, (
            "Concurrency limit was not respected"
        )
