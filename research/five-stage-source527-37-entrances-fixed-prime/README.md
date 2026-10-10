# Recomputable fixed-prime refinement on PR251's 37 entrance construction

This arithmetic-only extension keeps PR251's physical word, 37 transported entrances, bank charts, source/dirty restoration, and all charged routes unchanged. It applies the fixed prime and rare-class density from PR235/PR252 to PR251's literal 24-replica profile, retains the full 32m^2 fallback for every rare child, extends the finite ordinary recurrence until the 10^-27 saving grid is reached, and uses the smaller outer backoff eta = 10^-24.

The exact result is kappa = 710433690953069816941696/10^27, improving PR251's 710433687047883/10^18 by 3905186816941696/10^27. The fixed-prime calculation with the prior eta = 10^-12 gives 710433690950939525300899/10^27; the additional backoff gain is 2130291640797/10^27.

## Reproduction

From the repository root, with Python 3.11+ and assertions enabled, run:

    python3 -m pip install -r research/five-stage-source527-37-entrances-fixed-prime/requirements.txt
    python3 -B research/five-stage-source527-37-entrances-fixed-prime/verify.py --output /tmp/source527-pr251-fixed-prime

The verifier replays all eight mandatory PR251 stages from pinned source, then recomputes both rational moment engines, all eight finite cutoff levels, the prime density, the 47 strict assembly inequalities, seven margins, and rejection of the adjacent final grid point. It requires a new output directory outside the checkout and uses no network during arithmetic replay. Prime.lean is checked separately in CI.

The full exact result and every finite cutoff are in expected.json. The package manifest pins every source and certificate file.
