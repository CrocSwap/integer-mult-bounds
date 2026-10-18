"""Builds inputs/ (gz copies of PR files) and SOURCES.part.json from a clone of CrocSwap/integer-mult-bounds.
usage: vendor.py <clone> <pkg dir>.  Needs the PR heads fetched as refs/kpr2/pr<N> (git fetch origin pull/N/head:refs/kpr2/prN).
For a .gz copy of a non-.gz source the blob id is that of the decompressed content (as in #595 SOURCES.json)."""
import gzip, hashlib, json, os, subprocess, sys
clone, pkg = sys.argv[1:3]
def git(*a): return subprocess.check_output(('git', '-C', clone) + a)
PRS = [
 (595, 'research/format-limits/scripts/a5_scope_multipliers.py', 'inputs/pr595/a5_scope_multipliers.py', 0, 'E1: scope-multiplier script re-run unchanged'),
 (595, 'research/format-limits/scripts/skel.py', 'inputs/pr595/skel.py', 0, 'E1: imported by a5'),
 (595, 'research/format-limits/scripts/cert.py', 'inputs/pr595/cert.py', 0, 'E1: imported by skel'),
 (595, 'research/format-limits/scripts/report.py', 'inputs/pr595/report.py', 0, 'E1: imported by a5'),
 (626, 'research/complex-k492-owner-repair/data/PLAN.json', 'inputs/pr626/PLAN.json.gz', 1, 'P1,P3,P4: profile {width: count}, m = 73, live 7168, deficit 2560'),
 (626, 'research/complex-k492-owner-repair/README.md', 'inputs/pr626/README.md.gz', 1, 'P1: conditional kappa literal 0.001635527380375392'),
 (649, 'research/gauge44-bit589/data/PLAN.json', 'inputs/pr649/PLAN.json.gz', 1, 'P3: base profile of the rate table'),
 (645, 'research/gauge44-global/data/PLAN.json', 'inputs/pr645/PLAN.json.gz', 1, 'P3: profile reproduced'),
 (646, 'research/signed-root-k480/data/PLAN.json', 'inputs/pr646/PLAN.json.gz', 1, 'P3: profile reproduced'),
 (635, 'research/complex-571-cold14-st2/data/PLAN.json', 'inputs/pr635/PLAN.json.gz', 1, 'P3: profile reproduced'),
 (555, 'research/e8-bit-p111/EXPECTED.json', 'inputs/pr555/EXPECTED.json.gz', 1, 'P2: nine-stage bit profile, live, shipped c'),
]
files = []
for pr, src, dst, gz, used in PRS:
    commit = git('rev-parse', 'refs/kpr2/pr%d' % pr).decode().strip()
    data = git('show', '%s:%s' % (commit, src))
    blob = git('rev-parse', '%s:%s' % (commit, src)).decode().strip()
    out = os.path.join(pkg, dst); os.makedirs(os.path.dirname(out), exist_ok=True)
    if gz:
        with open(out, 'wb') as f:
            with gzip.GzipFile(fileobj=f, mode='wb', mtime=0) as g: g.write(data)
    else:
        open(out, 'wb').write(data)
    files.append({'file': dst, 'pr': pr, 'commit': commit, 'source_path': src, 'blob': blob, 'used_for': used})
json.dump(files, open(os.path.join(pkg, 'tools', 'vendor.out.json'), 'w'), indent=1)
