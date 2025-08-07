"""Database manager for centralized database operations and migrations."""

import logging
from pathlib import Path
from typing import Optional

from .session import init_engine, is_initialized


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database manager for PromptLab Studio.

    This class ensures that database initialization and migrations
    are handled in a centralized, thread-safe manner.
    """

    _instance: Optional["DatabaseManager"] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._db_url: Optional[str] = None
            self._initialized = True

    def initialize_database(self, db_file: str) -> None:
        """Initialize the database with the given file path.

        Args:
            db_file (str): Path to the SQLite database file
        """
        if is_initialized():
            logger.info("Database already initialized, skipping initialization")
            return

        # Ensure the directory exists
        db_path = Path(db_file)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db_url = f"sqlite:///{db_file}"

        logger.info(f"Initializing database at: {db_file}")

        try:
            # Initialize the engine and create tables
            init_engine(self._db_url)

            # Run migrations if Alembic is available
            self._run_migrations()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _run_migrations(self) -> None:
        """Run database migrations using Alembic.

        This checks for pending migrations and applies them automatically.
        """
        try:
            from alembic.config import Config
            from alembic import command
            from alembic.script import ScriptDirectory
            from alembic.runtime.environment import EnvironmentContext
            from sqlalchemy import create_engine

            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            alembic_cfg_path = project_root / "alembic.ini"

            if not alembic_cfg_path.exists():
                logger.warning("Alembic configuration not found, skipping migrations")
                return

            # Configure Alembic
            alembic_cfg = Config(str(alembic_cfg_path))
            alembic_cfg.set_main_option("sqlalchemy.url", self._db_url)

            # Check if we need to run migrations
            script = ScriptDirectory.from_config(alembic_cfg)

            # Create a connection to check current revision
            engine = create_engine(self._db_url)

            with engine.connect():
                context = EnvironmentContext(alembic_cfg, script)

                def get_current_revision():
                    return context.get_current_revision()

                try:
                    with context.begin_transaction():
                        current_rev = context.get_current_revision()
                        head_rev = script.get_current_head()

                        if current_rev != head_rev:
                            logger.info(
                                f"Running migrations from {current_rev} to {head_rev}"
                            )
                            command.upgrade(alembic_cfg, "head")
                        else:
                            logger.info("Database is up to date, no migrations needed")

                except Exception:
                    logger.info(
                        "No migration table found, creating initial migration state"
                    )
                    # Stamp the database with the current head revision
                    command.stamp(alembic_cfg, "head")

        except ImportError:
            logger.warning("Alembic not installed, skipping migrations")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            # Don't fail initialization if migrations fail

    @property
    def is_ready(self) -> bool:
        """Check if the database is ready for use.

        Returns:
            bool: True if database is initialized and ready
        """
        return is_initialized()

    @property
    def database_url(self) -> Optional[str]:
        """Get the current database URL.

        Returns:
            str: Database URL if initialized, None otherwise
        """
        return self._db_url


# Global database manager instance
db_manager = DatabaseManager()
