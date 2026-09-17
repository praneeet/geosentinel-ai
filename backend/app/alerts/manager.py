import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.iso_countries import get_country_info
from app.alerts.websocket import ws_dispatcher
from app.models.alert import Alert

logger = logging.getLogger("geosentinel.alerts")

class AlertManager:
    """
    Handles alert deduplication, cooldown windows, persistent logging,
    and WebSocket broadcasting when country risk breaches critical threshold R > 75.
    """

    def __init__(self, cooldown_hours: int = settings.ALERT_COOLDOWN_HOURS):
        self.cooldown_hours = cooldown_hours
        # In-memory fast cache for country last-alert timestamps: {country_iso: datetime}
        self._last_alerted: Dict[str, datetime] = {}

    def is_in_cooldown(self, country_iso: str, now: datetime = None) -> bool:
        current = now or datetime.now(timezone.utc)
        last_time = self._last_alerted.get(country_iso)
        if not last_time:
            return False
        delta = current - last_time
        return delta < timedelta(hours=self.cooldown_hours)

    async def check_and_trigger(
        self,
        country_iso: str,
        risk_score: float,
        tier: str,
        contributing_factors: Dict[str, Any],
        session: AsyncSession,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates risk score. If R > 75 and cooldown expired,
        records the alert to the database and broadcasts over WebSocket.
        """
        now = datetime.now(timezone.utc)
        if risk_score <= settings.ALERT_CRITICAL_THRESHOLD:
            return None

        if self.is_in_cooldown(country_iso, now):
            logger.info(f"Suppressed alert for {country_iso} due to active {self.cooldown_hours}h cooldown.")
            return None

        country_info = get_country_info(country_iso)
        country_name = country_info.get("name", country_iso)

        top_contribs = [
            {"category": "Conflict", "score": contributing_factors.get("conflict_score", 0)},
            {"category": "Security", "score": contributing_factors.get("security_score", 0)},
            {"category": "Economy", "score": contributing_factors.get("economy_score", 0)},
            {"category": "Diplomacy", "score": contributing_factors.get("diplomacy_score", 0)},
        ]
        top_contribs.sort(key=lambda x: x["score"], reverse=True)

        alert_payload = {
            "country": country_iso,
            "country_name": country_name,
            "risk_score": float(risk_score),
            "tier": tier,
            "trigger": "critical_threshold",
            "timestamp": now.isoformat(),
            "top_contributors": top_contribs,
            "evidence": contributing_factors.get("top_event_ids", []),
        }

        # Persist alert record to database
        alert_obj = Alert(
            alert_id=str(uuid.uuid4()),
            country_iso=country_iso,
            risk_score=risk_score,
            trigger_tier=tier,
            trigger_reason="critical_threshold",
            payload=alert_payload,
            sent_at=now,
        )
        session.add(alert_obj)

        # Update cooldown timestamp
        self._last_alerted[country_iso] = now

        # Broadcast via WebSockets to connected browsers
        await ws_dispatcher.broadcast_alert(alert_payload)
        logger.info(f"Dispatched critical alert for {country_iso} (Risk: {risk_score})")

        return alert_payload

alert_manager = AlertManager()
