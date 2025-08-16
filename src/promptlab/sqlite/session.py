import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

_engine = None
_SessionLocal = None
_db_initialized = False
_init_lock = threading.Lock()


def _create_default_admin_user():
    """Create default admin user if it doesn't exist."""
    from .models import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    session = _SessionLocal()
    try:
        if not session.query(User).filter_by(username="admin").first():
            admin_user = User(
                username="admin", password_hash=pwd_context.hash("admin"), role="admin"
            )
            session.add(admin_user)
            session.commit()
    finally:
        session.close()


def init_engine(db_url):
    """Initialize the database engine and session maker.

    This function ensures that database initialization only happens once,
    even if called multiple times from different parts of the application.

    Args:
        db_url (str): Database URL for SQLite connection
    """
    global _engine, _SessionLocal, _db_initialized

    # Use double-checked locking pattern for thread safety
    if _db_initialized:
        return

    with _init_lock:
        # Check again inside the lock to prevent race conditions
        if _db_initialized:
            return

        _engine = create_engine(db_url, connect_args={"check_same_thread": False})
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

        # Create all tables
        Base.metadata.create_all(bind=_engine)

        # Insert default admin user if not exists
        _create_default_admin_user()

        _db_initialized = True


def get_session():
    """Get a database session.

    Returns:
        Session: SQLAlchemy session object

    Raises:
        RuntimeError: If the database engine has not been initialized
    """
    if _SessionLocal is None:
        raise RuntimeError("Session not initialized. Call init_engine first.")
    return _SessionLocal()


def is_initialized():
    """Check if the database has been initialized.

    Returns:
        bool: True if database is initialized, False otherwise
    """
    return _db_initialized


def reset_initialization():
    """Reset the initialization state. Used primarily for testing.

    Warning: This should only be used in test environments.
    """
    global _engine, _SessionLocal, _db_initialized
    with _init_lock:
        _engine = None
        _SessionLocal = None
        _db_initialized = False
