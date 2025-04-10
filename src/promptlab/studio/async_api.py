import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from promptlab.db.sql import SQLQuery
from promptlab.types import TracerConfig
from promptlab.utils import Utils
from promptlab.enums import AssetType

class AsyncStudioApi:
 
    def __init__(self, tracer_config: TracerConfig):
        self.tracer_config = tracer_config
        self.app = FastAPI(title="PromptLab Studio API")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()
        
    def _setup_routes(self):
        
        @self.app.get("/experiments")
        async def get_experiments():
            try:               
                experiments = self.tracer_config.db_client.fetch_data(SQLQuery.SELECT_EXPERIMENTS_QUERY)
                
                # Process experiments and remove asset_binary
                processed_experiments = []
                for experiment in experiments:
                    system_prompt, user_prompt, _ = Utils.split_prompt_template(experiment["asset_binary"])
                    # Create new dict without asset_binary
                    experiment_data = {k: v for k, v in experiment.items() if k != 'asset_binary'}
                    experiment_data["system_prompt_template"] = system_prompt
                    experiment_data["user_prompt_template"] = user_prompt
                    processed_experiments.append(experiment_data)

                return {"experiments": processed_experiments}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
            
        @self.app.get("/prompttemplates")
        async def get_prompt_templates():
            try:               
                prompt_templates = self.tracer_config.db_client.fetch_data(SQLQuery.SELECT_ASSET_BY_TYPE_QUERY, (AssetType.PROMPT_TEMPLATE.value,))
                
                processed_templates = []
                for template in prompt_templates:
                    system_prompt, user_prompt, _ = Utils.split_prompt_template(template["asset_binary"])

                    experiment_data = {k: v for k, v in template.items() if k != 'asset_binary'}
                    experiment_data["system_prompt_template"] = system_prompt
                    experiment_data["user_prompt_template"] = user_prompt
                    processed_templates.append(experiment_data)

                return {"prompt_templates": processed_templates}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
            
        @self.app.get("/datasets")
        async def get_datasets():
            try:               
                datasets = self.tracer_config.db_client.fetch_data(SQLQuery.SELECT_ASSET_BY_TYPE_QUERY, (AssetType.DATASET.value,))

                processed_datasets = []
                for dataset in datasets:
                    file_path = json.loads(dataset["asset_binary"])['file_path']

                    data = {k: v for k, v in dataset.items() if k != 'asset_binary'}
                    data["file_path"] = file_path
                    processed_datasets.append(data)

                return {"datasets": processed_datasets}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
    async def run(self, host: str = "127.0.0.1", port: int = 5000):
        import uvicorn
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()
