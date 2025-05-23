from promptlab import PromptLab
from promptlab.model.ollama import Ollama, Ollama_Embedding
from promptlab.types import ModelConfig, PromptTemplate, Dataset
from factual_correctness import RagasFactualCorrectness
from length import LengthEvaluator

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

# model instnace
inference_model = Ollama(model_config=ModelConfig(model_deployment="llama3.2"))
embedding_model = Ollama_Embedding(
    model_config=ModelConfig(model_deployment="nomic-embed-text:latest")
)

length = LengthEvaluator()
factual_correctness = RagasFactualCorrectness()

# Run an experiment
experiment_config = {
    "inference_model": inference_model,
    "embedding_model": embedding_model,
    "prompt_template": pt,
    "dataset": ds,
    "evaluation": [
        {
            "metric": "length",
            "column_mapping": {
                "response": "$inference",
            },
            "evaluator": length,
        },
        {
            "metric": "factual_correctness",
            "column_mapping": {"response": "$inference", "reference": "feedback"},
            "evaluator": factual_correctness,
        },
    ],
}
pl.experiment.run(experiment_config)

# Start the PromptLab Studio to view results
pl.studio.start(8000)
