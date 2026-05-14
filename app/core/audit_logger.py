

from __future__ import annotations

import logging
from typing import Optional

from fastapi import Request

from app.core.registries import ACTION_REGISTRY, ERROR_REGISTRY
from app.schemas.audit_log import AuditLogCreate
from app.services.audit_log import AuditLogService

_logger = logging.getLogger(__name__)
_service = AuditLogService()


# ─── Request context helpers ──────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_geo_info(request: Request) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Return (latitude, longitude, geo_status) from request headers.
    Frontend sends X-Latitude / X-Longitude on success, or X-Geo-Status on denial.
    """
    lat = request.headers.get("X-Latitude")
    lng = request.headers.get("X-Longitude")
    status = request.headers.get("X-Geo-Status") or None
    if lat and lng:
        return lat, lng, "available"
    return None, None, status


_UA_DEVICE_MAP = [
    ("iPad", "iPad"),
    ("iPhone", "iPhone"),
    ("Android", "Android"),
]
_UA_OS_MAP = [
    ("Windows NT", "Windows"),
    ("Macintosh", "macOS"),
    ("iPhone", "iOS"),
    ("iPad", "iOS"),
    ("Android", "Android"),
    ("Linux", "Linux"),
]


def get_device_info(request: Request) -> tuple[str, str]:
    """Return (device_name, os_name) by parsing the User-Agent header."""
    ua = request.headers.get("User-Agent", "")
    device = next((d for kw, d in _UA_DEVICE_MAP if kw in ua), "Desktop")
    os_name = next((o for kw, o in _UA_OS_MAP if kw in ua), "Unknown")
    return device, os_name


def _extract_request_context(request: Request) -> dict:
    """
    Build a combined ip_address string: {ip}/{geo}/{device}
    Examples:
      171.6.207.133/Latitude : 13.726 Longitude : 100.595/iPhone
      49.230.145.155/User denied the request for Geolocation./Windows
      1.2.3.4/unavailable/Desktop
    """
    ip = get_client_ip(request)
    lat, lng, geo_status = get_geo_info(request)
    device, _os = get_device_info(request)

    if lat and lng:
        geo_part = f"Latitude : {lat} Longitude : {lng}"
    elif geo_status:
        geo_part = geo_status
    else:
        geo_part = "unavailable"

    return {"ip_address": f"{ip}/{geo_part}/{device}"}


# ─── Audit wrapper ────────────────────────────────────────────────────────────

class _AuditWrapper:
    """
    Thin façade over AuditLogService.
    All writes are fire-and-forget (errors are logged, never raised).
    """

    # ── raw write ────────────────────────────────────────────────────────────

    def log(
        self,
        *,
        action: str,
        user_name: str,
        ip_address: str,
        employee_code: Optional[str] = None,
    ) -> None:
        """Persist one audit entry. Safe to call anywhere — swallows DB errors."""
        try:
            payload = AuditLogCreate(
                employee_code=employee_code,
                user_name=user_name,
                ip_address=ip_address,
                action=action,
            )
            _service.create(payload)
        except Exception as exc:  # pragma: no cover
            _logger.error("audit.log failed: %s", exc, exc_info=True)

    # ── action helper ────────────────────────────────────────────────────────

    def action(
        self,
        category: str,
        key: str,
        *,
        request: Request,
        user_name: str,
        employee_code: Optional[str] = None,
        **fmt_kwargs,
    ) -> None:
        """
        Look up an action in ACTION_REGISTRY and write it to audit_logs.

        Extra keyword arguments are interpolated into the message template,
        e.g. audit.action("DATA", "ACT_DAT_001", resource="employee", ...).
        
        Format: [ACT_KEY]ACTION_NAME | message
        """
        try:
            entry = ACTION_REGISTRY[category][key]
            message_template: str = entry["message"]
            action_name: str = entry["action"]
            message = message_template.format(**fmt_kwargs) if fmt_kwargs else message_template
            full_action = f"[{key}]{action_name} | {message}"
        except KeyError:
            full_action = f"[UNKNOWN] {category}.{key}"

        self.log(
            action=full_action,
            user_name=user_name,
            employee_code=employee_code,
            **_extract_request_context(request),
        )

    # ── action with error details ────────────────────────────────────────────

    def action_with_error(
        self,
        category: str,
        key: str,
        *,
        request: Request,
        user_name: str,
        employee_code: Optional[str] = None,
        error_category: str,
        error_key: str,
        **fmt_kwargs,
    ) -> None:
        """
        Log action with detailed error information.
        Format: [ACT_KEY]ACTION | message | ERROR_KEY | ERROR_TYPE | ERROR_MESSAGE
        """
        try:
            # Get action entry
            action_entry = ACTION_REGISTRY[category][key]
            action_name: str = action_entry["action"]
            message_template: str = action_entry["message"]
            message = message_template.format(**fmt_kwargs) if fmt_kwargs else message_template
            
            # Get error entry
            error_entry = ERROR_REGISTRY[error_category][error_key]
            error_type = error_entry["error"]
            error_message = error_entry["message"]
            
            # Format: [ACT_KEY]ACTION | message | ERROR_KEY | ERROR_TYPE | ERROR_MESSAGE
            full_action = f"[{key}]{action_name} | {message} | {error_key} | {error_type} | {error_message}"
        except KeyError:
            full_action = f"[UNKNOWN] {category}.{key} | Error: {error_category}.{error_key}"

        self.log(
            action=full_action,
            user_name=user_name,
            employee_code=employee_code,
            **_extract_request_context(request),
        )

    # ── error helper ─────────────────────────────────────────────────────────

    def error(
        self,
        category: str,
        key: str,
        *,
        request: Request,
        user_name: str,
        employee_code: Optional[str] = None,
        detail: str = "",
    ) -> None:
        """
        Look up an error in ERROR_REGISTRY and write it as an audit entry.
        Useful for auditing security violations, 404s, rate-limit hits, etc.
        """
        try:
            entry = ERROR_REGISTRY[category][key]
            code = entry["code"]
            http_status = entry["http_status"]
            message = entry["message"]
            contacts_list = entry.get("contacts", [])
            contacts_str = ", ".join(
                f"{c.get('team') or c.get('role')} <{c.get('email')}>"
                for c in contacts_list
            )
            full_action = (
                f"[ERR-{code}] HTTP {http_status} | {message}"
                + (f" | detail={detail}" if detail else "")
                + (f" | contacts={contacts_str}" if contacts_str else "")
            )
        except KeyError:
            full_action = f"[ERR-UNKNOWN] {category}.{key}" + (f" | detail={detail}" if detail else "")

        self.log(
            action=full_action,
            user_name=user_name,
            employee_code=employee_code,
            **_extract_request_context(request),
        )


# ─── Singleton ────────────────────────────────────────────────────────────────
audit = _AuditWrapper()
