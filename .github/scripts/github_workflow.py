"""Maintain native issue readiness/owners and check PR closing dependencies.

Uses the runner's gh CLI. Credentials stay in GH_TOKEN; no secret is printed or
passed as a command argument. This script does not merge PRs or close issues.
"""

import json
import os
import subprocess
import sys
from urllib.parse import quote


OWNERS = {
    "owner:samet": "mathissdupont",
    "owner:halil": "halilabaci",
    "owner:fatmanur": "fatmanurrbulut",
}
READINESS = {"workflow:ready", "workflow:blocked"}


def api(endpoint, *, method="GET", payload=None):
    arguments = ["gh", "api", "--method", method, endpoint]
    if payload is not None:
        arguments.extend(["--input", "-"])
    result = subprocess.run(
        arguments, input=json.dumps(payload) if payload is not None else None,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode:
        raise RuntimeError(f"GitHub API failed for {method} {endpoint}: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def paginated(endpoint):
    separator = "&" if "?" in endpoint else "?"
    result, page = [], 1
    while True:
        items = api(f"{endpoint}{separator}per_page=100&page={page}")
        if not isinstance(items, list):
            raise ValueError(f"Expected a list from {endpoint}")
        result.extend(items)
        if len(items) < 100:
            return result
        page += 1


def readiness(issue, blockers):
    """Ready means hard prerequisites are closed, not that work has started."""
    if issue["state"] == "closed":
        return set()
    return {"workflow:blocked" if any(item["state"] != "closed" for item in blockers) else "workflow:ready"}


def unresolved_dependencies(closing_numbers, dependency_map):
    """A single PR may complete a prerequisite and its dependent together."""
    closing = set(closing_numbers)
    return [
        (number, dependency["number"])
        for number in sorted(closing)
        for dependency in dependency_map.get(number, [])
        if dependency["state"] != "closed" and dependency["number"] not in closing
    ]


def can_assign(repository, username):
    result = subprocess.run(
        ["gh", "api", f"repos/{repository}/assignees/{username}", "--silent"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        return True
    if "404" in result.stderr:
        return False
    raise RuntimeError(f"Could not check assignee eligibility for {username}: {result.stderr.strip()}")


def sync(repository):
    eligibility = {}
    for issue in paginated(f"repos/{repository}/issues?state=all"):
        if "pull_request" in issue:
            continue
        labels = {label["name"] for label in issue["labels"]}
        if "type:tracking" in labels:
            continue
        number = issue["number"]
        endpoint = f"repos/{repository}/issues/{number}"
        blockers = paginated(f"{endpoint}/dependencies/blocked_by") if issue["state"] == "open" else []
        desired = readiness(issue, blockers)
        for label in sorted((labels & READINESS) - desired):
            api(f"{endpoint}/labels/{quote(label, safe='')}", method="DELETE")
        additions = desired - labels
        if additions:
            api(f"{endpoint}/labels", method="POST", payload={"labels": sorted(additions)})
        owner_labels = labels & OWNERS.keys()
        if issue["state"] == "open" and len(owner_labels) == 1:
            username = OWNERS[next(iter(owner_labels))]
            if username not in {user["login"] for user in issue["assignees"]}:
                if username not in eligibility:
                    eligibility[username] = can_assign(repository, username)
                if eligibility[username]:
                    api(f"{endpoint}/assignees", method="POST", payload={"assignees": [username]})
                else:
                    print(f"#{number}: @{username} is not assignable yet; owner label retained.")
        elif len(owner_labels) > 1:
            raise ValueError(f"#{number}: choose exactly one owner label.")
        print(f"#{number}: {', '.join(sorted(desired)) or 'closed'}")


def check_pr(repository, number):
    owner, name = repository.split("/", 1)
    query = """query($owner:String!,$name:String!,$number:Int!) {
      repository(owner:$owner,name:$name) {
        pullRequest(number:$number) {
          isDraft
          closingIssuesReferences(first:100) {
            nodes { number repository { nameWithOwner } }
            pageInfo { hasNextPage }
          }
        }
      }
    }"""
    response = api("graphql", method="POST", payload={
        "query": query, "variables": {"owner": owner, "name": name, "number": number},
    })
    if response.get("errors"):
        raise ValueError(f"Cannot read PR issue links: {response['errors']}")
    pr = response["data"]["repository"]["pullRequest"]
    if pr["isDraft"]:
        print("Draft PR: prerequisite work may continue; checks rerun when marked ready.")
        return
    references = pr["closingIssuesReferences"]
    if references["pageInfo"]["hasNextPage"]:
        raise ValueError("More than 100 closing references; split this PR into smaller deliveries.")
    closing = [issue["number"] for issue in references["nodes"] if issue["repository"]["nameWithOwner"].lower() == repository.lower()]
    if not closing:
        raise ValueError("Link a completed local issue using Closes #NUMBER; otherwise keep the PR as draft.")
    dependency_map = {
        issue: paginated(f"repos/{repository}/issues/{issue}/dependencies/blocked_by")
        for issue in closing
    }
    unresolved = unresolved_dependencies(closing, dependency_map)
    if unresolved:
        raise ValueError("Open prerequisites: " + "; ".join(f"#{issue} is blocked by #{blocker}" for issue, blocker in unresolved))
    print(f"All hard dependencies satisfied for {', '.join('#' + str(issue) for issue in closing)}.")


def main():
    repository = os.environ["GH_REPO"]
    command = sys.argv[1]
    if command == "sync":
        sync(repository)
    elif command == "check-pr":
        check_pr(repository, int(os.environ["PR_NUMBER"]))
    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"Workflow error: {exc}", file=sys.stderr)
        raise SystemExit(1)
