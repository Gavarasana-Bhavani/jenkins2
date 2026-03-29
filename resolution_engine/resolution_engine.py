"""
resolution_engine.py
Rule-augmented resolution recommendation engine.
Maps predicted Jenkins failure categories to concrete remediation steps.
"""

RESOLUTIONS = {
    "compilation_failure": {
        "title": "Compilation Failure",
        "icon": "🔴",
        "severity": "High",
        "description": "The source code failed to compile. This is typically caused by syntax errors, missing dependencies, incorrect Java version, or unresolved symbols in the codebase.",
        "steps": [
            "Locate the exact file and line number reported in the Jenkins console output.",
            "Fix syntax errors such as missing semicolons, unmatched braces, or incorrect method signatures.",
            "Verify all imported packages and dependencies are declared in pom.xml or build.gradle.",
            "Ensure the JDK version configured in Jenkins matches the project's source/target compatibility.",
            "Run 'mvn clean compile' locally to reproduce and resolve the error before re-pushing.",
            "Check for merge conflicts in recently merged branches that may have broken the code.",
        ],
        "commands": [
            "mvn clean compile -X",
            "mvn dependency:resolve",
            "javac -version",
        ],
    },
    "test_failure": {
        "title": "Test Failure",
        "icon": "🟠",
        "severity": "High",
        "description": "One or more JUnit test cases failed during the test phase. This may indicate a code logic bug, broken assertions, missing test data, or environment-specific issues.",
        "steps": [
            "Identify the failing test class and method name from the Jenkins console output.",
            "Run the failing test locally using: mvn test -Dtest=ClassName#methodName",
            "Analyse the AssertionError — compare the expected vs actual values carefully.",
            "Check for environment dependencies such as database connections, mock configurations, or port availability.",
            "Look for NullPointerExceptions — verify test setup and teardown methods (@Before / @After).",
            "If the test is intermittently failing (flaky), add retry logic or stabilise the test data.",
        ],
        "commands": [
            "mvn test -Dtest=FailingTestClass",
            "mvn surefire-report:report",
            "mvn test -pl module-name",
        ],
    },
    "code_quality_gate": {
        "title": "Code Quality Gate Failure",
        "icon": "🟡",
        "severity": "Medium",
        "description": "The SonarQube Quality Gate conditions were not met. This includes bugs, vulnerabilities, code smells, or security hotspots exceeding the defined thresholds.",
        "steps": [
            "Open the SonarQube dashboard and navigate to the project to view failing conditions.",
            "Resolve all Critical and Blocker bugs — these directly impact reliability.",
            "Fix security vulnerabilities and review unresolved security hotspots.",
            "Reduce code smells to lower technical debt below the Quality Gate threshold.",
            "Ensure new code meets the minimum line and branch coverage requirements.",
            "Re-trigger the analysis after fixes using: mvn sonar:sonar",
        ],
        "commands": [
            "mvn sonar:sonar -Dsonar.host.url=http://localhost:9000",
            "mvn sonar:sonar -Dsonar.login=<your-token>",
        ],
    },
    "jacoco_coverage_failure": {
        "title": "JaCoCo Coverage Failure",
        "icon": "🟡",
        "severity": "Medium",
        "description": "The JaCoCo code coverage report shows that test coverage is below the configured minimum threshold. This indicates insufficient unit test coverage for the codebase.",
        "steps": [
            "Check the JaCoCo report in the Jenkins build output for current vs required coverage values.",
            "Open the HTML coverage report at: target/site/jacoco/index.html",
            "Identify classes, methods, and branches with zero or low coverage.",
            "Write unit tests specifically targeting the uncovered code paths.",
            "Use @Test annotations correctly and ensure tests actually execute the target methods.",
            "Run 'mvn test jacoco:report' locally to verify coverage improvement before pushing.",
        ],
        "commands": [
            "mvn test jacoco:report",
            "mvn verify",
            "open target/site/jacoco/index.html",
        ],
    },
    "sonarqube_error": {
        "title": "SonarQube Analysis Error",
        "icon": "🔵",
        "severity": "Medium",
        "description": "The SonarQube scanner failed to connect to the server or upload analysis results. This is typically a connectivity, authentication, or configuration issue.",
        "steps": [
            "Verify the SonarQube server is running: curl http://sonarqube-host:9000/api/system/status",
            "Check that the SonarQube authentication token in Jenkins credentials is valid and not expired.",
            "Confirm that the Jenkins build agent has network access to the SonarQube server.",
            "Check the SonarQube server logs for HTTP 500 or memory-related errors.",
            "Verify sonar.projectKey and sonar.host.url values in pom.xml or sonar-project.properties.",
            "Restart the SonarQube service if the server is unresponsive.",
        ],
        "commands": [
            "curl -u token: http://sonarqube:9000/api/system/status",
            "mvn sonar:sonar -Dsonar.verbose=true",
        ],
    },
    "docker_build_failure": {
        "title": "Docker Build Failure",
        "icon": "🐳",
        "severity": "High",
        "description": "The Docker image build step failed during the pipeline. This may be caused by a missing Dockerfile, failed RUN commands, unavailable base images, or Docker daemon issues.",
        "steps": [
            "Check that the Dockerfile exists in the expected directory (project root by default).",
            "Ensure the build artifact (JAR/WAR) exists in the target/ directory before the Docker stage.",
            "Verify the base image name and tag are correct and accessible: docker pull <base-image>",
            "Check available disk space on the Jenkins agent: df -h",
            "Run 'docker build .' manually on the build agent to replicate and debug the error.",
            "Confirm the Docker daemon is running on the build agent: systemctl status docker",
        ],
        "commands": [
            "docker build -t app:latest .",
            "docker system prune -f",
            "systemctl status docker",
        ],
    },
    "deployment_error": {
        "title": "Deployment Error",
        "icon": "🚀",
        "severity": "Critical",
        "description": "The deployment to the target environment failed. This may involve SSH connectivity issues, missing AWS credentials, incorrect Tomcat configuration, or insufficient server permissions.",
        "steps": [
            "Verify SSH connectivity to the target server using the deployment key pair.",
            "Check that AWS credentials or the IAM role attached to the Jenkins instance has deployment permissions.",
            "Review EC2 Security Group inbound rules — ensure SSH (port 22) and application ports are open.",
            "Validate the deployment script paths and environment variable configurations.",
            "Check Tomcat Manager credentials in Maven settings.xml match the tomcat-users.xml configuration.",
            "Review the target server's available disk space and memory before re-deploying.",
        ],
        "commands": [
            "ssh -i key.pem ec2-user@<server-ip>",
            "aws sts get-caller-identity",
            "curl http://server:8080/manager/text/list -u admin:password",
        ],
    },
}


def get_resolution(failure_type: str) -> dict:
    return RESOLUTIONS.get(failure_type, {
        "title":       "Unknown Failure",
        "icon":        "❓",
        "severity":    "Unknown",
        "description": "The failure type could not be identified. Review the full build log manually.",
        "steps":       ["Examine the full Jenkins console output for error keywords.", "Check the build history for similar failures."],
        "commands":    [],
    })


def get_all_failure_types():
    return list(RESOLUTIONS.keys())
