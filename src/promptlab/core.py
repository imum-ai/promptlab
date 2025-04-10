from promptlab.asset import Asset
from promptlab.experiment import Experiment
from promptlab.studio.studio import Studio
from promptlab.studio.async_studio import AsyncStudio
from promptlab.tracer.tracer_factory import TracerFactory
from promptlab.config import ConfigValidator, TracerConfig

class PromptLab:

    def __init__(self, tracer_config: dict):

        tracer_config = TracerConfig(**tracer_config)
        ConfigValidator.validate_tracer_config(tracer_config)

        self.tracer = TracerFactory.get_tracer(tracer_config)
        self.tracer.init_db()

        self.asset = Asset(self.tracer)
        self.experiment = Experiment(self.tracer)
        self.studio = Studio(self.tracer)
        self.async_studio = AsyncStudio(self.tracer)

    async def run_experiment_async(self, experiment_config: dict):
        """Run an experiment asynchronously"""
        return await self.experiment.run_async(experiment_config)

    async def start_studio_async(self, port: int = 8000):
        """Start the studio asynchronously"""
        return await self.async_studio.start_async(port)