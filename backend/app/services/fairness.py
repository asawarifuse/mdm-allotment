"""
Fairness experiment: run the same allotment three ways on the same data.

Mode A (cgpa):    rank students by CGPA desc
Mode B (lottery): random shuffle with fixed seed
Mode C (hybrid):  average of CGPA rank and lottery rank (rank sum)

Each mode respects the same preference list, quota grid, and fallback rule.
Read-only — does NOT touch live allotments.
"""

import random
from scipy.stats import chi2_contingency

from sqlalchemy.orm import Session

from app.models.course import CourseSeat
from app.models.preference import Preference
from app.models.student import Student


def _load(db: Session):
    prefs_all = (
        db.query(Preference.student_uid, Preference.course_id, Preference.rank)
        .order_by(Preference.student_uid, Preference.rank)
        .all()
    )
    prefs_by_uid: dict[str, list[int]] = {}
    for uid, cid, _ in prefs_all:
        prefs_by_uid.setdefault(uid, []).append(cid)

    students = db.query(Student).all()
    seats = db.query(CourseSeat).all()
    quota = {(s.course_id, s.branch): s.seats for s in seats}
    return students, prefs_by_uid, quota


def _simulate(order, prefs_by_uid, quota_copy):
    """Return dict: choice -> count."""
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, "fallback": 0, "none": 0}
    filled: dict[tuple[int, str], int] = {}
    for uid, cgpa, branch in order:
        prefs = prefs_by_uid.get(uid, [])
        placed = None
        for rank, cid in enumerate(prefs, start=1):
            key = (cid, branch)
            cap = quota_copy.get(key, 0)
            if filled.get(key, 0) < cap:
                filled[key] = filled.get(key, 0) + 1
                placed = rank
                break
        if placed is None:
            for (cid, b), cap in quota_copy.items():
                if b == branch and filled.get((cid, b), 0) < cap:
                    filled[(cid, b)] = filled.get((cid, b), 0) + 1
                    placed = "fallback"
                    break
        if placed is None:
            counts["none"] += 1
        else:
            counts[placed] += 1
    return counts


def _pct(counts, n, key):
    return round(100.0 * counts.get(key, 0) / n, 2) if n else 0.0


def run_fairness_experiment(db: Session, seed: int = 42) -> dict:
    students, prefs_by_uid, quota = _load(db)
    pool = [(s.uid, s.cgpa, s.parent_branch) for s in students if s.uid in prefs_by_uid]
    n = len(pool)

    # Mode A: CGPA
    order_a = sorted(pool, key=lambda r: -r[1])
    counts_a = _simulate(order_a, prefs_by_uid, dict(quota))

    # Mode B: Lottery
    rng = random.Random(seed)
    shuffled = pool[:]
    rng.shuffle(shuffled)
    counts_b = _simulate(shuffled, prefs_by_uid, dict(quota))

    # Mode C: Hybrid (rank-sum of CGPA rank + lottery rank)
    cgpa_rank = {uid: i for i, (uid, _, _) in enumerate(sorted(pool, key=lambda r: -r[1]))}
    lotto_rank = {uid: i for i, (uid, _, _) in enumerate(shuffled)}
    order_c = sorted(pool, key=lambda r: cgpa_rank[r[0]] + lotto_rank[r[0]])
    counts_c = _simulate(order_c, prefs_by_uid, dict(quota))

    def summarise(counts):
        return {
            "first_choice_pct": _pct(counts, n, 1),
            "second_choice_pct": _pct(counts, n, 2),
            "fifth_choice_pct": _pct(counts, n, 5),
            "fallback_pct": _pct(counts, n, "fallback"),
            "unallotted_pct": _pct(counts, n, "none"),
            "raw": counts,
        }

    # Chi-square on choice distribution across 3 modes
    table = []
    for counts in (counts_a, counts_b, counts_c):
        row = [counts.get(k, 0) for k in (1, 2, 3, 4, 5, 6)] + [counts.get("fallback", 0)]
        table.append(row)

    try:
        chi2, p, _, _ = chi2_contingency(table)
        cramers_v = (chi2 / (n * 6)) ** 0.5 if n else 0.0
    except Exception:
        p, cramers_v = 1.0, 0.0

    interp = ("Statistically significant difference between allocation strategies"
              if p < 0.05 else
              "No statistically significant difference observed")

    return {
        "cgpa": summarise(counts_a),
        "lottery": summarise(counts_b),
        "hybrid": summarise(counts_c),
        "p_value": round(float(p), 6),
        "cramers_v": round(float(cramers_v), 4),
        "interpretation": interp,
    }