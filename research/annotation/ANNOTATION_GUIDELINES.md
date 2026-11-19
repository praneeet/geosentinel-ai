# GeoSentinel AI — Formal Annotation Guidelines & Protocol
**Document Version:** 1.0.0 | **Research Scope:** 1,000-Article Real-World Geopolitical Intelligence Corpus  
**Target Inter-Annotator Reliability:** Cohen's Kappa $\kappa \ge 0.80$ (Substantial to Almost Perfect Agreement)

---

## 1. Research Objective & Scope
The objective of this protocol is to construct a standardized, reproducible, and verifiable gold-standard evaluation corpus of 1,000+ real-world open-source intelligence (OSINT) articles for evaluating automated geopolitical threat classification, entity extraction, and time-decayed risk scoring.

Each article is independently reviewed by two trained annotators. Where discrepancies occur, a senior annotator adjudicates the final gold-standard label.

---

## 2. Four-Domain Geopolitical Taxonomy

### Domain 1: `CONFLICT` (Weight: 1.00)
- **Definition:** Direct, active kinetic engagements, armed clashes, military operations, and tactical violence involving sovereign armed forces, non-state insurgent groups, or armed militias.
- **Inclusion Criteria:**
  - Artillery, rocket, drone, and airstrikes against combatants or infrastructure.
  - Active troop maneuvers, frontline infantry engagements, trench combat.
  - Naval skirmishes, maritime missile launches, anti-ship attacks.
  - Casualties or battlefield losses resulting from kinetic military fire.
- **Exclusion Criteria:**
  - Non-kinetic troop deployment drills or routine exercises (Classify as `SECURITY`).
  - Pre-war political rhetoric without active kinetic engagement (Classify as `DIPLOMACY`).

### Domain 2: `SECURITY` (Weight: 0.80)
- **Definition:** State defense readiness, deterrence operations, intelligence/counter-intelligence activities, cyber defense, territorial policing, counter-terrorism, and internal stability measures.
- **Inclusion Criteria:**
  - Strategic missile deployments, military exercises, war games, air-defense readiness.
  - State-sponsored or advanced persistent threat (APT) cyber warfare, grid tampering.
  - Counter-terrorism raids, arms caches seizures, border interdictions.
  - Defense alliances, arms sales contracts, troop mobilization without active combat.
  - Civil unrest, state of emergency declarations, martial law enforcement.
- **Exclusion Criteria:**
  - Actual active frontline combat or strikes (Classify as `CONFLICT`).
  - Multilateral treaty ratifications (Classify as `DIPLOMACY`).

### Domain 3: `ECONOMY` (Weight: 0.55)
- **Definition:** Macroeconomic turbulence, trade restrictions, energy supply shocks, financial sanctions, currency instability, and critical supply chain disruptions induced by geopolitical crises.
- **Inclusion Criteria:**
  - Unilateral or multilateral economic sanctions, trade embargoes, asset freezes.
  - Sovereign debt default, severe currency depreciation, hyperinflation, central bank currency defense.
  - Energy commodity shocks (oil/gas price spikes, pipeline transit cutoffs).
  - Maritime trade corridor blockade, insurance war-risk surcharge hikes.
  - Export controls on dual-use technology, semiconductors, or critical minerals.
- **Exclusion Criteria:**
  - Routine fiscal announcements, standard quarterly GDP reports unrelated to geopolitical strife.

### Domain 4: `DIPLOMACY` (Weight: 0.35)
- **Definition:** Bilateral and multilateral statecraft, international negotiations, treaties, ambassadorial relations, summits, international arbitration, and crisis de-escalation protocols.
- **Inclusion Criteria:**
  - Peace negotiations, ceasefire roadmaps, armistice negotiations.
  - High-level summits (UN General Assembly, G20, ASEAN, NATO summits).
  - Expulsion or recall of ambassadors, formal diplomatic demarches, protest notes.
  - Joint bilateral declarations, trade agreements, humanitarian corridor pacts.
  - International Court of Justice (ICJ) or international arbitration proceedings.
- **Exclusion Criteria:**
  - Enforcement of punitive economic sanctions by a ministry of trade (Classify as `ECONOMY`).

---

## 3. Ambiguous Case Resolution & Hierarchy Rules
When an article spans multiple themes (e.g., peace talks while fighting continues, or sanctions accompanying military exercises), annotators MUST apply the following priority hierarchy:

1. **Dominant Causal Event Rule:** If the headline and $>60\%$ of body text report an active kinetic strike or battle, classify as `CONFLICT` even if peace talks are mentioned in passing.
2. **Action Over Intent Rule:** If kinetic conflict is actively occurring, kinetic violence supersedes diplomatic rhetoric.
3. **Primary Trigger Hierarchy:**
   $$\text{CONFLICT} \succ \text{SECURITY} \succ \text{ECONOMY} \succ \text{DIPLOMACY}$$
   *Example:* "Country X imposes retaliatory energy sanctions following missile attack on border":
   - If focus is the energy embargo and financial market fallout $\rightarrow$ `ECONOMY`.
   - If focus is the military strike and casualties $\rightarrow$ `CONFLICT`.

---

## 4. Multi-Annotator Protocol & Agreement Metric
1. **Blind Annotation:** Annotator 1 and Annotator 2 annotate the same set of 1,000 articles without access to each other's decisions.
2. **Metric:** Cohen's Kappa ($\kappa$) is computed according to:
   $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
   Where:
   - $P_o = \frac{1}{N} \sum_{i=1}^k C_{ii}$ (Observed proportional agreement)
   - $P_e = \sum_{i=1}^k \left(\frac{R_i}{N} \cdot \frac{C_i}{N}\right)$ (Hypothetical chance agreement)
3. **Acceptance Threshold:** $\kappa \ge 0.80$ is required for publication-grade gold standard corpus validation.
4. **Adjudication:** Any item where Annotator 1 and Annotator 2 disagree is reviewed by the Principal Investigator for adjudicated ground truth.
