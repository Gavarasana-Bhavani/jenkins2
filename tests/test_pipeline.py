"""
test_pipeline.py
Unit tests for the Automated Jenkins Failure Detection system.
"""
import os, sys, pickle, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resolution_engine.resolution_engine import get_resolution, get_all_failure_types

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../model/best_model.pkl")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "../model/model_results.json")


def test_resolution_engine():
    types = get_all_failure_types()
    assert len(types) == 7, f"Expected 7 failure types, got {len(types)}"
    for t in types:
        res = get_resolution(t)
        assert "title" in res, f"Missing title for {t}"
        assert "steps" in res, f"Missing steps for {t}"
        assert len(res["steps"]) >= 5, f"Too few steps for {t}"
        assert "commands" in res, f"Missing commands for {t}"
    print("✅ Resolution engine — PASSED")


def test_model_predictions():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    test_cases = [
        ("ERROR: BUILD FAILURE\n[ERROR] COMPILATION ERROR\n[ERROR] /src/Main.java:[12,5] ';' expected", "compilation_failure"),
        ("Tests run: 15, Failures: 3\nFAILED: testUserLogin\nAssertionError: expected:<200> but was:<401>", "test_failure"),
        ("ERROR: QUALITY GATE FAILURE\nCondition: Coverage on New Code < 80%\nProject failed the quality gate", "code_quality_gate"),
        ("FAILED: JaCoCo Coverage Check\nLine coverage: 62% (minimum required: 80%)", "jacoco_coverage_failure"),
        ("ERROR: SonarQube server connection refused\nCould not connect to SonarQube at http://sonarqube:9000", "sonarqube_error"),
        ("ERROR: Docker build failed\nStep 5/10 : RUN mvn clean install\nnon-zero code: 1", "docker_build_failure"),
        ("ERROR: Deployment to EC2 failed\nSSH connection refused: ec2-54-xx-xx.compute.amazonaws.com", "deployment_error"),
    ]

    passed = 0
    for log, expected in test_cases:
        pred = model.predict([log])[0]
        status = "✅" if pred == expected else "❌"
        print(f"  {status} {expected}: predicted → {pred}")
        if pred == expected:
            passed += 1

    assert passed == len(test_cases), f"Only {passed}/{len(test_cases)} predictions correct"
    print(f"✅ Model predictions — PASSED ({passed}/{len(test_cases)})")


def test_model_metrics():
    with open(RESULTS_PATH) as f:
        data = json.load(f)
    rf = data["results"]["Random Forest"]
    assert rf["accuracy"] >= 80.0, f"Accuracy too low: {rf['accuracy']}"
    assert rf["f1_score"] >= 0.80, f"F1 too low: {rf['f1_score']}"
    print(f"✅ Model metrics — PASSED (Accuracy: {rf['accuracy']}%, F1: {rf['f1_score']})")


if __name__ == "__main__":
    print("\n── Running Test Suite ──\n")
    test_resolution_engine()
    test_model_predictions()
    test_model_metrics()
    print("\n🎉 All tests passed!\n")
