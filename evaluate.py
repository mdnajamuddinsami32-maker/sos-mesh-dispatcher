"""Compare the dispatcher with first-come-first-served on synthetic scenarios.
Ground truth here is simulated; replace it with real volunteer rankings before drawing conclusions."""
import json

from sos_mesh import Box, Dispatcher, Team
from sos_mesh.simulate import generate
from sos_mesh.triage import merge_requests


def top_k_overlap(pred, truth, k):
    k = min(k, len(truth))
    return len(set(pred[:k]) & set(truth[:k])) / k if k else 1.0


def spearman(pred, truth):
    common = [b for b in truth if b in pred]
    n = len(common)
    if n < 2:
        return 1.0
    pr = {b: i for i, b in enumerate([b for b in pred if b in common])}
    tr = {b: i for i, b in enumerate(common)}
    d2 = sum((pr[b] - tr[b]) ** 2 for b in common)
    return 1 - 6 * d2 / (n * (n * n - 1))


def main(n_scenarios=200):
    boxes = [Box(**b) for b in json.load(open("data/boxes.json", encoding="utf-8"))]
    teams = [Team("Alpha", 23.8990, 90.3990), Team("Bravo", 23.9050, 90.4080)]
    disp = Dispatcher(boxes, teams)
    rows = {"dispatcher": [], "first-come-first-served": []}
    for seed in range(n_scenarios):
        sos, truth, water = generate(boxes, n_events=8, seed=seed)
        truth_order = sorted(truth, key=lambda b: -truth[b])
        pred = [r.box.box_id for r in disp.plan(sos, 90, water).ranked]
        fcfs = [k[0] for k, _ in sorted(merge_requests(sos).items(), key=lambda kv: kv[1][0])]
        for name, order in (("dispatcher", pred), ("first-come-first-served", fcfs)):
            rows[name].append((top_k_overlap(order, truth_order, 3),
                               1.0 if truth_order and truth_order[0] in order[:2] else 0.0,
                               spearman(order, truth_order)))
    print("Scenarios: %d (synthetic)" % n_scenarios)
    print("%-26s %-12s %-16s %s" % ("method", "top-3 match", "top-1 in top-2", "rank correlation"))
    for name, vals in rows.items():
        avg = [sum(v[i] for v in vals) / len(vals) for i in range(3)]
        print("%-26s %-12.2f %-16.2f %.2f" % (name, avg[0], avg[1], avg[2]))


if __name__ == "__main__":
    main()
