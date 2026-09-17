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
