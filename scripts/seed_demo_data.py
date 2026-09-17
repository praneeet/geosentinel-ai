import sys
import os
import asyncio

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import init_db, async_session_factory
from app.ingestion.service import ingestion_service
from app.models.country_score import CountryScore
from sqlalchemy import select

async def main():
    print("[GeoSentinel AI] Initializing schema...")
    await init_db()
    print("[GeoSentinel AI] Triggering ingestion pipeline...")
    async with async_session_factory() as session:
        result = await ingestion_service.run_pipeline(session)
        print("[GeoSentinel AI] Ingestion Result:")
        for k, v in result.items():
            print(f"  {k}: {v}")

        print("\n[GeoSentinel AI] Country Risk Scores:")
        scores_res = await session.execute(select(CountryScore).order_by(CountryScore.risk_index.desc()))
        scores = scores_res.scalars().all()
        for s in scores:
            print(f"  [{s.country_iso}] Risk Index: {s.risk_index:.1f}/100 ({s.risk_tier}) - Events: {s.event_count}")

if __name__ == "__main__":
    asyncio.run(main())
