# Async Example

This example demonstrates how to use the async functionality in PromptLab.

## Overview

PromptLab now supports asynchronous operations for:

1. Running experiments
2. Invoking models
3. Starting the PromptLab Studio

This allows for more efficient processing, especially when dealing with large datasets or multiple concurrent operations.

## Running the Example

To run this example:

```bash
cd samples/async_example
python async_example.py
```

This will:

1. Create a prompt template and dataset
2. Run an experiment asynchronously
3. Start the PromptLab Studio asynchronously

## Key Features

### Async Model Invocation

Models now support asynchronous invocation through the `ainvoke` method:

```python
# Synchronous invocation
result = model.invoke(system_prompt, user_prompt)

# Asynchronous invocation
result = await model.ainvoke(system_prompt, user_prompt)
```

### Async Experiment Execution

Experiments can be run asynchronously:

```python
# Synchronous execution
pl.experiment.run(experiment_config)

# Asynchronous execution
await pl.run_experiment_async(experiment_config)
```

### Async Studio

The PromptLab Studio can be started asynchronously:

```python
# Synchronous start
pl.studio.start(8000)

# Asynchronous start
await pl.start_studio_async(8000)
```

## Benefits

- **Improved Performance**: Process multiple requests concurrently
- **Better Resource Utilization**: Make efficient use of system resources
- **Responsive Applications**: Keep your application responsive while processing large datasets
- **Scalability**: Handle more concurrent operations
