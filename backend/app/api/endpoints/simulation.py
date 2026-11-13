from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.country_score import CountryScore
from app.models.event import Event
from app.scoring.risk_engine import risk_engine
from app.forecasting.engine import forecasting_engine
from app.utils.iso_countries import get_country_info, COUNTRY_DATABASE
from app.api.endpoints.auth import require_permission

router = APIRouter()

class SimulationRequest(BaseModel):
    country_iso: str = Field(..., description="ISO 3166-1 alpha-3 code")
    scenario_title: str = Field(..., description="Tactical scenario description")
    category: str = Field("CONFLICT", description="Event category: CONFLICT, SECURITY, ECONOMY, DIPLOMACY")
    sentiment: float = Field(-0.85, ge=-1.0, le=1.0, description="Sentiment polarity")
    credibility: float = Field(0.95, ge=0.1, le=1.0, description="Source credibility")
    injected_incidents_count: int = Field(3, ge=1, le=25, description="Number of concurrent tactical strikes/incidents")
    spillover_countries: Optional[List[str]] = Field(default_factory=list, description="Allied or border countries impacted")
    notes: Optional[str] = None

class SimulationResponse(BaseModel):
    country_iso: str
    country_name: str
    scenario_title: str
    baseline_risk: float
    baseline_tier: str
    simulated_risk: float
    simulated_tier: str
    risk_delta: float
    is_critical_breach: bool
    contributing_factors: Dict[str, Any]
    projected_trajectory: List[Dict[str, Any]]
    spillover_effects: List[Dict[str, Any]]

PRESET_SCENARIOS = [
    {
        "id": "red_sea_interdiction",
        "title": "Red Sea Maritime Chokepoint Interdiction",
        "country_iso": "YEM",
        "category": "CONFLICT",
        "sentiment": -0.90,
        "credibility": 0.95,
        "injected_incidents_count": 4,
        "spillover_countries": ["SAU", "EGY", "ISR"],
        "description": "Multiple anti-ship missile and one-way drone strikes against commercial container vessels transiting the Bab-el-Mandeb strait.",
    },
    {
        "id": "eastern_frontline_surge",
        "title": "Major Frontline Artillery & Air Defense Surge",
        "country_iso": "UKR",
        "category": "CONFLICT",
        "sentiment": -0.95,
        "credibility": 0.98,
        "injected_incidents_count": 6,
        "spillover_countries": ["RUS", "POL", "DEU"],
        "description": "Coordinated multi-axis kinetic bombardment targeting defense logistics nodes and critical energy transmission grids.",
    },
    {
        "id": "semiconductor_export_embargo",
        "title": "Bilateral Advanced Semiconductor Embargo",
        "country_iso": "TWN",
        "category": "ECONOMY",
        "sentiment": -0.80,
        "credibility": 0.92,
        "injected_incidents_count": 3,
        "spillover_countries": ["CHN", "USA", "JPN"],
        "description": "Sudden regulatory trade embargo and maritime customs cordon targeting high-end lithography tools and wafer fabs.",
    },
    {
        "id": "critical_grid_cyber_offensive",
        "title": "Critical Infrastructure Power Grid Cyber Assault",
        "country_iso": "USA",
        "category": "SECURITY",
        "sentiment": -0.85,
        "credibility": 0.90,
        "injected_incidents_count": 3,
        "spillover_countries": ["GBR", "CAN"],
        "description": "Zero-day SCADA malware exploitation inducing rolling transmission disconnects across metropolitan substation corridors.",
    },
]

@router.get("/simulation/templates")
async def get_simulation_templates():
    """Returns curated tactical scenario templates for decision-maker sandbox testing."""
    return PRESET_SCENARIOS

@router.post("/simulation/run", response_model=SimulationResponse)
async def run_scenario_simulation(
    req: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permission("simulate")),
):
    """
    Executes a sandbox 'What-If' simulation using the exact closed-form risk formula (Eq. 1).
    Calculates score deltas, tier transitions, and 7-day projected forward trajectory.
    """
    c_iso = req.country_iso.upper()
    country_info = get_country_info(c_iso)
    country_name = country_info.get("name", c_iso)

    # 1. Fetch baseline events and current risk score
    score_stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
    score_res = await db.execute(score_stmt)
    baseline_obj = score_res.scalars().first()

    baseline_risk = baseline_obj.risk_index if baseline_obj else 15.0
    baseline_tier = baseline_obj.risk_tier if baseline_obj else "Low"

    # Fetch active events from the last 30 days
    ev_stmt = select(Event).where(Event.country_iso == c_iso)
    ev_res = await db.execute(ev_stmt)
    db_events = ev_res.scalars().all()

    active_events_data = [
        {
            "event_id": ev.event_id,
            "category": ev.category,
            "sentiment": ev.sentiment,
            "credibility": ev.severity if ev.severity else 0.85,
            "timestamp": ev.timestamp,
        }
        for ev in db_events
    ]

    now = datetime.now(timezone.utc)

    # 2. Inject hypothetical scenario events
    injected_events = list(active_events_data)
    for i in range(req.injected_incidents_count):
        injected_events.append({
            "event_id": f"sim_incident_{i+1}",
            "category": req.category.upper(),
            "sentiment": req.sentiment,
            "credibility": req.credibility,
            "timestamp": now,
        })

    # 3. Calculate simulated risk via closed-form equation
    sim_result = risk_engine.calculate_country_risk(injected_events, current_time=now)
    simulated_risk = sim_result["risk_index"]
    simulated_tier = sim_result["risk_tier"]
    risk_delta = round(simulated_risk - baseline_risk, 2)
    is_critical = risk_engine.is_critical_alert(simulated_risk)

    # 4. Generate projected trajectory under simulated conditions
    history = [baseline_risk, baseline_risk + (risk_delta * 0.4), simulated_risk]
    forecast_points = forecasting_engine.generate_forecast(
        current_risk=simulated_risk,
        history_points=history,
        days=7,
    )

    # 5. Model regional spillover contagion
    spillover_effects = []
    for sp_iso in (req.spillover_countries or []):
        sp_iso_clean = sp_iso.strip().upper()
        if sp_iso_clean == c_iso:
            continue
        sp_info = get_country_info(sp_iso_clean)
        # Regional transmission ratio ~25% to 40% of primary crisis delta
        spillover_bump = round(risk_delta * 0.35, 2)
        spillover_effects.append({
            "country_iso": sp_iso_clean,
            "country_name": sp_info.get("name", sp_iso_clean),
            "estimated_contagion_risk_bump": max(0.5, spillover_bump),
            "transmission_vector": f"Adjacent {req.category.lower()} vulnerability and trade corridor interdependence.",
        })

    return SimulationResponse(
        country_iso=c_iso,
        country_name=country_name,
        scenario_title=req.scenario_title,
        baseline_risk=baseline_risk,
        baseline_tier=baseline_tier,
        simulated_risk=simulated_risk,
        simulated_tier=simulated_tier,
        risk_delta=risk_delta,
        is_critical_breach=is_critical,
        contributing_factors=sim_result["contributing_factors"],
        projected_trajectory=forecast_points,
        spillover_effects=spillover_effects,
    )
