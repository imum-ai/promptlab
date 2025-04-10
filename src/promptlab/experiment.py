from datetime import datetime
from typing import List, Dict, Tuple, Any
import json
import re
import uuid
import asyncio

from promptlab.config import ConfigValidator, ExperimentConfig
from promptlab.db.sql import SQLQuery
from promptlab.model.model_factory import ModelFactory
from promptlab.evaluator.evaluator_factory import EvaluatorFactory
from promptlab.tracer.tracer import Tracer
from promptlab.utils import Utils

class Experiment:
    def __init__(self, tracer: Tracer):
        self.tracer = tracer

    def run(self, experiment_config: ExperimentConfig):
        """
        Synchronous version of experiment execution
        """
        experiment_config = ExperimentConfig(**experiment_config)
        ConfigValidator.validate_experiment_config(experiment_config)

        prompt_template = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_QUERY, (experiment_config.prompt_template.name, experiment_config.prompt_template.version))[0]
        system_prompt, user_prompt, prompt_template_variables = Utils.split_prompt_template(prompt_template['asset_binary'])

        eval_dataset_path = self.tracer.db_client.fetch_data(SQLQuery.SELECT_DATASET_FILE_PATH_QUERY, (experiment_config.dataset.name, experiment_config.dataset.version))[0]
        eval_dataset = Utils.load_dataset(eval_dataset_path['file_path'])

        exp_summary = self.init_batch_eval(eval_dataset, system_prompt, user_prompt, prompt_template_variables, experiment_config)

        self.tracer.trace(experiment_config, exp_summary)

    async def run_async(self, experiment_config: ExperimentConfig):
        """
        Asynchronous version of experiment execution
        """
        experiment_config = ExperimentConfig(**experiment_config)
        ConfigValidator.validate_experiment_config(experiment_config)

        prompt_template = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_QUERY, (experiment_config.prompt_template.name, experiment_config.prompt_template.version))[0]
        system_prompt, user_prompt, prompt_template_variables = Utils.split_prompt_template(prompt_template['asset_binary'])

        eval_dataset_path = self.tracer.db_client.fetch_data(SQLQuery.SELECT_DATASET_FILE_PATH_QUERY, (experiment_config.dataset.name, experiment_config.dataset.version))[0]
        eval_dataset = Utils.load_dataset(eval_dataset_path['file_path'])

        exp_summary = await self.init_batch_eval_async(eval_dataset, system_prompt, user_prompt, prompt_template_variables, experiment_config)

        self.tracer.trace(experiment_config, exp_summary)

    def init_batch_eval(self, eval_dataset, system_prompt, user_prompt, prompt_template_variables, experiment_config: ExperimentConfig) -> List:

        inference_model = ModelFactory.get_model(experiment_config.model)
        experiment_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        exp_summary = []

        for eval_record in eval_dataset:
            system_prompt, user_prompt = self.prepare_prompts(eval_record, system_prompt, user_prompt, prompt_template_variables)

            inference_result = inference_model.invoke(system_prompt, user_prompt)
            evaluation = self.evaluate(inference_result.inference, eval_record, experiment_config)

            eval = dict()
            eval["experiment_id"] = experiment_id
            eval["dataset_record_id"] = eval_record['id']
            eval["inference"] = inference_result.inference
            eval["prompt_tokens"] = inference_result.prompt_tokens
            eval["completion_tokens"] = inference_result.completion_tokens
            eval["latency_ms"] = inference_result.latency_ms
            eval["evaluation"] = evaluation
            eval["created_at"] = timestamp

            exp_summary.append(eval)

        return exp_summary

    def evaluate(self, inference: str, row, experiment_config: ExperimentConfig) -> str:

        evaluations = []
        for eval in experiment_config.evaluation:
            evaluator = EvaluatorFactory.get_evaluator(eval.type, eval.metric, experiment_config.model, eval.evaluator)
            data = dict()
            for key, value in eval.column_mapping.items():
                if value == "$inference":
                    data[key] = inference
                else:
                    data[key] = row[value]
            evaluation_result = evaluator.evaluate(data)
            evaluations.append({
                "metric": f'{eval.type}-{eval.metric}',
                "result": evaluation_result
            })
        return json.dumps(evaluations)

    async def init_batch_eval_async(self, eval_dataset, system_prompt, user_prompt, prompt_template_variables, experiment_config: ExperimentConfig) -> List:
        """
        Asynchronous version of batch evaluation
        """
        inference_model = ModelFactory.get_model(experiment_config.model)
        experiment_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        exp_summary = []
        tasks = []

        # Prepare all prompts first
        prepared_prompts = []
        for eval_record in eval_dataset:
            sys_prompt, usr_prompt = self.prepare_prompts(eval_record, system_prompt, user_prompt, prompt_template_variables)
            prepared_prompts.append((eval_record, sys_prompt, usr_prompt))

        # Create tasks for async execution
        for eval_record, sys_prompt, usr_prompt in prepared_prompts:
            task = asyncio.create_task(self._process_record_async(inference_model, sys_prompt, usr_prompt, eval_record, experiment_id, timestamp, experiment_config))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        exp_summary.extend(results)

        return exp_summary

    async def _process_record_async(self, inference_model, system_prompt, user_prompt, eval_record, experiment_id, timestamp, experiment_config):
        """
        Process a single record asynchronously
        """
        inference_result = await inference_model.ainvoke(system_prompt, user_prompt)
        evaluation = self.evaluate(inference_result.inference, eval_record, experiment_config)

        eval_result = dict()
        eval_result["experiment_id"] = experiment_id
        eval_result["dataset_record_id"] = eval_record['id']
        eval_result["inference"] = inference_result.inference
        eval_result["prompt_tokens"] = inference_result.prompt_tokens
        eval_result["completion_tokens"] = inference_result.completion_tokens
        eval_result["latency_ms"] = inference_result.latency_ms
        eval_result["evaluation"] = evaluation
        eval_result["created_at"] = timestamp

        return eval_result

    def prepare_prompts(self, item, system_prompt, user_prompt, prompt_template_variables):

        for variable in prompt_template_variables:
            placeholder = f'<{variable}>'
            replacement = f'<{item[variable]}>'

            system_prompt = system_prompt.replace(placeholder, replacement)
            user_prompt = user_prompt.replace(placeholder, replacement)

        return system_prompt, user_prompt