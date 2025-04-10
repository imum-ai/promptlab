import asyncio
from http.server import HTTPServer
from typing import Optional
import threading
import uvicorn

from promptlab.config import TracerConfig
from promptlab.studio.async_api import AsyncStudioApi
from promptlab.studio.web import StudioWebHandler

class AsyncStudio:

    def __init__(self, tracer_config: TracerConfig):
        self.tracer_config = tracer_config
        self.web_server: Optional[HTTPServer] = None
        self.api_server: Optional[AsyncStudioApi] = None
        self.web_thread: Optional[threading.Thread] = None
        self.api_task = None
        
    def start_web_server(self, web_port: int):
        """Start the web server in a separate thread"""
        self.web_server = HTTPServer(
            ("localhost", web_port),
            StudioWebHandler
        )

        self.web_thread = threading.Thread(
            target=self.web_server.serve_forever,
            daemon=True
        )

        self.web_thread.start()
    
    async def start_api_server(self, api_port: int):
        """Start the API server asynchronously"""
        self.api_server = AsyncStudioApi(self.tracer_config)
        await self.api_server.run("localhost", api_port)
    
    def shutdown(self):
        """Shutdown all servers"""
        if self.web_server:
            self.web_server.shutdown()
            
        if self.web_thread and self.web_thread.is_alive():
            self.web_thread.join(timeout=5)
            
        if self.api_task:
            self.api_task.cancel()

    async def start_async(self, port: int = 8000):
        """Start the studio asynchronously"""
        try:
            # Start web server in a separate thread
            self.start_web_server(port)
            
            # Start API server asynchronously
            self.api_task = asyncio.create_task(self.start_api_server(port + 1))
            
            print(f"Studio started at http://localhost:{port}")
            
            # Keep the task running
            await self.api_task
                
        except asyncio.CancelledError:
            print("\nShutting down servers...")
            self.shutdown()
        except Exception as e:
            self.shutdown()
            raise e

    def start(self, port: int = 8000):
        """
        Synchronous wrapper for starting the studio
        This maintains backward compatibility
        """
        try:
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async start method
            try:
                loop.run_until_complete(self.start_async(port))
            except KeyboardInterrupt:
                print("\nShutting down servers...")
                self.shutdown()
            finally:
                loop.close()
                
        except Exception as e:
            self.shutdown()
            raise e
