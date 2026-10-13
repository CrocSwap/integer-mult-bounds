# Auto-research: instructions for agents

This repository is worked on by many human-guided AI agents at once (Codex, Claude Code and others). This file is the entry point for any agent starting a session. Read it first, then follow the shared prompt.

## 1. Start from the shared prompt

Use the community prompt maintained by @Mister-Meeseeks:

**https://gist.github.com/Mister-Meeseeks/9f768c8b1a3e7d2e70b8e5c0bc18ab7e**

In short, the prompt asks you to:

1. **Orient.** Clone the repo, record the base commit, and read [CONTRIBUTING.md](CONTRIBUTING.md), the [selected record](certificates/selected-result.json), the [current status](docs/research/current-status.md) and the [PR ledger](docs/research/pr-ledger.md). Older documents may quote superseded results.
2. **Pick one track** with a random seed (supplier improvements, structural/decoder research, recursive interfaces, adversarial audits, verification or consolidation).
3. **Claim your scope** on the coordination issue, if there is one, and avoid overlapping concurrent work.
4. **Run one bounded experiment.** Spend at most about 20% of the session orienting. Test a single hypothesis, and price its full cost before building anything large.
5. **Verify and package** on a separate branch with a reproducible command. Record negative results accurately and credit predecessor work.
6. **Hand off.** Open at most one focused PR with an accurate title, or leave a clean patch and a handoff note.

The gist is the authoritative version; this summary is only a pointer.

## 2. Where your work goes

New submissions go under [`auto-research/`](auto-research/README.md), one directory per package:

```
auto-research/<YYYY-MM-DD>-<handle>-<short-slug>/
  README.md        what was tried, the result, the exact reproduce command and its scope
  RESULT.json      machine-readable outcome (see auto-research/README.md)
  verify.py        or verify.sh: one command, standard library where possible
  MANIFEST.json    sha256 of every file in the package
  NOTICE.md        sources, credits and AI-assistance disclosure
  code/  data/  evidence/   as needed
```

Negative and no-gain results are welcome. Also add a short entry to the experiment log so other agents do not repeat the same search.

The existing [`research/`](research/) tree is **not** being moved. More than 1,600 files pin paths under `research/` (verifiers, manifests, hashes and the Makefile), so renaming it would break existing certificates. Treat `research/` as the frozen legacy tree: keep citing and pinning it, but put new packages under `auto-research/`.

## 3. Ground rules

- κ claims must come from an exact, reproducible replay (both moment engines and all strict outer inequalities), never from estimates.
- State scope honestly: finite certificate checks are not a full theorem, and "no candidate found" is not an impossibility proof.
- Keep `upstream/` unchanged, follow CONTRIBUTING.md, and run the checks your change affects.
- Credit every predecessor PR you build on, and disclose the models and harnesses you used.
- Do not use shared or production infrastructure that isn't yours for compute. Use your own sandboxes.
- Before starting, check the experiment log and recent `no new kappa` PRs for your idea.
