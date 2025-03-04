from typing import overload, TypeVar
from datetime import datetime
import json
import os
import uuid

from promptrace.enums import AssetType
from promptrace.db.sql import SQLQuery
from promptrace.tracer.tracer import Tracer
from promptrace.types import Dataset, PromptTemplate

T = TypeVar('T', Dataset, PromptTemplate)

class Asset:

    def __init__(self, tracer: Tracer):        
        self.tracer = tracer
    
    @overload
    def create_or_update(self, asset: Dataset) -> Dataset:
        ...
    
    @overload
    def create_or_update(self, asset: PromptTemplate) -> PromptTemplate:
        ...

    @overload
    def deploy(self, asset: PromptTemplate, target_dir: str):
        ...
    
    def create_or_update(self, asset: T) -> T:

        if isinstance(asset, Dataset):
            return self._handle_dataset(asset)
        elif isinstance(asset, PromptTemplate):
            return self._handle_prompt_template(asset)
        else:
            raise TypeError(f"Unsupported asset type: {type(asset)}")
    
    def _handle_dataset(self, dataset: Dataset) -> Dataset:

        timestamp = datetime.now().isoformat()
        if dataset.id is not None:
            pass
        else:        
            dataset.id = str(uuid.uuid4())
            dataset.version = 1

            binary = {
                "file_path": dataset.file_path
            }

        self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (dataset.id, dataset.name, dataset.description, dataset.version, AssetType.DATASET.value, json.dumps(binary), timestamp))

        return dataset
    
    def _handle_prompt_template(self, template: PromptTemplate) -> PromptTemplate:

        timestamp = datetime.now().isoformat()

        if template.id is not None:
            pass
        else:
            template.id = str(uuid.uuid4())
            template.version = 1

            binary = f'''
                <<system>>
                    {template.system_prompt}
                <<user>>
                    {template.user_prompt}
            '''
            
        self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (template.id, template.name, template.description, template.version, AssetType.PROMPT_TEMPLATE.value,  binary, timestamp))
        return template
    
    def deploy(self, asset: T, target_dir: str) -> T:

        if isinstance(asset, PromptTemplate):
            return self._handle_prompt_template_deploy(asset, target_dir)
        else:
            raise TypeError(f"Unsupported asset type: {type(asset)}")
        
    def _handle_prompt_template_deploy(self, template: PromptTemplate, target_dir: str):

        prompt_template = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_QUERY, (template.id,))[0]

        prompt_template_name = prompt_template['asset_name']
        prompt_template_binary = prompt_template['asset_binary']

        prompt_template_path = os.path.join(target_dir, prompt_template_name)
        
        with open(prompt_template_path, 'w', encoding='utf-8') as file:
            file.write(prompt_template_binary)

        self.tracer.db_client.execute_query(SQLQuery.UPDATE_EXPERIMENT_QUERY, (template.id,))
