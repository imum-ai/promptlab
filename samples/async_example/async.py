import asyncio
from promptlab import PromptLab
from promptlab.types import PromptTemplate, Dataset, ModelConfig
from promptlab.model.ollama import Ollama, Ollama_Embedding


async def main():
    # Initialize PromptLab with SQLite storage
    tracer_config = {"type": "sqlite", "db_file": "./promptlab.db"}
    pl = PromptLab(tracer_config)

    # Create a prompt template
    prompt_name = "essay_feedback"
    prompt_description = "A prompt for generating feedback on essays"
    system_prompt = "You are a helpful assistant who can provide feedback on essays."
    user_prompt = """The essay topic is - <essay_topic>.
                The submitted essay is - <essay>
                Now write feedback on this essay."""
    prompt_template = PromptTemplate(
        name=prompt_name,
        description=prompt_description,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    pt = pl.asset.create(prompt_template)

    # Create a dataset
    dataset_name = "essay_samples"
    dataset_description = "dataset for evaluating the essay_feedback prompt"
    dataset_file_path = "./samples/data/essay_feedback.jsonl"
    dataset = Dataset(
        name=dataset_name, description=dataset_description, file_path=dataset_file_path
    )
    ds = pl.asset.create(dataset)

    # Retrieve assets
    pt = pl.asset.get(asset_name=prompt_name, version=0)
    ds = pl.asset.get(asset_name=dataset_name, version=0)

    # Initialize model objects
    inference_model = Ollama(model_config=ModelConfig(model_deployment="llama3.2"))
    embedding_model = Ollama_Embedding(
        model_config=ModelConfig(model_deployment="llama3.2")
    )

    experiment_config = {
        "inference_model": inference_model,
        "embedding_model": embedding_model,
        "prompt_template": pt,
        "dataset": ds,
        "evaluation": [
            {
                "metric": "semantic_similarity",
                "column_mapping": {"response": "$inference", "reference": "feedback"},
            },
            {
                "metric": "fluency",
                "column_mapping": {"response": "$inference"},
            },
        ],
    }
    # Run the experiment asynchronously
    await pl.experiment.run_async(experiment_config)

    # Start the PromptLab Studio asynchronously
    await pl.studio.start_async(8000)


if __name__ == "__main__":
    asyncio.run(main())
