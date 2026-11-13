import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger("geosentinel.alerts.webhooks")

class AlertWebhookDispatcher:
    """
    Dispatches automated real-time tactical flash advisories to Discord and Telegram
    when critical geopolitical risk thresholds (R_c(t) > 75) are breached.
    """

    async def dispatch_critical_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats and broadcasts a tactical advisory across configured external webhooks.
        """
        results = {"discord": "skipped", "telegram": "skipped"}
        if not settings.WEBHOOKS_ENABLED:
            return results

        country_iso = alert_data.get("country_iso", "GLOBAL")
        risk_score = alert_data.get("risk_score", 0.0)
        dominant_factor = alert_data.get("dominant_factor", "CONFLICT")
        headline = alert_data.get("headline", "Critical Geopolitical Risk Threshold Exceeded")
        alert_id = alert_data.get("alert_id", "FLASH-ALERT")

        # 1. Dispatch Discord Webhook
        if settings.DISCORD_WEBHOOK_URL:
            try:
                discord_payload = {
                    "username": "GeoSentinel Enterprise Tactical Dispatcher",
                    "avatar_url": "https://raw.githubusercontent.com/praneetpravin/geosentinel-ai/master/frontend/public/favicon.ico",
                    "embeds": [
                        {
                            "title": f"🚨 GEOSENTINEL FLASH ADVISORY: {country_iso} BREACH",
                            "description": headline,
                            "color": 15158332 if risk_score > 75 else 15105570,  # Red / Orange
                            "fields": [
                                {"name": "Country ISO", "value": f"`{country_iso}`", "inline": True},
                                {"name": "Risk Index", "value": f"**{risk_score:.1f}/100 (Severe)**", "inline": True},
                                {"name": "Dominant Factor", "value": f"`{dominant_factor}`", "inline": True},
                                {"name": "Alert ID", "value": f"`{alert_id}`", "inline": True},
                                {"name": "Attribution", "value": "GeoSentinel GTOC", "inline": True},
                            ],
                            "footer": {
                                "text": "GeoSentinel Enterprise Global Threat Operations Center (GTOC)"
                            },
                        }
                    ],
                }
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.post(settings.DISCORD_WEBHOOK_URL, json=discord_payload)
                    results["discord"] = "dispatched" if resp.status_code in (200, 204) else f"error_{resp.status_code}"
            except Exception as e:
                logger.warning(f"Discord webhook failed: {e}")
                results["discord"] = f"error: {str(e)}"

        # 2. Dispatch Telegram Bot Broadcast
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            try:
                telegram_msg = (
                    f"🚨 <b>GEOSENTINEL FLASH ADVISORY: {country_iso}</b>\n\n"
                    f"<b>Risk Index:</b> <code>{risk_score:.1f}/100</code> (Severe Risk)\n"
                    f"<b>Dominant Factor:</b> <code>{dominant_factor}</code>\n"
                    f"<b>Headline:</b> {headline}\n\n"
                    f"🔗 <a href='{settings.FRONTEND_URL}'>Open Live Tactical Dossier</a>\n"
                    f"<i>GeoSentinel Enterprise • Global Threat Operations Center (GTOC)</i>"
                )
                tg_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.post(
                        tg_url,
                        json={
                            "chat_id": settings.TELEGRAM_CHAT_ID,
                            "text": telegram_msg,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": False,
                        },
                    )
                    results["telegram"] = "dispatched" if resp.status_code == 200 else f"error_{resp.status_code}"
            except Exception as e:
                logger.warning(f"Telegram webhook failed: {e}")
                results["telegram"] = f"error: {str(e)}"

        return results

webhook_dispatcher = AlertWebhookDispatcher()
