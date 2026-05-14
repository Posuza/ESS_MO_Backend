"""Database initialization logic."""

import logging
from sqlalchemy.exc import OperationalError, DatabaseError, InterfaceError, DBAPIError
from app.core.orm import Base, engine, _is_db_port_open
from app.core.registries.error_registry import ERROR_REGISTRY
import app.models.sector_report
import app.models.employee
import app.models.field
import app.models.department
import app.models.division
import app.models.sector
import app.models.zone
import app.models.route
import app.models.position
import app.models.position_change_log
import app.models.name_prefix
import app.models.address
import app.models.province
import app.models.district
import app.models.sub_district
import app.models.postal_code

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
