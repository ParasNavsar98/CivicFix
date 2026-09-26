from app.services.matching_engine import score_university
from app.models.matching_config import DEFAULT_WEIGHTS


def test_manually_verified_weighted_score(sample_problem, sample_university):
    """
    Hand-computed expectation for sample_problem + sample_university:
      expertise      = 0.5   (1/2 required terms matched)
      faculty        = 0.5   (1/2 required terms covered by available faculty)
      infrastructure = 0.0   (required resources not present in infra/tech list)
      pastProjects   = 0.5   (1 relevant project / divisor 2)
      geography      = 1.0   (same district: Ranchi, Jharkhand)
      capacity       = 0.4   (AVAILABLE, 6/10 active -> 4/10 free)
      industry       = 1.0   ("Environmental Technology Companies" matches "Environment")

    final = (0.5*.35 + 0.5*.20 + 0.0*.15 + 0.5*.10 + 1.0*.10 + 0.4*.05 + 1.0*.05) * 100
          = (0.175 + 0.10 + 0 + 0.05 + 0.10 + 0.02 + 0.05) * 100
          = 49.5
    """
    result = score_university(sample_problem, sample_university, DEFAULT_WEIGHTS)

    assert result["factorScores"]["expertise"] == 0.5
    assert result["factorScores"]["faculty"] == 0.5
    assert result["factorScores"]["infrastructure"] == 0.0
    assert result["factorScores"]["pastProjects"] == 0.5
    assert result["factorScores"]["geography"] == 1.0
    assert result["factorScores"]["capacity"] == 0.4
    assert result["factorScores"]["industry"] == 1.0
    assert result["finalScore"] == 49.5


def test_score_includes_explanation_and_university_id(sample_problem, sample_university):
    result = score_university(sample_problem, sample_university, DEFAULT_WEIGHTS)
    assert result["universityId"] == "UNI-TEST-001"
    assert "49.5" in result["explanation"]


def test_run_matching_for_problem_persists_and_ranks(db, sample_problem, sample_university):
    from app.services.matching_engine import run_matching_for_problem

    other = dict(sample_university)
    other["universityId"] = "UNI-TEST-002"
    other["expertise"] = []  # will score much lower on expertise

    db.universities.insert_many([sample_university, other])

    results = run_matching_for_problem(db, sample_problem)

    assert len(results) == 2
    assert results[0]["rank"] == 1
    assert results[0]["universityId"] == "UNI-TEST-001"
    assert results[0]["finalScore"] >= results[1]["finalScore"]

    stored = db.matching_results.find_one({"problemId": sample_problem.problem_id})
    assert stored is not None
    assert len(stored["results"]) == 2
