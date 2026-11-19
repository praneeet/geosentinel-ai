import uuid
import asyncio
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
    Thread and concurrency safe.
    """

    def __init__(self, cooldown_hours: int = settings.ALERT_COOLDOWN_HOURS):
        self.cooldown_hours = cooldown_hours
        # In-memory fast cache for country last-alert timestamps: {country_iso: datetime}
        self._last_alerted: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def is_in_cooldown(self, country_iso: str, session: Optional[AsyncSession] = None, now: datetime = None) -> bool:
        current = now or datetime.now(timezone.utc)
        # 1. Fast in-memory check
        last_time = self._last_alerted.get(country_iso)
        if last_time and (current - last_time) < timedelta(hours=self.cooldown_hours):
            return True
        # 2. Persistent database check across worker processes & restarts
        if session is not None:
            try:
                cutoff = current - timedelta(hours=self.cooldown_hours)
                stmt = select(Alert).where(
                    Alert.country_iso == country_iso,
                    Alert.sent_at >= cutoff
                ).limit(1)
                res = await session.execute(stmt)
                existing = res.scalars().first()
                if existing:
                    self._last_alerted[country_iso] = existing.sent_at or current
                    return True
            except Exception:
                pass
        return False

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
        Strict atomic concurrency protection via async mutex covering check, persist, and cooldown update.
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            if risk_score <= settings.ALERT_CRITICAL_THRESHOLD:
                return None

            if await self.is_in_cooldown(country_iso, session=session, now=now):
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
            # Commit alert to database first so it is permanently persisted before broadcast
            await session.commit()

            # Update cooldown timestamp inside lock
            self._last_alerted[country_iso] = now

        # Broadcast via WebSockets to connected browsers only AFTER successful persistence
        await ws_dispatcher.broadcast_alert(alert_payload)
        logger.info(f"Dispatched critical alert for {country_iso} (Risk: {risk_score:.1f})")

        # Broadcast via Discord & Telegram External Webhooks
        try:
            from app.alerts.webhooks import webhook_dispatcher
            dominant = top_contribs[0]["category"].upper() if top_contribs else "CONFLICT"
            await webhook_dispatcher.dispatch_critical_alert({
                "country_iso": country_iso,
                "risk_score": float(risk_score),
                "dominant_factor": dominant,
                "headline": f"Critical risk threshold breached in {country_name} ({country_iso}) with index {risk_score:.1f}/100.",
                "alert_id": alert_obj.alert_id,
            })
        except Exception as e:
            logger.warning(f"Webhook dispatch error: {e}")

        return alert_payload

alert_manager = AlertManager()
