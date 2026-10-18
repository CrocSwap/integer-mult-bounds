#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the unchanged predecessor recipe with a larger outer wall-time allowance.

Only run_stage's resource timeout changes from 1,800 to at least 7,200 seconds.
Commands, domains, scientific predicates, log binding and final release checks
are the original PR3054 implementation. Substantial OpenAI Codex assistance.
"""

import argparse
import sys

import verify as v


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=v.Path, required=True)
    parser.add_argument("--work", type=v.Path, required=True)
    a = parser.parse_args()
    v.need(
        not a.work.resolve().is_relative_to(v.P),
        "baseline logs and cache must stay outside the published package",
    )
    v.authenticate()
    parent = v.ROOT / "research/rank7-t740-carrier-skips"
    sys.path.insert(0, str(parent))
    source = v.load(parent / "reproduce.py", "credited_baseline_budget")
    original = source.run_stage

    def run_stage(name, command, work, env, stages, timeout):
        allowance = max(timeout, 7200) if name == "complete-admission" else timeout
        return original(name, command, work, env, stages, allowance)

    source.run_stage = run_stage
    result = source.execute(a.repo.resolve(), a.work.resolve(), False)
    source.save(a.work.resolve() / "RESULT.json", result)
    v.need(
        result["status"] == "PASS_T740_SIX_SKIP_COMPLETE_RELEASE",
        "complete original baseline",
    )
    print(result["status"])


if __name__ == "__main__":
    main()
