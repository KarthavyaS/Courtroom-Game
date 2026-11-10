# ⚖️ LOGIC COURTROOM
> *"Where Logic Decides the Verdict"*

A modular, desktop educational courtroom investigation game built in **Python 3.12+** and **Pygame**, powered by **Traditional Artificial Intelligence** (Symbolic Logic, Forward Chaining, Backward Chaining, and Resolution Refutation).

---

## 📖 Overview

In **LOGIC COURTROOM**, the player assumes the role of a Lead Defense & Prosecuting Counsel investigating complex criminal cases. 
Unlike generative AI or LLM-based games, the **AI Magistrate** evaluates every claim, evidence link, and deductive argument using **deterministic symbolic logic**, ensuring transparent, mathematically verifiable verdicts without hallucinations.

### 🏛️ Key Features

1. **Interactive 2D Crime Scene Investigation**:
   - Inspect interactive crime scenes (Vance Manor Study, Kensington Vault, Executive Finance Suite).
   - Click hotspots to uncover autopsy reports, murder weapons, latent fingerprints, digital logs, and phone messages.
   - Unlock logical propositions into your investigative Knowledge Base.

2. **Suspect Interrogations & Statement Cross-Examination**:
   - Review suspect dossiers, motives, occupations, and sworn depositions.
   - Cross-reference alibis with forensic timelines to detect logical contradictions.

3. **Forensic Evidence Review Dashboard**:
   - Filter evidence across 5 legal categories: *Direct, Physical, Digital, Testimonial, Circumstantial*.
   - Understand the crucial legal distinction between **Reliability** (trustworthiness of the source) and **Relevance** (logical connection to the crime elements).

4. **Lawyer's Argument Workshop**:
   - Select the accused suspect under indictment.
   - Assemble grounded premises from collected evidence and forensic findings.
   - Frame deductive target conclusions (e.g. `suspect_guilty_beyond_reasonable_doubt`).
   - Add custom legal pleadings and parse natural-language claims.

5. **AI Judge Courtroom & Deliberation Engine**:
   - Step-by-step reasoning trace displaying Forward Chaining deductions, Backward Chaining goal trees, and Propositional Resolution proofs.
   - Transparent 0–100 scorecards evaluating Logical Validity (30 pts), Evidence Strength (40 pts), Premise Grounding (15 pts), and Safeguard Adherence (15 pts).
   - Dynamic verdict categories: `SUPPORTED`, `NOT PROVEN`, or `CONTRADICTED`.

6. **Custom Case Authoring Studio**:
   - Create, validate, and publish custom cases with suspects, evidence, and deduction rules.
   - Published cases immediately appear in the Case Selection docket.

7. **Hall of Fame Leaderboard**:
   - Persistent ranking of legal advocates and their case scores.

---

## 🏗️ Project Architecture

```
logic_courtroom/
│
├── main.py                    # Game loop & Screen Navigation Orchestrator
├── config.py                  # Colors, dimensions, and font manager
├── requirements.txt           # Python dependencies (pygame>=2.5.0)
├── README.md                  # Complete technical & gameplay documentation
│
├── assets/                    # Media assets structure
│   ├── images/
│   │   ├── backgrounds/
│   │   ├── characters/
│   │   ├── evidence/
│   │   ├── icons/
│   │   └── buttons/
│   ├── fonts/
│   └── sounds/
│
├── screens/                   # Pygame Screen classes (MVC View-Controller)
│   ├── __init__.py
│   ├── main_menu.py           # Vintage courtroom main menu
│   ├── case_selection.py      # Case dossiers browser
│   ├── crime_scene.py         # 2D interactive crime scene
│   ├── suspect_details.py     # Suspect profiles & cross-examination
│   ├── evidence_view.py       # Forensic evidence review dashboard
│   ├── argument_builder.py    # Structured premise & conclusion workshop
│   ├── courtroom.py           # AI Judge deliberation & scorecard
│   ├── create_case.py         # Custom case authoring studio
│   └── leaderboard.py         # Persistent high-score rankings
│
├── components/                # Reusable UI widgets & procedural illustrations
│   ├── __init__.py
│   ├── button.py              # Vintage wood & gold buttons
│   ├── card.py                # Parchment cards with dual borders
│   ├── panel.py               # Scrollable/bordered content containers
│   ├── text_box.py            # Single & multiline text inputs
│   ├── notification.py        # Animated toast alerts
│   └── illustrations.py       # Procedural avatars, judge, and evidence icons
│
├── ai_engine/                 # Traditional Artificial Intelligence Subsystems
│   ├── __init__.py
│   ├── knowledge_base.py      # Facts, propositions, and Horn rule store
│   ├── propositional_logic.py # AST (And, Or, Not, Implies) & CNF converter
│   ├── forward_chaining.py    # Bottom-up data-driven deduction engine
│   ├── backward_chaining.py   # Top-down goal-directed proof search
│   ├── resolution.py          # Propositional refutation resolution
│   ├── argument_parser.py     # Rule-based natural language argument parser
│   ├── evidence_analyzer.py   # Multi-criteria reliability & relevance analyzer
│   ├── rule_engine.py         # Legal safeguards & forensic inference rules
│   └── scoring.py             # 0-100 objective evaluation & verdict classifier
│
├── models/                    # Data models
│   ├── __init__.py
│   ├── case.py                # Case model
│   ├── suspect.py             # Suspect model
│   ├── evidence.py            # Evidence model
│   └── argument.py            # Legal argument model
│
├── services/                  # Business & persistence layer
│   ├── __init__.py
│   ├── case_service.py        # JSON case loader, validator & saver
│   ├── game_state.py          # Active gameplay session singleton
│   └── save_service.py        # Persistent leaderboard storage
│
├── data/                      # Persistent JSON files
│   ├── cases.json             # 3 playable built-in cases
│   ├── rules.json             # Courtroom inference rules
│   └── leaderboard.json       # Record of honor
│
└── tests/                     # Automated unit test suite
    ├── __init__.py
    ├── test_forward_chaining.py
    ├── test_backward_chaining.py
    ├── test_resolution.py
    └── test_scoring.py
```

---

## 🧠 Traditional AI Algorithms Explained

### 1. Knowledge Base (`ai_engine/knowledge_base.py`)
Maintains a state of propositional symbols (e.g. `knife_found_at_scene`, `cctv_shows_suspect_entry`) and formal Horn clauses. Provides `tell()`, `retract()`, and truth-assignment queries.

### 2. Propositional Logic & CNF (`ai_engine/propositional_logic.py`)
Implements an Abstract Syntax Tree (AST) supporting `Literal`, `Not`, `And`, `Or`, and `Implies`. Includes an automated conversion pipeline to **Conjunctive Normal Form (CNF)** via implication elimination, De Morgan's laws, and disjunction distribution.

### 3. Forward Chaining Engine (`ai_engine/forward_chaining.py`)
A data-driven inference algorithm that begins with known forensic facts, checks satisfied rule antecedents, and iteratively derives new conclusions until reaching a fixed point. Tracks a complete chronological reasoning trace.

### 4. Backward Chaining Engine (`ai_engine/backward_chaining.py`)
A goal-directed recursive proof engine that takes a target conclusion (e.g. `suspect_had_contact_with_knife`) and builds an AND/OR goal tree by recursively verifying rule subgoals. Contains cycle detection to prevent infinite recursion.

### 5. Resolution Refutation Engine (`ai_engine/resolution.py`)
Implements classical Robinson propositional resolution. To prove $KB \models \alpha$, the engine negates $\alpha$, extracts CNF clauses, and systematically resolves pairs of clauses with complementary literals $(L, \neg L)$. If the **empty clause ($\square$)** is derived, the query is mathematically entailed.

### 6. Legal Safeguards & Fallacy Detector (`ai_engine/rule_engine.py`)
Enforces critical legal safeguards:
- **Motive Alone $\neq$ Guilt**: Financial greed or inheritance rights alone cannot convict without physical opportunity or means.
- **Contact Alone $\neq$ Homicide**: Fingerprints on a knife prove handling, not murder, unless connected to the fatal stab wound.
- **Presence Alone $\neq$ Guilt**: Being in the mansion establishes opportunity, not criminal action.
- **Verified Alibi Contradiction**: If a suspect has an independently verified alibi, asserting guilt triggers a fatal contradiction penalty.

---

## 🎮 Playable Built-In Cases

1. **CASE 001: The Midnight Murder (HARD)**
   - *Scenario*: Arthur Vance was stabbed in his locked study at midnight.
   - *Suspects*: Victor Vance (Heir), Clara Sterling (Partner), Arthur Finch (Butler), Dr. Julian Hayes (Doctor).
   - *Evidence*: Autopsy report, bloody chef knife, brandy goblet, broken balcony window, encrypted phone, CCTV hard drive, bloodstained rug, muddy boots.
   - *Solution*: Victor Vance entered at 11:50 PM (CCTV), handled the knife (fingerprints), and falsified a cinema alibi.

2. **CASE 002: The Missing Necklace (MEDIUM)**
   - *Scenario*: A diamond necklace vanished from Lady Kensington's private safe.
   - *Suspects*: Marcus Sterling (Jeweler), Duchess Vivienne, Higgins (Butler).
   - *Evidence*: Unforced safe lock, duplicate brass key, velvet appraisal box, guest registry, silk glove thread, ballroom recording.

3. **CASE 003: The Corporate Fraud (EASY)**
   - *Scenario*: £2.5M siphoned through ghost invoices to a Cayman offshore account.
   - *Suspects*: CFO Richard Sterling, Elena Rostova (Accountant), Thomas Vance (IT Admin).
   - *Evidence*: Offshore wire ledger, hardware 2FA token, deleted email archive, forged invoice, encrypted USB drive.

---

## ⚙️ Installation & Running

### Requirements
- Python 3.12+
- Pygame $\ge$ 2.5.0

### Setup
```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Launch LOGIC COURTROOM
python main.py
```

### Running Unit Tests
```bash
python -m unittest discover -s tests -v
```

---

## 🏛️ Controls & Navigation

- **Mouse Left Click**: Select cards, click interactive crime scene objects, toggle evidence premises, and press buttons.
- **Keyboard**: Type in single/multiline text boxes (supports Backspace, Arrow keys, Enter, Ctrl+V paste).
- **Navigation Bar**: Move smoothly between Crime Scene, Suspects, Evidence, and Argument Builder during active investigations without losing progress.
