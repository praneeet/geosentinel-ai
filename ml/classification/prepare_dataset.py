"""
GeoSentinel AI - ML Dataset Preparation
Constructs stratified geopolitical text classification splits for CONFLICT, SECURITY, ECONOMY, DIPLOMACY.
AKGEC Department of IT | CSIT Group 32
"""
import os
import json
from sklearn.model_selection import train_test_split

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
    ],
}

def prepare_splits(output_dir: str = None):
    if output_dir is None:
        base_dir = os.path.dirname(__file__)
        output_dir = os.path.abspath(os.path.join(base_dir, "../../data/processed"))
    os.makedirs(output_dir, exist_ok=True)

    data = []
    labels = []
    for cat, sentences in CATEGORY_TEMPLATES.items():
        for sent in sentences:
            data.append(sent)
            labels.append(cat)
            # Add realistic news style variations
            data.append(f"Reports confirm: {sent}")
            labels.append(cat)
            data.append(f"Government officials stated that {sent.lower()}")
            labels.append(cat)

    X_train, X_test, y_train, y_test = train_test_split(
        data, labels, test_size=0.25, random_state=42, stratify=labels
    )

    train_data = [{"text": t, "label": l} for t, l in zip(X_train, y_train)]
    test_data = [{"text": t, "label": l} for t, l in zip(X_test, y_test)]

    with open(os.path.join(output_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2)

    with open(os.path.join(output_dir, "test.json"), "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)

    print(f"Prepared {len(train_data)} train examples and {len(test_data)} test examples in {output_dir}")

if __name__ == "__main__":
    prepare_splits()
