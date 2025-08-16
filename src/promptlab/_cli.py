import asyncio
import click
from promptlab.core import PromptLab


@click.group()
def promptlab():
    """PromptLab CLI tool for experiment tracking and visualization"""
    pass


@promptlab.group()
def studio():
    """Studio related commands"""
    pass


@studio.command()
@click.option("-d", "--db", required=True, help="Path to the SQLite file")
@click.option(
    "-p", "--port", default=8000, show_default=True, help="Port to run the Studio on"
)
def start(db, port):
    """Start the studio server"""

    click.echo(f"Starting studio with database: {db}")

    tracer_config = {"type": "local", "db_file": db}
    pl = PromptLab(tracer_config)
    asyncio.run(pl.studio.start_async(port))

    click.echo(f"Running on port: {port}")


@promptlab.group()
def db():
    """Database management commands"""
    pass


@db.command()
@click.option("-d", "--db", required=True, help="Path to the SQLite file")
def init(db):
    """Initialize the database"""
    from promptlab.sqlite.database_manager import db_manager

    click.echo(f"Initializing database: {db}")
    db_manager.initialize_database(db)
    click.echo("Database initialized successfully!")


@db.command()
@click.option("-d", "--db", required=True, help="Path to the SQLite file")
def migrate(db):
    """Run database migrations"""
    from promptlab.sqlite.database_manager import db_manager

    click.echo(f"Running migrations for database: {db}")
    db_manager.initialize_database(db)  # This includes running migrations
    click.echo("Migrations completed successfully!")


@db.command()
@click.option("-d", "--db", required=True, help="Path to the SQLite file")
@click.option("-m", "--message", required=True, help="Migration message")
def revision(db, message):
    """Create a new migration revision"""
    try:
        from alembic.config import Config
        from alembic import command
        from pathlib import Path

        # Get the alembic.ini from within the package
        package_root = Path(__file__).parent
        alembic_cfg_path = package_root / "alembic.ini"

        if not alembic_cfg_path.exists():
            click.echo("Error: Alembic configuration not found", err=True)
            return

        # Configure Alembic
        alembic_cfg = Config(str(alembic_cfg_path))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db}")

        click.echo(f"Creating migration revision: {message}")
        command.revision(alembic_cfg, message=message, autogenerate=True)
        click.echo("Migration revision created successfully!")

    except ImportError:
        click.echo("Error: Alembic not installed", err=True)
    except Exception as e:
        click.echo(f"Error creating migration: {e}", err=True)


if __name__ == "__main__":
    promptlab()
