import os
import json
import subprocess


def scream(line):
    if "autofix" in line:
        return "Received `autofix`. Using `Autofix` recommended"


def analyze_one(issue_file):
    issues = []

    def raise_issue(issue_code, title, line, column):
        issues.append({
            "issue_text": title,
            "issue_code": issue_code,
            "location": {
                "position": {
                    "begin": {
                        "line": line,
                        "column": column,
                    },
                    "end": {
                        "line": line,
                        "column": column,
                    },
                },
                "path": issue_file[6:],  # /code/filename
            },
        })

    with open(issue_file) as fd:
        for lno, line in enumerate(fd.readlines()):
            if message := scream(line):
                raise_issue("SCM-I0001", message, lno, 0)

    return issues


def get_files(base_dir):
    """Return a generator with filepaths in base_dir."""
    for subdir, _, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(subdir, filename)
            yield filepath


def publish_results(filename):
    # publish result via marvin:
    subprocess.run(["/toolbox/marvin", "--publish-report", filename])


def analyze():
    code_path = os.getenv("CODE_PATH", "/code")
    base_dir = os.path.join(code_path, ".deepsource", "analyzer", "issues")

    issues = []

    for f in get_files(base_dir):
        if not f.endswith(".toml"):
            continue

        issues.extend(analyze_one(f))

    results = {
        "issues": issues,
        "metrics": [],
    }

    results_path = f"{os.getenv('TOOLBOX_PATH')}/analysis_results.json"

    with open(results_path, "w") as f:
        f.write(json.dumps(results))

    print(results)
    # publish_results(results_path)


analyze()
