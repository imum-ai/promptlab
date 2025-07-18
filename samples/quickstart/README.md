# Quickstart

This sample ([quickstart.py](quickstart.py)) demonstrates how to use PromptLab to evaluate a simple prompt. 

## Installation and Setup

It's highly recommended to use a virtual environment (try venv or conda or uv).

```bash
pip install promptlab
```

## Initialize PromptLab 

The first step to use PromptLab is to initialize the PromptLab object. PromptLab needs a tracer object, please check [Tracer](../../docs/README.md#tracer) to learn more about the tracer configuration.

Initializing PromptLab with local tracer.

```python
tracer_config = {
    "type": "local", 
    "db_file": "./promptlab.db"
}
```

If you are using PromptLab locally, you can start the PromptLab Studio to check the assets and experiments.

```python
asyncio.run(pl.studio.start_async(8000))
```

## Create a Prompt Template

A prompt template is a prompt with or without placeholders. Please check [Prompt Template](../../docs/README.md#prompt-template) to learn more about it.

A prompt template has two main attributes - `system_prompt` and `user_prompt`. The sample prompt used in this example is:

```python
prompt_name = "essay_feedback"
prompt_description = "A prompt for generating feedback on essays"
system_prompt = "You are a helpful assistant who can provide feedback on essays."
user_prompt = """The essay topic is - <essay_topic>.
               The submitted essay is - <essay>
               Now write feedback on this essay."""
prompt_template = PromptTemplate(name=prompt_name, description=prompt_description, system_prompt=system_prompt, user_prompt=user_prompt)
pt = pl.asset.create(prompt_template)
```

Here, `<essay_topic>` and `<essay>` are placeholders that will be replaced with real data before sending to the LLM. PromptLab will search the dataset for columns with these exact names and use their values to replace the corresponding placeholders. Ensure that the dataset contains columns named `essay_topic` and `essay`.

![PromptLab Studio](../../img/studio-pt.png)

## Create Dataset

A dataset is a JSONL file used to design the experiment. Please check [Dataset](../../docs/README.md#dataset) to learn more about it.

```python
dataset_name = "essay_samples"
dataset_description = "dataset for evaluating the essay_feedback prompt"
dataset_file_path = "./samples/data/essay_feedback.jsonl"
dataset = Dataset(name=dataset_name, description=dataset_description, file_path=dataset_file_path)
ds = pl.asset.create(dataset)
```

![PromptLab Studio](../../img/studio-ds.png)

## Create Experiment

An experiment evaluates the outcome of a prompt against a set of metrics for a given dataset. Developers can modify hyperparameters (such as prompt template and models) and compare experiment results to determine the best prompt to deploy in production. Please check [Experiment](../../docs/README.md#experiment) to learn more about it.

In the [quickstart.py](quickstart.py), we are using the prompt template and dataset created in the previous steps to design an experiment. It also uses two evaluation metrics: `semantic_similarity` and `fluency`. Please check [Metric](../../docs/README.md#metric) to learn more about evaluation metrics.

```python
experiment_config = {
    "name": "demo_experimet",
    "completion_model_config": {
        "name": "ollama/llama3.2", 
        "type": "completion"
    },
    "embedding_model_config": {
        "name": "ollama/nomic-embed-text:latest",
        "type": "embedding",
    },
    "prompt_template": pt,
    "dataset": ds,
    "evaluation": [
        {
            "metric": "semantic_similarity",
            "column_mapping": {"response": "$completion", "reference": "feedback"},
        },
        {
            "metric": "relevance",
            "column_mapping": {
                "response": "$completion",
                "query": "essay_topic",
            },
        },
    ],
}
```

![PromptLab Studio](../../img/studio-exp.png)

Details of the experiment:

![PromptLab Studio](../../img/studio-exp-details.png)