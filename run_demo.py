"""Print a dispatch plan for one synthetic flood scenario: python run_demo.py [seed]"""
import json
import sys

from sos_mesh import Box, Dispatcher, Team
from sos_mesh.simulate import generate

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 3
boxes = [Box(**b) for b in json.load(open("data/boxes.json", encoding="utf-8"))]
teams = [Team("Alpha", 23.8990, 90.3990), Team("Bravo", 23.9050, 90.4080)]
sos, truth, water = generate(boxes, n_events=8, seed=seed)
plan = Dispatcher(boxes, teams).plan(sos, now_minute=90, water_levels=water)

print("Ranked requests (urgency 0-5):")
for i, r in enumerate(plan.ranked, 1):
    print("%2d. Box %-2d %-16s %-8s %.2f  team %s ETA %s min" % (
        i, r.box.box_id, r.box.name, r.req_type, r.urgency, r.team, r.eta_min))
    print("      why: " + "; ".join(r.reasons))
print("\nDispatch messages:")
for m in plan.messages:
    print(" - " + m["en"])
    print("   " + m["bn"])
