"""Check the repository automation's state decisions without GitHub writes."""

import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/github_workflow.py"
SPEC = importlib.util.spec_from_file_location("github_workflow", SCRIPT)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)


class DependencyStateTests(unittest.TestCase):
    def test_any_open_prerequisite_blocks_completion(self):
        labels = workflow.readiness({"state": "open"}, [{"state": "closed"}, {"state": "open"}])
        self.assertEqual(labels, {"workflow:blocked"})

    def test_closed_prerequisites_allow_ready_state(self):
        self.assertEqual(workflow.readiness({"state": "open"}, [{"state": "closed"}]), {"workflow:ready"})

    def test_closed_issue_is_not_left_ready_or_blocked(self):
        self.assertEqual(workflow.readiness({"state": "closed"}, [{"state": "open"}]), set())

    def test_pr_cannot_close_an_issue_with_open_external_prerequisites(self):
        unresolved = workflow.unresolved_dependencies([13], {13: [{"number": 9, "state": "open"}]})
        self.assertEqual(unresolved, [(13, 9)])

    def test_same_pr_can_complete_a_prerequisite_and_its_dependent(self):
        unresolved = workflow.unresolved_dependencies([9, 13], {13: [{"number": 9, "state": "open"}]})
        self.assertEqual(unresolved, [])

    def test_already_closed_prerequisites_do_not_fail_a_pr(self):
        unresolved = workflow.unresolved_dependencies([13], {13: [{"number": 9, "state": "closed"}]})
        self.assertEqual(unresolved, [])


if __name__ == "__main__":
    unittest.main()
