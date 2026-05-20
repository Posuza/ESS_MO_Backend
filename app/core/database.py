"""Database initialization logic."""

import logging
from sqlalchemy.exc import OperationalError, DatabaseError, InterfaceError, DBAPIError
from app.core.orm import Base, engine, _is_db_port_open
from app.core.registries.error_registry import ERROR_REGISTRY
import app.models.mo_daily_transactions
import app.models.employees
import app.models.fields
import app.models.departments
import app.models.divisions
import app.models.routes
import app.models.positions
import app.models.position_change_logs
import app.models.name_prefixs
import app.models.addresses
import app.models.provinces
import app.models.districts
import app.models.sub_districts
import app.models.postal_codes
import app.models.audit_logs

logger = logging.getLogger(__name__)

def init_db():
    """Auto-create tables based on SQLAlchemy Base metadata."""
    try:
        if not _is_db_port_open():
            entry = ERROR_REGISTRY["DB"]["ER_DB_501"]
            logger.warning(f"[{entry['error']}] {entry['message']} (Port check failed)")
            return
            
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except (OperationalError, InterfaceError, DBAPIError) as e:
        entry = ERROR_REGISTRY["DB"]["ER_DB_501"]
        logger.warning(f"[{entry['error']}] {entry['message']}")
        logger.warning(f"Details: {str(e)}")
    except Exception as e:
        entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]
        logger.error(f"[{entry['error']}] {entry['message']}")
        logger.error(f" Details: {str(e)}")
