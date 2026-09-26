from app.services.ranking import top_n


def make_result(uid, score, expertise=0.5):
    return {"universityId": uid, "finalScore": score, "factorScores": {"expertise": expertise}}


def test_top_5_from_ten_candidates():
    results = [make_result(f"UNI-{i:03d}", 100 - i) for i in range(10)]
    results.sort(key=lambda r: -r["finalScore"])
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    top5 = top_n(results, 5)

    assert len(top5) == 5
    assert [r["universityId"] for r in top5] == ["UNI-000", "UNI-001", "UNI-002", "UNI-003", "UNI-004"]
    assert top5[0]["rank"] == 1


def test_deterministic_tie_break_by_expertise_then_id():
    """Same test pattern the matching_engine.run_matching_for_problem sort uses:
    finalScore desc, then expertise desc, then universityId asc."""
    results = [
        make_result("UNI-B", 80.0, expertise=0.6),
        make_result("UNI-A", 80.0, expertise=0.8),
        make_result("UNI-C", 80.0, expertise=0.8),
    ]
    results.sort(key=lambda r: (-r["finalScore"], -r["factorScores"]["expertise"], r["universityId"]))

    assert [r["universityId"] for r in results] == ["UNI-A", "UNI-C", "UNI-B"]
