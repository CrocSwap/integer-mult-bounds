"""Failure controls for overlap coverage, package provenance and bounded replay."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import find_overlap as overlap
import new_research_package as scaffold
import research_package as package
import research_baseline as baseline
sys.path.pop(0)


class OverlapTests(unittest.TestCase):
    def test_body_only_matches_and_no_clean_certificate(self):
        records = [{"kind": "pr", "title": "A modest change", "body": "Exact dirty connector alphabet proof", "head": "a" * 40},
                   {"kind": "discussion-comment", "title": "Claims", "body": "Testing nine-term decoder"}]
        matches = overlap.search(records, ["connector", "alphabet"], all_terms=True)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["head"], "a" * 40)
        self.assertEqual(overlap.search(records, ["missing"]), [])

    def test_report_survives_a_cp1252_stdout(self):
        # Supply the excerpt ourselves, independently of checkout contents or user caches.
        # Forcing cp1252 reproduces a Windows pipe on any host.
        env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            script = root / "scripts/find_overlap.py"
            script.parent.mkdir(parents=True)
            script.write_bytes((ROOT / "scripts/find_overlap.py").read_bytes())
            readme = root / "research/fixture/README.md"
            readme.parent.mkdir(parents=True)
            readme.write_text("Fixture contains κ", encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(script), "κ", "--offline",
                                     "--cache", str(Path(tmp) / "overlap.json")],
                                    cwd=root, env=env, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertIn(b"1 possible matches; showing 1", result.stdout)
        self.assertIn(b"Fixture contains \\u03ba", result.stdout)

    def test_pr_pagination_normalization(self):
        def row(n):
            return {"number": n, "title": "t", "body": "body", "html_url": f"url{n}",
                    "head": {"sha": str(n)}, "updated_at": "date", "state": "open", "draft": True}
        result = overlap.pull_records([[row(1)], [row(2)]])
        self.assertEqual([x["number"] for x in result], [1, 2])
        self.assertTrue(all(x["draft"] for x in result))

    def test_discussion_comment_and_reply_pagination(self):
        calls = []
        def page(nodes, more=False):
            return {"nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": "next"}}
        def comment(text):
            return {"body": text, "url": text, "updatedAt": "date"}
        def api(query, variables):
            calls.append(variables)
            if 'repository(owner:' in query:
                return {"repository": {"discussions": page([
                    {"id": "D", "number": 1, "title": "thread", **comment("topic")}
                ] if variables["cursor"] is None else [], variables["cursor"] is None)}}
            if "... on DiscussionComment" in query:
                return {"node": {"replies": page([comment("late reply claim")])}}
            if variables["cursor"] is None:
                return {"node": {"comments": page([
                    {"id": "C", **comment("first claim"), "replies": page([comment("early reply")], True)}
                ], True)}}
            return {"node": {"comments": page([
                {"id": "C2", **comment("late claim"), "replies": page([])}
            ])}}
        with patch.object(overlap, "graphql", side_effect=api):
            records = overlap.fetch_discussions()
        self.assertEqual(len(records), 5)
        self.assertEqual(len(calls), 5)
        self.assertIn("late reply claim", [r["body"] for r in records])
        self.assertIn("late claim", [r["body"] for r in records])

    def test_cache_fresh_offline_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            with patch.object(overlap, "gh_json", return_value=[[]]) as gh, patch.object(overlap, "fetch_discussions", return_value=[]):
                snapshot, warnings = overlap.remote_snapshot(cache)
                self.assertFalse(warnings)
                self.assertTrue(cache.is_file())
                overlap.remote_snapshot(cache)
                self.assertEqual(gh.call_count, 1)
            with patch.object(overlap, "gh_json", side_effect=AssertionError("offline network request")):
                _, warnings = overlap.remote_snapshot(cache, offline=True)
                self.assertEqual(len(warnings), 2)
            with patch.object(overlap, "gh_json", side_effect=ValueError("API unavailable")), patch.object(overlap, "fetch_discussions", return_value=[]):
                newer, warnings = overlap.remote_snapshot(cache, refresh=True)
                self.assertEqual(newer["sources"]["open_prs"], snapshot["sources"]["open_prs"])
                self.assertTrue(any("refresh failed" in w for w in warnings))

    def test_local_readme_and_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "research/a").mkdir(parents=True)
            (root / "research/a/README.md").write_text("Open next questions: paired decoder")
            records = overlap.local_records(root)
            self.assertEqual(len(overlap.search(records, ["paired decoder"])), 1)
            self.assertEqual(len(records[0]["sha256"]), 64)
            (root / "research/a/TASK.json").write_text('{"open_questions":["joint decoder"]}')
            matches = overlap.search(overlap.local_records(root), ["joint decoder"])
            self.assertEqual(matches[0]["kind"], "local-task")


class OverlapPathIndexTests(unittest.TestCase):
    """Changed-file index for open PRs (discussion 1200 request: search by path)."""

    ROWS = [{"number": 7, "paths": ["docs/research/current-status.md", "README.md"], "truncated": False},
            {"number": 8, "paths": ["research/lean-external-review/EXPLAINER.md"], "truncated": True}]

    def test_path_report_exact_glob_substring_and_rejection(self):
        prs = [{"kind": "pr", "number": 7, "title": "T", "body": "b", "url": "u7", "head": "a" * 40,
                "updated_at": "d", "draft": False, "state": "open"}]
        exact = overlap.path_report(prs, self.ROWS, ["docs/research/current-status.md"])
        self.assertEqual([m["number"] for m in exact], [7])
        self.assertEqual(exact[0]["matched_paths"], ["docs/research/current-status.md"])
        self.assertFalse(exact[0]["truncated"])
        # basename substring and fnmatch glob both match
        self.assertEqual(overlap.path_report(prs, self.ROWS, ["current-status.md"])[0]["number"], 7)
        globbed = overlap.path_report(prs, self.ROWS, ["docs/*"])
        self.assertEqual(globbed[0]["matched_paths"], ["docs/research/current-status.md"])
        # rejection control: no PR changed a matching path
        self.assertEqual(overlap.path_report(prs, self.ROWS, ["TASK.json"]), [])
        # PR metadata joined when known (with a URL fallback when the metadata
        # snapshot is older than the file index), truncation flag preserved
        unjoined = overlap.path_report([], self.ROWS, ["EXPLAINER.md"])
        self.assertEqual(unjoined[0]["title"], "")
        self.assertEqual(unjoined[0]["url"],
                         "https://github.com/CrocSwap/integer-mult-bounds/pull/8")
        self.assertTrue(unjoined[0]["truncated"])

    def test_fetch_pr_files_paginates_and_flags_shortfall(self):
        def page(rows, more):
            return {"repository": {"pullRequests": {
                "pageInfo": {"hasNextPage": more, "endCursor": "next"},
                "nodes": [{"number": n, "headRefOid": "abc", "changedFiles": len(paths), "files": {
                    "pageInfo": {"hasNextPage": False},
                    "nodes": [{"path": p} for p in paths]}}
                    for n, paths, trunc in rows]}}}
        pages = [page([(1, ["a.txt", "b.txt"], False)], True),
                 page([(2, ["c.txt", "c.txt"], True)], False)]
        with patch.object(overlap, "graphql", side_effect=pages) as call:
            rows = overlap.fetch_pr_files()
        self.assertEqual(call.call_count, 2)
        self.assertEqual(rows[0], {"number": 1, "paths": ["a.txt", "b.txt"], "truncated": False})
        self.assertEqual(rows[1], {"number": 2, "paths": ["c.txt"], "truncated": True})

    def test_fetch_pr_files_skips_unavailable_file_lists(self):
        page = {"repository": {"pullRequests": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"number": 376, "files": None},
                      {"number": 9, "headRefOid": "abc", "changedFiles": 1,
                       "files": {"pageInfo": {"hasNextPage": False},
                                              "nodes": [{"path": "ok.md"}, None]}}]}}}
        with patch.object(overlap, "graphql", return_value=page):
            rows = overlap.fetch_pr_files()
        self.assertEqual(rows[0], {"number": 9, "paths": ["ok.md"], "truncated": False})
        # An unavailable file list is recorded as empty and flagged, never silently trusted.
        self.assertEqual(rows[1], {"number": 376, "paths": [], "truncated": True})

    def test_fetch_pr_files_retries_transient_page_failures(self):
        page = {"repository": {"pullRequests": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"number": 1, "headRefOid": "abc", "changedFiles": 1,
                       "files": {"pageInfo": {"hasNextPage": False},
                                              "nodes": [{"path": "a.md"}]}}]}}}
        boom = subprocess.CalledProcessError(1, "gh api graphql")
        with patch.object(overlap, "graphql", side_effect=[boom, boom, page]) as call, \
             patch.object(overlap.time, "sleep") as slept:
            rows = overlap.fetch_pr_files()
        self.assertEqual(rows, [{"number": 1, "paths": ["a.md"], "truncated": False}])
        self.assertEqual(call.call_count, 3)
        self.assertEqual(slept.call_count, 2)
        with patch.object(overlap, "graphql", side_effect=[boom] * 4), \
             patch.object(overlap.time, "sleep"):
            with self.assertRaises(subprocess.CalledProcessError):
                overlap.fetch_pr_files()

    def test_pr_files_fetched_only_when_requested_and_cached(self):
        rows = [{"number": 3, "paths": ["x.md"], "truncated": False}]
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            with patch.object(overlap, "gh_json", return_value=[[]]), \
                 patch.object(overlap, "fetch_discussions", return_value=[]), \
                 patch.object(overlap, "fetch_pr_files", return_value=rows) as files_fetch:
                # Existing invocations pay nothing: pr_files is not fetched or warned about.
                snapshot, warnings = overlap.remote_snapshot(cache)
                self.assertFalse(warnings)
                self.assertNotIn("pr_files", snapshot["sources"])
                self.assertEqual(files_fetch.call_count, 0)
                # A path query fetches it once and reuses the cache on the next query.
                first, warnings = overlap.remote_snapshot(cache, need_files=True)
                self.assertFalse(warnings)
                self.assertEqual(first["sources"]["pr_files"]["records"], rows)
                second, _ = overlap.remote_snapshot(cache, need_files=True)
                self.assertEqual(files_fetch.call_count, 1)
                self.assertEqual(second["sources"]["pr_files"]["records"], rows)
            with patch.object(overlap, "fetch_pr_files", side_effect=AssertionError("offline network request")):
                _, warnings = overlap.remote_snapshot(cache, offline=True, need_files=True)
                self.assertTrue(any("pr_files" in w for w in warnings))

    def test_pr_files_refresh_failure_keeps_old_records(self):
        rows = [{"number": 5, "paths": ["keep.md"], "truncated": False}]
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            with patch.object(overlap, "gh_json", return_value=[[]]), \
                 patch.object(overlap, "fetch_discussions", return_value=[]), \
                 patch.object(overlap, "fetch_pr_files", return_value=rows):
                overlap.remote_snapshot(cache, need_files=True)
            with patch.object(overlap, "gh_json", return_value=[[]]), \
                 patch.object(overlap, "fetch_discussions", return_value=[]), \
                 patch.object(overlap, "fetch_pr_files", side_effect=ValueError("API unavailable")):
                snapshot, warnings = overlap.remote_snapshot(cache, refresh=True, need_files=True)
            self.assertTrue(any("pr_files" in w and "refresh failed" in w for w in warnings))
            self.assertEqual(snapshot["sources"]["pr_files"]["records"], rows)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        # Pin line-ending handling so committed blobs equal working bytes on every host
        # (Git for Windows defaults to core.autocrlf=true).
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false")):
            package.git(self.root, "config", key, value)
        (self.root / "docs/research").mkdir(parents=True)
        (self.root / "certificates").mkdir()
        (self.root / "docs/research/agent-task-catalog.json").write_text(json.dumps({
            "priority_revision": 2, "tracks": [{"tasks": [{"id": "fixture", "question": "Change the alphabet", "acceptance_gate": "Price it"}]}]}))
        (self.root / "certificates/selected-result.json").write_text('{}')
        (self.root / "input.txt").write_text("pinned fixture\n")
        package.git(self.root, "add", ".")
        package.git(self.root, "-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")
        self.target = scaffold.create(self.root, "fixture", "fixture", "Fixture", ["input.txt"])

    def ready(self):
        task_path = self.target / "TASK.json"
        task = json.loads(task_path.read_text())
        task.update(bottleneck_link="Tests a changed paid contract", stop_rule="One exact fixture",
                    outcome="partial", evidence="Exact positive and negative fixtures", ai_assistance="Test fixture only",
                    open_questions=[dict(question="Which new operation?", why_it_matters="Changes the bill",
                                         first_step="Price one operation", blocked_by="No legal implementation yet")])
        task_path.write_text(json.dumps(task))
        path = self.target / "VERIFY.json"
        manifest = json.loads(path.read_text()); manifest["status"] = "ready"
        manifest["commands"][0]["checks"] = "Scoped test fixture"
        path.write_text(json.dumps(manifest))
        return task, manifest

    def test_scaffold_pins_and_refuses_overwrite(self):
        with self.assertRaises(ValueError):
            scaffold.create(self.root, "fixture", "fixture", "Fixture")
        with self.assertRaises(ValueError):
            scaffold.create(self.root, "../bad", "fixture", "Fixture")
        with self.assertRaises(ValueError):
            package.validate(self.root, "research/fixture")
        self.ready()
        package.validate(self.root, "research/fixture")
        pins = json.loads((self.target / "SOURCES.json").read_text())["files"]
        self.assertEqual(len(pins), 3)
        self.assertTrue(all(len(r["sha256"]) == 64 and len(r["git_blob"]) == 40 for r in pins))

    def test_scope_drift_requires_reason(self):
        task, _ = self.ready()
        path = self.target / "TASK.json"
        task["actual_scope"] = "Increase source count inside the old alphabet"
        path.write_text(json.dumps(task))
        with self.assertRaisesRegex(ValueError, "different wording/scope"):
            package.validate(self.root, "research/fixture")
        task["scope_status"] = "changed"
        path.write_text(json.dumps(task))
        with self.assertRaisesRegex(ValueError, "explain"):
            package.validate(self.root, "research/fixture")
        task["scope_change_reason"] = "A side result with a clearly stated restricted implication"
        path.write_text(json.dumps(task))
        package.validate(self.root, "research/fixture")

    def test_utf8_metadata_validates_under_any_locale(self):
        # Byte 0x9d (in U+201D) is undefined in cp1252, the default Windows codec.
        task, _ = self.ready()
        task["evidence"] = "Exact κ moment — “priced”"
        (self.target / "TASK.json").write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
        readme = self.target / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n## Open next questions\n\n“Which κ?”\n",
                          encoding="utf-8")
        validated, _ = package.validate(self.root, "research/fixture")
        self.assertEqual(validated["evidence"], task["evidence"])

    def test_live_input_drift_but_provenance_survives_priority_change(self):
        self.ready()
        (self.root / "docs/research/agent-task-catalog.json").write_text('{"new":"priority"}')
        package.validate(self.root, "research/fixture")
        (self.root / "input.txt").write_text("changed input")
        with self.assertRaisesRegex(ValueError, "source drift"):
            package.validate(self.root, "research/fixture")

    def test_original_contract_and_timeout_limits(self):
        task, manifest = self.ready()
        task["original_card"]["acceptance_gate"] = "No gate"
        (self.target / "TASK.json").write_text(json.dumps(task))
        with self.assertRaisesRegex(ValueError, "original card"):
            package.validate(self.root, "research/fixture")
        self.set_task_contract_back()
        manifest["commands"][0]["timeout_seconds"] = 10000
        (self.target / "VERIFY.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "timeout"):
            package.validate(self.root, "research/fixture")

    def set_task_contract_back(self):
        path = self.target / "TASK.json"
        task = json.loads(path.read_text())
        task["original_card"]["acceptance_gate"] = "Price it"
        path.write_text(json.dumps(task))

    def test_dependency_plan_and_runtime_failure(self):
        self.ready()
        self.assertEqual(package.plan(self.root, ["input.txt"]), ["research/fixture"])
        self.assertEqual(package.plan(self.root, ["research/fixture/README.md"]), ["research/fixture"])
        self.assertEqual(package.plan(self.root, ["unrelated.txt"]), [])
        self.assertEqual(package.plan(self.root, ["docs/research/agent-task-catalog.json"]), [])
        with self.assertRaisesRegex(ValueError, "exited 3"):
            package.run_command([sys.executable, "-c", "raise SystemExit(3)"], self.root, 5)
        with self.assertRaisesRegex(ValueError, "timed out"):
            package.run_command([sys.executable, "-c", "import time; time.sleep(5)"], self.root, 0.05)

    @unittest.skipUnless(sys.version_info[:2] == (3, 12), "generic replay environment is Python 3.12")
    def test_ready_package_replays_and_mutation_fails(self):
        self.ready()
        verifier = self.target / "verify.py"
        verifier.write_text('from pathlib import Path\nif Path("input.txt").read_text() != "pinned fixture\\n": raise SystemExit(2)\n')
        package.run_package(self.root, "research/fixture")
        verifier.write_text('raise SystemExit(7)\n')
        with self.assertRaisesRegex(ValueError, "exited 7"):
            package.run_package(self.root, "research/fixture")

    def test_inherited_optimization_cannot_disable_child_checks(self):
        for value in ("1", "2"):
            with self.subTest(value=value), patch.dict(os.environ, {"PYTHONOPTIMIZE": value}):
                with self.assertRaisesRegex(ValueError, "exited 1"):
                    package.run_command([sys.executable, "-c", 'assert False, "invalid fixture"'], self.root, 5)
                self.assertEqual(os.environ["PYTHONOPTIMIZE"], value)

    def test_nested_interpreter_and_explicit_options(self):
        output = self.root / "mode.json"
        nested = "import json,os,sys; print(json.dumps([sys.flags.optimize, __debug__, os.environ.get('REPLAY_SENTINEL')]))"
        program = (
            "import json,subprocess,sys; from pathlib import Path; "
            f"child = json.loads(subprocess.check_output([sys.executable, '-c', {nested!r}])); "
            f"Path({str(output)!r}).write_text(json.dumps([sys.flags.optimize, __debug__, child]))"
        )
        with patch.dict(os.environ, {"PYTHONOPTIMIZE": "2", "REPLAY_SENTINEL": "preserved"}):
            for options, mode in (([], 0), (["-O"], 1), (["-OO"], 2)):
                with self.subTest(options=options):
                    package.run_command([sys.executable, *options, "-c", program], self.root, 5)
                    self.assertEqual(json.loads(output.read_text()),
                                     [mode, mode == 0, [0, True, "preserved"]])

    @unittest.skipUnless(sys.version_info[:2] == (3, 12), "generic replay environment is Python 3.12")
    def test_cli_replay_cannot_accept_assertion_failure_from_environment(self):
        self.ready()
        scripts = self.root / "scripts"
        scripts.mkdir()
        runner = scripts / "research_package.py"
        runner.write_bytes((ROOT / "scripts/research_package.py").read_bytes())
        verifier = self.target / "verify.py"
        argv = [sys.executable, "-B", str(runner), "--package", "research/fixture"]
        for value in ("", "0", "1", "2"):
            env = dict(os.environ, PYTHONOPTIMIZE=value)
            with self.subTest(value=value):
                verifier.write_text('assert False, "invalid fixture"\nprint("INVALID_FIXTURE_ACCEPTED")\n')
                result = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("AssertionError: invalid fixture", result.stderr)
                self.assertNotIn("PASS_REGISTERED", result.stdout)
                self.assertNotIn("INVALID_FIXTURE_ACCEPTED", result.stdout)
                verifier.write_text('assert 6 * 7 == 42\n')
                result = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_REGISTERED_RESEARCH_PACKAGE research/fixture", result.stdout)


class TextEncodingTests(unittest.TestCase):
    SCRIPTS = ("choose_research_task.py", "find_overlap.py", "new_research_package.py",
               "research_baseline.py", "research_package.py")

    def test_onboarding_text_io_does_not_depend_on_host_locale(self):
        # A UTF-8 CI host cannot observe locale-codec bugs, so check the calls statically.
        missing = []
        for name in self.SCRIPTS:
            for node in ast.walk(ast.parse((ROOT / "scripts" / name).read_text(encoding="utf-8"))):
                if not isinstance(node, ast.Call):
                    continue
                func = getattr(node.func, "attr", getattr(node.func, "id", None))
                keywords = {k.arg: k.value for k in node.keywords}
                mode = keywords.get("mode", node.args[0] if func == "open" and node.args else None)
                binary = isinstance(mode, ast.Constant) and "b" in str(mode.value)
                text = any(isinstance(keywords.get(k), ast.Constant) and keywords[k].value is True
                           for k in ("text", "universal_newlines"))
                if ((func in ("read_text", "write_text", "open", "NamedTemporaryFile") and not binary
                        or func in ("run", "Popen", "check_output") and text) and "encoding" not in keywords):
                    missing.append(f"{name}:{node.lineno}")
        self.assertEqual(missing, [])


class BaselineTests(unittest.TestCase):
    def test_binding_and_target_are_derived(self):
        record = {"kappa": "1/1000", "review": "r", "certificate": "c", "reproduce": "command"}
        result = baseline.summarize(record, {"bit_lower": "1/100", "complex_lower": "1/200"})
        self.assertEqual(result["binding_primitive"], "complex")
        self.assertEqual(result["target_primitive_under_retained_transfer"], "1/99")
        self.assertEqual(result["ideal_balanced_cap"], "1/201")


if __name__ == "__main__":
    unittest.main()
