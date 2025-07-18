# Custom Metric

This sample ([custom_metric.py](custom_metric.py)) demonstrates how to create custom evaluation metric. This also opens up the opprtunity to use external evaluation libraries like Ragas or Azure Evaluation SDK to use with PromptLab.

## Creating custom metric 

The following code snippet implements a metric using the evaluation library Ragas

    class RagasFactualCorrectness(Evaluator):
        def evaluate(self, data: dict):
            completion = data["response"]
            reference = data["reference"]

            sample = SingleTurnSample(response=completion, reference=reference)

            evaluator_llm = LangchainLLMWrapper(
                ChatOllama(model=self.completion.model_config.model_deployment)
            )

            scorer = FactualCorrectness(llm=evaluator_llm)
            return scorer.single_turn_score(sample)

## Using custom metric

The following code snippet demonstrate how to use the custom metric in the experiment.

    length = LengthEvaluator()
    factual_correctness = RagasFactualCorrectness()

    experiment_config = {
        "completion_model": completion_model,
        "embedding_model": embedding_model,
        "prompt_template": pt,
        "dataset": ds,
        "evaluation": [
            {
                "metric": "length",
                "column_mapping": {
                    "response": "$completion",
                },
                "evaluator": length,
            },
            {
                "metric": "factual_correctness",
                "column_mapping": {"response": "$completion", "reference": "feedback"},
                "evaluator": factual_correctness,
            },
        ],
    }
    pl.experiment.run(experiment_config)