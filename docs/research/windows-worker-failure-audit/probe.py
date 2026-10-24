"""Bounded native Windows probe for PR5017; run against an exact source export.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Reuses Nick Petalas's BLOCK/SOLVER readiness fixtures and Mihir Srivastava's
retained-handle observer; follows JoyboyBrian's PR5017 failure-order question.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch


def require(value, message):
    if not value:
        raise AssertionError(message)


def authenticate(root):
    sources = json.loads(Path(__file__).with_name("SOURCES.json").read_bytes())
    for row in sources["files"]:
        require(hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "audited source drift: " + row["path"])


def exercise(runner, fixtures, handles_type, error_type, ordered=False):
    marker = error_type("native later worker failure")
    real_popen = subprocess.Popen
    owners = []
    timer = None
    observer = handles_type()
    caught = None
    failure_time = None
    with tempfile.TemporaryDirectory(prefix="native worker failure ") as temporary:
        root = Path(temporary)
        tests = root / "tests"
        tests.mkdir()
        first, second = tests / "test_a.py", tests / "test_b.py"
        first.write_text(fixtures.BLOCK, encoding="utf-8")
        second.write_text(fixtures.BLOCK.replace("module.pid", "second-module.pid")
                          .replace("solver.py", "second-solver.py"), encoding="utf-8")
        (root / "solver.py").write_text(fixtures.SOLVER, encoding="utf-8")
        (root / "second-solver.py").write_text(
            fixtures.SOLVER.replace("solver.pid", "second-solver.pid")
            .replace("ready", "second-ready"), encoding="utf-8")

        def launch(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            command = args[0]
            is_module = any("test_a.py" in word or "test_b.py" in word for word in command)
            if not is_module:
                return process
            owners.append(process)
            if any("test_b.py" in word for word in command):
                original_communicate = process.communicate
                armed = False

                def communicate(*args, **kwargs):
                    nonlocal armed, timer, failure_time
                    if not armed:
                        armed = True
                        require(fixtures.wait_for(lambda: (root / "ready").exists()
                                                  and (root / "second-ready").exists()),
                                "both real modules and solvers must be ready")
                        pids = [int((root / (name + ".pid")).read_text()) for name in
                                ("module", "solver", "second-module", "second-solver")]
                        pids += [owner.pid for owner in owners]
                        require(len(set(pids)) == 6, "observe two owners, modules and solvers")
                        for pid in pids:
                            observer.observe(pid)
                        require(not observer.all_stopped(), "live readiness control")
                        timer = threading.Timer(6, (root / "release").touch)
                        timer.start()
                        failure_time = time.monotonic()
                        raise marker
                    return original_communicate(*args, **kwargs)

                process.communicate = communicate
            return process

        try:
            with patch.object(runner.subprocess, "Popen", side_effect=launch):
                if ordered:
                    with patch.object(runner, "as_completed", side_effect=lambda futures: iter(futures)):
                        try:
                            runner.run_modules([first, second], tests_dir=tests, cwd=root, workers=2)
                        except BaseException as error:
                            caught = error
                else:
                    try:
                        runner.run_modules([first, second], tests_dir=tests, cwd=root, workers=2)
                    except BaseException as error:
                        caught = error
            require(caught is marker, "the original exception object must propagate")
            forced = (root / "release").exists()
            require(forced == ordered, "ordered wait control must need release; fix must not")
            require(fixtures.wait_for(observer.all_stopped, timeout=3),
                    "one of six retained native process handles survived controller cleanup")
            return {"error": error_type.__name__, "ordered_control": ordered,
                    "forced_release": forced, "observed_processes": len(observer.handles),
                    "all_stopped_before_teardown": True, "same_exception": True,
                    "elapsed_after_error_seconds": round(time.monotonic() - failure_time, 3)}
        finally:
            if timer is not None:
                timer.cancel()
                timer.join()
            (root / "release").touch()
            try:
                observer.close()
            finally:
                for owner in owners:
                    if owner.poll() is None:
                        owner.kill()
                    owner.wait(timeout=5)
                    for stream in (owner.stdout, owner.stderr):
                        stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    args = parser.parse_args()
    require(os.name == "nt", "requires native Windows, not WSL")
    root = args.export.resolve()
    authenticate(root)
    sys.path.insert(0, str(root / "tests"))
    import test_isolated_test_cancellation as fixtures
    from test_isolated_test_windows_exit import ProcessHandles
    spec = importlib.util.spec_from_file_location("audited_runner", root / "scripts/run_isolated_tests.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    results = [exercise(runner, fixtures, ProcessHandles, error_type)
               for error_type in (OSError, StopIteration, SystemExit)]
    results.append(exercise(runner, fixtures, ProcessHandles, OSError, ordered=True))
    authenticate(root)
    print(json.dumps({"status": "PASS_NATIVE_WINDOWS_WORKER_FAILURE", "cases": results}, indent=2))


if __name__ == "__main__":
    main()
