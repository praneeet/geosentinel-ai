from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.country_score import CountryScore
from app.models.playbook import PlaybookModel
from app.utils.iso_countries import get_country_info

router = APIRouter()

class PlaybookQuantifiedImpact(BaseModel):
    schedule_variance: str
    fuel_or_cost_delta: str
    insurance_surcharge: str
    total_financial_variance: str
    threat_reduction_pct: str

class TacticalActionStep(BaseModel):
    step_number: int
    operational_phase: str
    directive: str
    responsible_team: str
    timeframe: str

class OperationalPlaybook(BaseModel):
    playbook_id: str
    title: str
    category: str
    trigger_threshold: str
    threat_theater: str
    executive_summary: str
    quantified_impact: PlaybookQuantifiedImpact
    recommended_option: str
    prescriptive_action_plan: List[TacticalActionStep]
    bimco_legal_clauses: List[str]

ENTERPRISE_PLAYBOOKS: List[Dict[str, Any]] = [
    {
        "playbook_id": "pb-red-sea-interdiction",
        "title": "Red Sea Transit Interdiction & Cape of Good Hope Diversion Playbook",
        "category": "MARITIME_LOGISTICS",
        "trigger_threshold": "Bab el-Mandeb littoral risk R_c(t) > 60 or naval drone strike reported within 200 km.",
        "threat_theater": "Southern Red Sea / Gulf of Aden / Suez Transit Corridor",
        "executive_summary": (
            "Anti-ship ballistic missile and one-way drone attacks present acute hull loss and crew casualty risks. "
            "Commercial transit through Suez requires either astronomical war-risk premiums or rerouting around the Cape of Good Hope."
        ),
        "quantified_impact": {
            "schedule_variance": "+11 to 14 Days transit delay",
            "fuel_or_cost_delta": "+$420,000 to $580,000 bunker fuel per voyage",
            "insurance_surcharge": "+0.75% to 1.10% of vessel hull value (approx $320,000 saved by diversion)",
            "total_financial_variance": "Net saving of ~$140,000 via Cape diversion vs Red Sea insured transit",
            "threat_reduction_pct": "98.5% reduction in kinetic strike vulnerability",
        },
        "recommended_option": "Cape of Good Hope Southern African Circum-navigation",
        "prescriptive_action_plan": [
            {
                "step_number": 1,
                "operational_phase": "IMMEDIATE FLEET ORDER",
                "directive": "Transmit immediate course deviation orders to all westbound vessels north of Salalah; hold at Port of Salalah anchor.",
                "responsible_team": "Global Marine Operations & Vessel Traffic Management",
                "timeframe": "0 - 2 Hours",
            },
            {
                "step_number": 2,
                "operational_phase": "CONTRACTUAL & LEGAL NOTICE",
                "directive": "Issue formal Notice of Force Majeure and War Risks Clause (BIMCO CONWARTIME 2004 / VOYWAR 2013) to charterers.",
                "responsible_team": "Corporate Legal & Risk Advisory",
                "timeframe": "2 - 6 Hours",
            },
            {
                "step_number": 3,
                "operational_phase": "BUNKER & LOGISTICS RESCHEDULING",
                "directive": "Book emergency bunkering stems at Port Louis (Mauritius) or Durban (South Africa) to support extended 14-day passage.",
                "responsible_team": "Global Fuel Procurement & Port Operations",
                "timeframe": "6 - 12 Hours",
            },
            {
                "step_number": 4,
                "operational_phase": "SUPPLY CHAIN NOTIFICATION",
                "directive": "Notify European distribution terminals (Rotterdam, Antwerp, Hamburg) of updated vessel ETAs (+13 days) to reschedule berth allocation.",
                "responsible_team": "Customer Supply Chain Operations",
                "timeframe": "12 - 24 Hours",
            },
        ],
        "bimco_legal_clauses": [
            "BIMCO CONWARTIME 2004 (Standard War Risk Clause for Time Charters)",
            "VOYWAR 2013 (Voyage Charter War Risks Clause)",
            "Institute War Clauses (Cargo / Hulls)",
        ],
    },
    {
        "playbook_id": "pb-taiwan-semiconductor-bridge",
        "title": "Taiwan Strait Semiconductor Supply Chain Air-Bridge Playbook",
        "category": "SUPPLY_CHAIN",
        "trigger_threshold": "Taiwan Strait naval blockade posture or cross-strait military escalation index > 65.",
        "threat_theater": "Taiwan Strait, Hsinchu Science Park, East China Sea Maritime Lanes",
        "executive_summary": (
            "Maritime customs cordon or military exercise cordons threaten containerized sea freight of advanced microelectronics. "
            "Activates emergency dedicated air-cargo corridors to preserve global manufacturing continuity."
        ),
        "quantified_impact": {
            "schedule_variance": "-22 Days faster than ocean freight (36 hrs vs 24 days)",
            "fuel_or_cost_delta": "+$6.80 / kg air cargo premium over ocean container",
            "insurance_surcharge": "+0.25% high-value cargo transit policy",
            "total_financial_variance": "+$85,000 per 10-ton shipment (mitigates potential $45M production stoppage)",
            "threat_reduction_pct": "100% bypass of maritime maritime naval cordons",
        },
        "recommended_option": "Emergency Trans-Pacific Air-Bridge (Taipei TPE -> Anchorage ANC -> Chicago ORD / Frankfurt FRA)",
        "prescriptive_action_plan": [
            {
                "step_number": 1,
                "operational_phase": "INVENTORY SWEEP",
                "directive": "Audit all 3nm and 5nm finished wafer lots at Hsinchu Fab 18 and Taichung packaging facilities.",
                "responsible_team": "Semiconductor Supply Operations",
                "timeframe": "0 - 4 Hours",
            },
            {
                "step_number": 2,
                "operational_phase": "AIR CARGO CHARTER",
                "directive": "Exercise wet-lease block space agreement for 3 Boeing 777F cargo flights via Taipei Taoyuan International (TPE).",
                "responsible_team": "Global Air Freight Logistics",
                "timeframe": "4 - 8 Hours",
            },
            {
                "step_number": 3,
                "operational_phase": "SAFETY STOCK EXPANSION",
                "directive": "Authorize emergency buffer inventory expansion at European and North American assembly hubs from 30 days to 90 days.",
                "responsible_team": "Chief Procurement Officer (CPO) Council",
                "timeframe": "8 - 24 Hours",
            },
        ],
        "bimco_legal_clauses": [
            "Montreal Convention 1999 (Air Carrier Liability)",
            "Incoterms 2020 CIP (Carriage and Insurance Paid to)",
        ],
    },
    {
        "playbook_id": "pb-critical-infrastructure-cyber",
        "title": "Industrial SCADA & Power Transmission Cyber Defense Playbook",
        "category": "CYBER_DEFENSE",
        "trigger_threshold": "Zero-day exploitation detected targeting regional energy or cloud infrastructure corridors.",
        "threat_theater": "Metropolitan Power Transmission & Hyperscale Cloud Interconnects",
        "executive_summary": (
            "State-sponsored cyber offensive targeting substations or cloud backbones requires emergency network segmentation "
            "and failover to isolated out-of-band management channels."
        ),
        "quantified_impact": {
            "schedule_variance": "Zero operational downtime during redundant failover",
            "fuel_or_cost_delta": "Generator fuel burn: $4,200 / hr during islanded grid mode",
            "insurance_surcharge": "Coverage validated under Lloyd's Cyber Catastrophe Policy",
            "total_financial_variance": "Prevents catastrophic $12M/hr manufacturing blackout penalties",
            "threat_reduction_pct": "92.0% containment of lateral network traversal",
        },
        "recommended_option": "Air-Gapped Substation Isolation & Secondary Cloud Backbone Failover",
        "prescriptive_action_plan": [
            {
                "step_number": 1,
                "operational_phase": "AIR-GAP ACTIVATION",
                "directive": "Isolate all substation Remote Terminal Units (RTUs) and switchgear from external telemetry interfaces.",
                "responsible_team": "Industrial Cyber Defense (OT Security)",
                "timeframe": "0 - 15 Minutes",
            },
            {
                "step_number": 2,
                "operational_phase": "BGP TRAFFIC SCRUBBING",
                "directive": "Reroute cloud border routing BGP announcements through Tier-1 DDoS mitigation scrubbers.",
                "responsible_team": "Global Network Engineering (NetOps)",
                "timeframe": "15 - 45 Minutes",
            },
            {
                "step_number": 3,
                "operational_phase": "EXECUTIVE STATUS BRIEF",
                "directive": "Deliver C-suite status brief confirming containment and triggering incident response forensic retention.",
                "responsible_team": "Chief Information Security Officer (CISO)",
                "timeframe": "1 - 2 Hours",
            },
        ],
        "bimco_legal_clauses": [
            "NIST SP 800-61 Incident Handling Standards",
            "CISA Emergency Directive Protocols",
        ],
    },
]

def playbook_model_to_dict(m: PlaybookModel) -> Dict[str, Any]:
    return {
        "playbook_id": m.playbook_id,
        "title": m.title,
        "category": m.category,
        "trigger_threshold": m.trigger_threshold,
        "threat_theater": m.threat_theater,
        "executive_summary": m.executive_summary,
        "quantified_impact": m.quantified_impact or {},
        "recommended_option": m.recommended_option,
        "prescriptive_action_plan": m.prescriptive_action_plan or [],
        "bimco_legal_clauses": m.bimco_legal_clauses or [],
    }

@router.get("/playbooks", response_model=List[OperationalPlaybook])
async def list_playbooks(db: AsyncSession = Depends(get_db)):
    """Returns curated prescriptive crisis playbooks with quantified operational and financial impacts."""
    stmt = select(PlaybookModel)
    res = await db.execute(stmt)
    db_playbooks = res.scalars().all()

    if not db_playbooks:
        # Seed initial playbooks into database
        for p in ENTERPRISE_PLAYBOOKS:
            db_obj = PlaybookModel(
                playbook_id=p["playbook_id"],
                title=p["title"],
                category=p["category"],
                trigger_threshold=p["trigger_threshold"],
                threat_theater=p["threat_theater"],
                executive_summary=p["executive_summary"],
                quantified_impact=p["quantified_impact"],
                recommended_option=p["recommended_option"],
                prescriptive_action_plan=p["prescriptive_action_plan"],
                bimco_legal_clauses=p["bimco_legal_clauses"],
            )
            db.add(db_obj)
        await db.commit()
        res = await db.execute(select(PlaybookModel))
        db_playbooks = res.scalars().all()

    return [OperationalPlaybook(**playbook_model_to_dict(p)) for p in db_playbooks]

@router.get("/playbooks/{playbook_id}", response_model=OperationalPlaybook)
async def get_playbook(playbook_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves operational execution steps and BIMCO contract clauses for a specific playbook."""
    stmt = select(PlaybookModel).where(PlaybookModel.playbook_id == playbook_id)
    res = await db.execute(stmt)
    db_obj = res.scalars().first()

    if db_obj:
        return OperationalPlaybook(**playbook_model_to_dict(db_obj))

    pb = next((p for p in ENTERPRISE_PLAYBOOKS if p["playbook_id"] == playbook_id), None)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return OperationalPlaybook(**pb)
