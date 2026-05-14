"""Database initialization logic."""

from app.core.orm import Base, engine
import app.models.sector_report  # Ensure models are imported for metadata creation
import app.models.employee
import app.models.field
import app.models.department
import app.models.division
import app.models.sector
import app.models.zone
import app.models.route
import app.models.position
import app.models.position_change_log
import app.models.name_prefix  # Added NamePrefix model
import app.models.address      # Added Address model
import app.models.province     # Added Province model
import app.models.district     # Added District model
import app.models.sub_district # Added SubDistrict model
import app.models.postal_code # Added PostalCode model

def init_db():
    """Auto-create tables based on SQLAlchemy Base metadata."""
    Base.metadata.create_all(bind=engine)
