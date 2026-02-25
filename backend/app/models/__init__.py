"""Database models."""
from app.models.organization import Organization
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.preset_location import PresetLocation
from app.models.preset_destination import PresetDestination
from app.models.fixed_tariff import FixedTariff
from app.models.trip import Trip
from app.models.gps_log import GPSLog
from app.models.invoice import Invoice

__all__ = [
    "Organization",
    "Driver",
    "Vehicle",
    "PresetLocation",
    "PresetDestination",
    "FixedTariff",
    "Trip",
    "GPSLog",
    "Invoice",
]
