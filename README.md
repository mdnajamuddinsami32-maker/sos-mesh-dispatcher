# SOS Mesh: AI dispatcher (proof of concept)

Concept project by **Signal Squad** (Metropolitan University) for the AI Builders Hackathon 2026,
track HumanitarianTech & Disaster Resilience.

**SOS Mesh** is a proposed offline emergency network: low-cost boxes with four buttons (Water, Medical,
Trapped, Safe) pass messages hop by hop to a gateway. This repository contains only the **software
side of the proposal**: a simulator and the dispatcher logic that turns raw SOS messages into one
ranked rescue plan. There is no hardware code here and no deployed system.

> Status: proof of concept on **synthetic data**. Scoring weights are assumptions and must be tuned
> with real coordinator feedback before any real use.

## What it does

1. **Triage:** merges duplicate presses, drops requests cancelled by a later SAFE, and scores urgency
   from 0 to 5 using request type, waiting time, repeated presses, vulnerable residents, households
   served and water level (`sos_mesh/triage.py`).
2. **Optional LLM adjustment:** if you pass a function, an LLM may nudge each score by at most +/-0.5.
   Invalid or missing output is ignored, so the rule-based score is the offline fallback.
3. **Grouping:** DBSCAN-style grouping of nearby boxes (`sos_mesh/clustering.py`).
4. **Routing:** urgency-first greedy assignment of requests to rescue teams (`sos_mesh/routing.py`).
   This is a heuristic, not an optimal route.
5. **Messages:** Bangla and English dispatch messages from templates (`sos_mesh/messages.py`).

## Run it

```
python run_demo.py 3        # print a plan for one synthetic scenario
python evaluate.py          # compare against first-come-first-served on 200 simulated scenarios
python -m unittest          # run the tests
```

## Evaluation (read before quoting any numbers)

`evaluate.py` compares the dispatcher with a first-come-first-served baseline. The "truth" is
simulated: it uses hidden factors (people at risk, true water depth) that the dispatcher only sees
partly. It stands in for volunteer judgement. Replace it with rankings from real people, then report
your own results here, including cases where the dispatcher is wrong.

## Using an LLM (optional)

`Dispatcher(boxes, teams, llm=my_function)` accepts any function that takes a prompt string and
returns JSON like `{"adjust": 0.2, "why": "..."}`. Wire it to the provider you choose. Keep API keys
in environment variables and never commit them (`.env` is in `.gitignore`).

## Limitations

- Synthetic data only; no real SOS dataset was used.
- Fixed weights and a greedy router; no learned model.
- The LLM hook is an interface; this repo does not ship a provider integration.
- Distances are straight lines, not real water routes.

## Proposed next steps

Collect real coordinator rankings, tune the weights against them, add a dashboard, and test the
offline fallback with a small open model.
