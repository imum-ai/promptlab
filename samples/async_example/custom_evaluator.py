from promptlab.evaluator.evaluator import Evaluator

class LengthEvaluator(Evaluator):
    """
    A simple evaluator that measures the length of the response
    """
    def evaluate(self, data: dict) -> str:
        """
        Evaluate the length of the response
        """
        response = data.get("response", "")
        return str(len(response))
        
class AsyncExample:
    """
    Example showing how to use async functionality in PromptLab
    """
    @staticmethod
    async def run_async_experiment():
        """
        Run an experiment asynchronously
        """
        import asyncio
        from promptlab import PromptLab
        from promptlab.types import PromptTemplate, Dataset
        
        # Initialize PromptLab
        tracer_config = {
            "type": "sqlite",
            "db_file": "./promptlab.db"
        }
        pl = PromptLab(tracer_config)
        
        # Create evaluator
        length_eval = LengthEvaluator()
        
        # Create prompt template and dataset
        # (Code omitted for brevity)
        
        # Run experiment asynchronously
        experiment_config = {
            # Configuration details
        }
        
        await pl.run_experiment_async(experiment_config)
        
        # Start studio asynchronously
        await pl.start_studio_async(8000)
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(AsyncExample.run_async_experiment())
