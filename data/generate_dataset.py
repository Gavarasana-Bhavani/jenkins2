"""
generate_dataset.py
Generates a labeled Jenkins build failure dataset for ML training.
Covers 7 real-world Jenkins CI/CD failure categories.
"""
import pandas as pd
import random
import os

random.seed(42)

FAILURE_TYPES = [
    "compilation_failure",
    "test_failure",
    "code_quality_gate",
    "jacoco_coverage_failure",
    "sonarqube_error",
    "docker_build_failure",
    "deployment_error"
]

SAMPLE_LOGS = {
    "compilation_failure": [
        "ERROR: BUILD FAILURE\n[ERROR] COMPILATION ERROR\n[ERROR] /src/main/java/com/app/Main.java:[12,5] ';' expected\n[ERROR] cannot find symbol: method getValue()\nBuild step 'Invoke top-level Maven targets' marked build as failure",
        "ERROR: BUILD FAILURE\n[ERROR] COMPILATION ERROR\n[ERROR] /src/main/java/com/app/Service.java:[34,10] incompatible types: String cannot be converted to int\n[INFO] BUILD FAILURE\n[ERROR] Failed to execute goal compile",
        "BUILD FAILED\n[ERROR] symbol not found\n[ERROR] package com.example does not exist\n[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.8.1:compile\nExit code: 1",
        "COMPILATION ERROR\n[ERROR] /src/UserController.java:[55] class, interface, or enum expected\n[ERROR] 3 errors\n[INFO] BUILD FAILURE\nFinished: FAILURE",
        "ERROR: javac returned exit code 1\n[ERROR] Source option 8 is no longer supported. Use 11 or later.\n[ERROR] Target option 8 is no longer supported.\nBuild step marked build as failure",
    ],
    "test_failure": [
        "Tests run: 15, Failures: 3, Errors: 0, Skipped: 0\nFAILED: testUserLogin(com.app.UserTest)\njava.lang.AssertionError: expected:<200> but was:<401>\nBUILD FAILURE",
        "Tests run: 20, Failures: 1, Errors: 2\nFAILED: testCalculateTotal(PaymentTest)\njava.lang.AssertionError: expected:<100> but was:<90>\n[INFO] BUILD FAILURE",
        "BUILD FAILURE\nThere are test failures.\nFailed tests:\n  testPayment(PaymentTest): expected true but was false\n  testOrder(OrderTest): NullPointerException\nFinished: FAILURE",
        "FAILED testSaveUser -- AssertionError: Database record not found\nTests run: 8, Failures: 2\n[ERROR] There are test failures.\n[INFO] BUILD FAILURE",
        "junit.framework.AssertionFailedError: Login should return token\nExpected: not null  but was: null\nTests run: 12, Failures: 1, Errors: 0\nFinished: FAILURE",
    ],
    "code_quality_gate": [
        "ERROR: QUALITY GATE FAILURE\nCondition: Coverage on New Code < 80%\nCondition: Bugs > 0\nProject failed the quality gate.\nBUILD FAILURE",
        "QUALITY GATE STATUS: FAILED\nBugs: 5 (ERROR threshold: 0)\nVulnerabilities: 2 (ERROR threshold: 0)\nCode Smells: 23\nFinished: FAILURE",
        "SonarQube Quality Gate FAILED\nNew Bugs: 3\nNew Vulnerabilities: 1\nNew Code Smells: 12\nTechnical Debt: 3h 20min\nBuild step marked build as failure",
        "QUALITY GATE FAILED\nSecurity Hotspots: 4 unreviewed\nDuplications on New Code: 15.5%\nMaintainability Rating: D\nBUILD FAILURE",
        "ERROR: Quality gate check failed\nCondition 'Reliability Rating' failed: actual value D is worse than E\nCondition 'Security Rating' failed\nFinished: FAILURE",
    ],
    "jacoco_coverage_failure": [
        "FAILED: JaCoCo Coverage Check\nLine coverage: 62% (minimum required: 80%)\nBranch coverage: 55% (minimum required: 70%)\nBUILD FAILURE\nFinished: FAILURE",
        "JaCoCo: Coverage below minimum threshold\nInstruction coverage: 58.3% (required: 75%)\nMethod coverage: 67.1% (required: 80%)\n[ERROR] BUILD FAILURE",
        "ERROR: JaCoCo minimum coverage not met\nCurrent line coverage: 71.2%, required: 85%\nCurrent branch coverage: 60.0%, required: 75%\nBUILD FAILURE",
        "JaCoCo Coverage Gate Failed\nClass coverage: 55% < 70% minimum\nComplexity coverage: 48% < 65% minimum\nFinished: FAILURE",
        "maven-jacoco-plugin: Coverage check failed\nOverall Instructions: 61% (threshold: 80%)\nOverall Lines: 63% (threshold: 80%)\n[INFO] BUILD FAILURE",
    ],
    "sonarqube_error": [
        "ERROR: SonarQube server connection refused\nCould not connect to SonarQube at http://sonarqube:9000\nConnection timeout after 30000ms\nBUILD FAILURE",
        "SonarScanner failed to execute\nERROR: Error during SonarQube Scanner execution\nFailed to upload report: HTTP 500 Internal Server Error\nFinished: FAILURE",
        "WARN: SonarQube analysis failed\nERROR: Not authorized. Provide a user token or verify credentials.\nHTTP 401 Unauthorized\nBUILD FAILURE",
        "ERROR: SonarQube analysis failed\nProject key not found: com.example:my-app\nPlease check sonar.projectKey configuration\nFinished: FAILURE",
        "SonarQube Scanner error\nERROR: java.io.IOException: Failed to parse response from SonarQube\nHTTP 503 Service Unavailable\nBUILD FAILURE",
    ],
    "docker_build_failure": [
        "ERROR: Docker build failed\nStep 5/10 : RUN mvn clean install\nThe command '/bin/sh -c mvn clean install' returned a non-zero code: 1\nFinished: FAILURE",
        "ERROR [build 6/9] COPY target/*.jar app.jar\nfailed to solve: failed to read dockerfile\nopen Dockerfile: no such file or directory\nBUILD FAILURE",
        "error building image: error building at STEP\nRUN npm install: exit status 1\nnpm ERR! code ENOENT\nnpm ERR! syscall open\nFinished: FAILURE",
        "Docker build error\nCannot connect to the Docker daemon at unix:///var/run/docker.sock\nIs the docker daemon running?\nBUILD FAILURE",
        "Step 3/8 : FROM openjdk:17-jdk-slim\nERROR: failed to pull image openjdk:17-jdk-slim\nnetwork timeout\nFinished: FAILURE",
    ],
    "deployment_error": [
        "ERROR: Deployment to EC2 failed\nSSH connection refused: ec2-54-xx-xx-xx.compute.amazonaws.com port 22\nCheck security group inbound rules.\nFinished: FAILURE",
        "DEPLOY FAILED\naws: error: Unable to locate credentials\nConfigure AWS CLI credentials or attach IAM role to instance.\nBUILD FAILURE",
        "Tomcat deployment failed\nHTTP 403 Forbidden from Tomcat Manager\nCheck credentials in Maven settings.xml\nFinished: FAILURE",
        "ERROR: Remote deployment script failed\nscp: /opt/app/deploy.sh: Permission denied\nExit code 1\nBUILD FAILURE",
        "Kubernetes deployment failed\nError from server: deployments.apps not found\nkubectl: error: context deadline exceeded\nFinished: FAILURE",
    ],
}

def generate_row(failure_type):
    log = random.choice(SAMPLE_LOGS[failure_type])
    return {
        "log_snippet":        log,
        "failure_type":       failure_type,
        "build_duration_sec": random.randint(15, 720),
        "failed_stage":       random.choice(["Checkout","Build","Test","Analysis","Package","Deploy"]),
        "retry_count":        random.randint(0, 3),
        "agent":              random.choice(["agent-1","agent-2","agent-3","master"]),
    }

rows = []
for ft in FAILURE_TYPES:
    for _ in range(50):
        rows.append(generate_row(ft))

random.shuffle(rows)
df = pd.DataFrame(rows)
out = os.path.join(os.path.dirname(__file__), "build_failures.csv")
df.to_csv(out, index=False)
print(f"[INFO] Dataset generated: {out}  ({len(df)} rows, {len(FAILURE_TYPES)} categories)")
