# Database Management in PromptLab

This document explains the centralized database management system implemented in PromptLab to solve the multiple initialization issue.

## Problem Solved

Previously, PromptLab had multiple `init_engine` functions that could initialize the database concurrently, leading to:
- Race conditions during startup
- Redundant database initialization
- Potential inconsistent database state
- Performance issues

## Solution Overview

### Centralized Database Manager

The new system implements a singleton `DatabaseManager` class that ensures:
- **Single Point of Initialization**: Only one place handles database setup
- **Thread Safety**: Uses locking mechanisms to prevent race conditions
- **One-Time Operation**: Database is initialized only once, regardless of how many times it's requested
- **Migration Support**: Integrated Alembic support for schema migrations

### Key Components

1. **DatabaseManager** (`src/promptlab/sqlite/database_manager.py`)
   - Singleton pattern ensures single instance
   - Thread-safe initialization with double-checked locking
   - Automatic Alembic migration support
   - Logging for debugging and monitoring

2. **Enhanced Session Management** (`src/promptlab/sqlite/session.py`)
   - Thread-safe session initialization
   - Utility functions for checking initialization state
   - Reset functionality for testing

3. **CLI Commands** (`src/promptlab/_cli.py`)
   - `promptlab db init`: Initialize database
   - `promptlab db migrate`: Run migrations
   - `promptlab db revision`: Create new migration

## Usage

### Starting the Studio

The studio startup remains the same:
```bash
promptlab studio start -d /path/to/database.db -p 8000
```

The database will be automatically initialized on first startup.

### Manual Database Operations

Initialize a database:
```bash
promptlab db init -d /path/to/database.db
```

Run migrations:
```bash
promptlab db migrate -d /path/to/database.db
```

Create a new migration:
```bash
promptlab db revision -d /path/to/database.db -m "Add new table"
```

### Programmatic Usage

```python
from promptlab.sqlite.database_manager import db_manager
from promptlab.tracer.local_tracer import LocalTracer

# The database will be automatically initialized
tracer = LocalTracer({"type": "local", "db_file": "/path/to/db.sqlite"})

# Or initialize manually
db_manager.initialize_database("/path/to/db.sqlite")
```

## Migration System

### Alembic Integration

The system now includes full Alembic support for database schema migrations:

- **Automatic Migration Detection**: On startup, the system checks for pending migrations
- **Safe Migration Execution**: Migrations are applied automatically and safely
- **Version Tracking**: Database schema version is tracked in the `alembic_version` table

### Creating Migrations

1. Make changes to your SQLAlchemy models in `src/promptlab/sqlite/models.py`
2. Generate a migration:
   ```bash
   promptlab db revision -d /path/to/database.db -m "Description of changes"
   ```
3. Review the generated migration file in `migrations/versions/`
4. Apply migrations:
   ```bash
   promptlab db migrate -d /path/to/database.db
   ```

## File Structure

```
promptlab/
├── alembic.ini                          # Alembic configuration
├── migrations/                          # Migration files
│   ├── env.py                          # Alembic environment
│   ├── script.py.mako                  # Migration template
│   └── versions/                       # Version files
├── src/promptlab/sqlite/
│   ├── database_manager.py             # Centralized database manager
│   ├── session.py                      # Enhanced session management
│   └── models.py                       # SQLAlchemy models
└── tests/unit/
    └── test_database_initialization.py  # Tests for new system
```

## Thread Safety

The new system implements several thread safety mechanisms:

1. **Double-Checked Locking**: Prevents race conditions during initialization
2. **Global State Protection**: Uses threading locks to protect shared state
3. **Singleton Pattern**: Ensures only one DatabaseManager instance exists

## Testing

Run the database initialization tests:
```bash
python -m pytest tests/unit/test_database_initialization.py
```

The tests verify:
- Single initialization across multiple calls
- Thread safety with concurrent access
- Proper LocalTracer integration
- Database file creation

## Benefits

1. **Reliability**: Eliminates race conditions and initialization conflicts
2. **Performance**: Avoids redundant database operations
3. **Maintainability**: Centralized database logic is easier to maintain
4. **Scalability**: Proper migration system supports schema evolution
5. **Debugging**: Comprehensive logging helps troubleshoot issues

## Backwards Compatibility

The changes are backwards compatible:
- Existing `LocalTracer` usage remains unchanged
- CLI commands work as before
- No breaking changes to public APIs

## Future Enhancements

- Database connection pooling for improved performance
- Support for multiple database backends
- Enhanced migration rollback capabilities
- Database health monitoring and metrics
