"""
GeoSentinel AI - ML Dataset Preparation
Constructs stratified geopolitical text classification splits for CONFLICT, SECURITY, ECONOMY, DIPLOMACY.
Ensures scenario-disjoint splits to strictly prevent train/test data leakage.
AKGEC Department of IT | CSIT Group 32
"""
import os
import json
import random

CATEGORY_TEMPLATES = {
    "CONFLICT": [
        "Artillery shelling and rocket strikes hit strategic frontline logistics depots causing casualties.",
        "Naval battle groups launched guided cruise missiles targeting fortified coastal command positions.",
        "Infantry battalions engaged in intense urban combat as cross-border firefights erupted.",
        "Airstrikes destroyed ammunition bunkers and rail supply arteries in contested southern theater.",
        "Border skirmishes escalated following heavy mortar fire exchange along mountain forward outposts.",
        "Armed drone strikes struck military barracks resulting in severe personnel casualties.",
        "Hostile militias initiated a coordinated offensive against sovereign defensive perimeter garrisons.",
        "Tactical ballistic missiles impacted forward air defense positions across the frontline corridor.",
        "Heavy armor columns advanced toward contested river crossings under intense counter-battery fire.",
        "Combat aircraft conducted low-altitude precision strikes against insurgent training encampments.",
        "Cross-border rocket salvos targeted civilian settlements and military command outposts overnight.",
        "Special forces commandos engaged hostile insurgents during counter-ambush operations in forest valleys.",
        "Trench warfare intensified as mechanized units launched coordinated counterattacks along defensive lines.",
        "Naval frigates repelled hostile explosive-laden unmanned surface vessels near offshore natural gas platforms.",
        "Anti-tank guided missiles destroyed multiple armored transport vehicles in disputed valley.",
        "Mortar rounds struck forward radar stations as rebel factions breached the sovereign security buffer zone.",
        "Precision glide bombs demolished fortified tunnel complexes housing heavy weapons caches.",
        "Helicopter gunships provided continuous close air support during ground operations against armed militants.",
        "Amphibious assault ships deployed marine contingents to reinforce contested island outposts.",
        "Multiple rocket launcher systems conducted prolonged barrages against fortified enemy trench networks.",
        "Sniper engagements along the armistice line resulted in fatal casualties among patrolling soldiers.",
        "Guerrilla combatants ambushed a military supply convoy utilizing improvised explosive devices and small arms.",
        "Surface-to-surface cruise missiles targeted energy infrastructure installations near active battle zones.",
        "Military hospital complexes reported high casualty admissions following sustained heavy artillery barrages.",
        "Fighter interceptors engaged hostile strike fighters attempting deep airspace penetration over contested provinces.",
    ],
    "SECURITY": [
        "State cyber defense command blocked coordinated ransomware assault targeting national power grid substations.",
        "Military intelligence services detained hostile reconnaissance drone operators near airbase perimeter.",
        "Strategic ballistic missile brigades commenced operational readiness maneuvers with road-mobile launchers.",
        "Maritime patrol aircraft detected unidentified submarines operating within exclusive economic exclusion zones.",
        "Counter-terrorism units executed pre-dawn search raids seizing military-grade encrypted communication equipment.",
        "National security council deployed anti-aircraft batteries around sovereign government installations.",
        "Paramilitary border patrols established strict perimeter cordons following unauthorized airspace incursions.",
        "Electronic warfare units deployed active radar jamming systems across northern defense sectors.",
        "Internal security services dismantled foreign espionage ring operating near sensitive aerospace laboratories.",
        "Coast guard cutters intercepted suspicious cargo vessel carrying unregistered dual-use optical sensors.",
        "Emergency civil protection agencies conducted nationwide disaster response and air-raid siren readiness exercises.",
        "Police anti-riot brigades contained civil unrest following disputed municipal assembly elections.",
        "Defense intelligence agency issued alert regarding suspected state-sponsored cyber penetration of telecom networks.",
        "Critical infrastructure protection agency hardened water treatment facilities against remote SCADA tampering.",
        "Border security guards seized clandestine cache of automatic rifles and night-vision optics at mountain checkpoint.",
        "Defense ministry announced emergency deployment of early warning radar arrays to monitor maritime approaches.",
        "Homeland security agents intercepted illicit nuclear isotope shipments concealed within industrial shipping containers.",
        "Armed forces initiated joint interoperability live-fire exercises simulating high-intensity multi-domain defense.",
        "Intelligence task force identified state-backed APT groups conducting spear-phishing campaigns against defense contractors.",
        "National port authority elevated maritime security tier following underwater acoustic detection of diver propulsion vehicles.",
        "Federal communications commission revoked operating licenses for foreign communications equipment citing national security risks.",
        "Anti-sabotage inspection teams reinforced structural security along vital cross-country petroleum pipelines.",
        "Sovereign space command tracked foreign inspection satellites performing proximity maneuvers near defensive satellites.",
        "Specialized bomb disposal technicians neutralized remote-detonation ordnance discovered near railway hub.",
        "Internal affairs ministry reinforced border biometric screening protocols following intelligence threat advisory.",
    ],
    "ECONOMY": [
        "Commerce authorities enforced strict export curbs on high-end semiconductor foundry equipment and rare earth ores.",
        "Sovereign credit rating downgraded following severe foreign exchange depletion and energy import debt defaults.",
        "Maritime shipping insurers surged war-risk premiums after naval drone threats disrupted strategic chokepoint transit.",
        "Bilateral trade sanctions imposed on critical banking networks freezing cross-border capital liquidity.",
        "Energy ministers negotiated emergency gas reserve quotas to counter deep pipeline supply bottlenecks.",
        "National treasury announced emergency currency stabilization measures amidst escalating inflation.",
        "Export embargoes enacted on agricultural commodities and critical fertilizer minerals.",
        "Industrial manufacturing slowed down as container supply chains faced severe maritime diversions.",
        "Central bank raised benchmark interest rates by 75 basis points to stabilize sliding currency exchange rate.",
        "Crude oil futures spiked sharply following unexpected supply disruption at major export terminal.",
        "Customs authorities halted grain shipments at border crossings pending bilateral tariff renegotiations.",
        "Mining conglomerates suspended lithium extraction operations following nationalization decree.",
        "Government debt auction faced subdued institutional demand pushing 10-year sovereign bond yields to multi-year highs.",
        "Commercial air carriers rerouted international freight corridors to avoid airspace transit fees.",
        "Bilateral currency swap agreement signed between regional central banks to facilitate non-dollar trade settlement.",
        "Ministry of finance announced sovereign debt restructuring negotiations with international creditor committees.",
        "Global container shipping rates doubled overnight following closure of key commercial transit canals.",
        "National stock exchange triggered automatic circuit breakers following steep selloffs in banking sector shares.",
        "Petrochemical refineries reduced processing capacity due to embargoed crude oil feedstock delivery delays.",
        "Trade ministry slapped punitive countervailing duties on imported electric vehicles and industrial steel.",
        "Foreign direct investment inflows plunged to historic lows amidst heightened regulatory expropriation fears.",
        "Agricultural commodities board warned of acute grain shortages following drought and fertilizer export restrictions.",
        "Multilateral development bank froze concessional development loans pending sovereign fiscal governance audits.",
        "Central bank governor intervened in foreign exchange markets selling foreign reserves to defend currency peg.",
        "Major energy multinational declared force majeure on liquefied natural gas long-term delivery contracts.",
    ],
    "DIPLOMACY": [
        "Heads of state concluded high-level bilateral peace talks signing an enduring maritime demarcation treaty.",
        "Special diplomatic envoys submitted revised ceasefire roadmap draft to the United Nations Security Council.",
        "Foreign ministry dispatched goodwill delegation to mediate de-escalation protocols along border buffer corridors.",
        "Ambassadors convened multilateral summit in Geneva reaching consensus on humanitarian relief convoy corridors.",
        "Neighboring governments exchanged ratified diplomatic accords establishing shared maritime environmental protections.",
        "Ministers of foreign affairs held emergency trilateral talks to establish diplomatic dialogue channels.",
        "Peace summit delegates initialed a preliminary disarmament framework under international supervision.",
        "Consular relations restored between regional powers following successful ambassadorial consultations.",
        "Regional security organization held annual ministerial summit adopting non-aggression joint declaration.",
        "United Nations special rapporteur conducted fact-finding mission examining humanitarian access across conflict line.",
        "Bilateral border delimitation commission concluded fourth round of boundary verification demarcations.",
        "Diplomatic mission reopened after five-year suspension of formal ambassadorial ties.",
        "Joint communique reaffirmed mutual commitment to peaceful resolution of outstanding sovereignty disputes.",
        "International mediators proposed demilitarized buffer zone along contested frontier corridor.",
        "Foreign ambassadors summoned to ministry of foreign affairs to receive formal diplomatic protest note.",
        "Plenipotentiary representatives signed comprehensive mutual extradition and legal assistance pact.",
        "General assembly delegates adopted landmark resolution establishing multinational peacekeeping observation mandate.",
        "State leaders held confidential bilateral retreat discussing terms for restoring severed diplomatic representation.",
        "Foreign secretary welcomed international observer delegation monitoring parliamentary election integrity.",
        "High-level emissaries negotiated exchange of detained diplomatic personnel following protracted backchannel talks.",
        "Regional cooperation council established permanent secretariat to coordinate cross-border disaster protocols.",
        "Peace negotiations resumed in neutral capital following acceptance of revised mediation framework.",
        "Permanent representative to the UN delivered formal address urging adherence to international humanitarian law.",
        "Government issued formal diplomatic demarche protesting extraterritorial maritime jurisdiction claims.",
        "Trilateral working group concluded technical negotiations on shared river water sharing treaty.",
    ],
}

def prepare_splits(output_dir: str = None):
    if output_dir is None:
        base_dir = os.path.dirname(__file__)
        output_dir = os.path.abspath(os.path.join(base_dir, "../../data/processed"))
    os.makedirs(output_dir, exist_ok=True)

    # Scenario-Disjoint Partitioning:
    # We partition base templates (75% train, 25% test) before generating any stylistic variations.
    # This guarantees ZERO data leakage between train and test splits!
    train_data = []
    test_data = []

    rng = random.Random(42)

    for cat, base_sentences in CATEGORY_TEMPLATES.items():
        split_idx = int(len(base_sentences) * 0.80)
        train_templates = base_sentences[:split_idx]
        test_templates = base_sentences[split_idx:]

        # For train set: expand with diverse journalistic framing
        for sent in train_templates:
            train_data.append({"text": sent, "label": cat})
            train_data.append({"text": f"Reports confirm that {sent[:1].lower() + sent[1:]}", "label": cat})
            train_data.append({"text": f"According to defense and intelligence dispatches: {sent}", "label": cat})

        # For test set: independent out-of-sample holdout test items
        for sent in test_templates:
            test_data.append({"text": sent, "label": cat})
            test_data.append({"text": f"Official news wires report: {sent}", "label": cat})

    # Shuffle final splits
    rng.shuffle(train_data)
    rng.shuffle(test_data)

    with open(os.path.join(output_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2)

    with open(os.path.join(output_dir, "test.json"), "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)

    print(f"Prepared {len(train_data)} train examples and {len(test_data)} test examples in {output_dir}")
    print("Guaranteed scenario-disjoint splits: ZERO train/test data leakage.")

if __name__ == "__main__":
    prepare_splits()
