"""Independent labeled-word closure, f<=4.

DLamdata with OpenAI Codex skeptical-review assistance. Apache-2.0.
The oracle uses swap components and pair deletions, not crossing or piling.
"""
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import sys
import time

PKG = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def load(name):
    spec = importlib.util.spec_from_file_location(name, PKG / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

candidate = load('verify')

def words(letters):
    counts = {a: 2 for a in letters}
    result = []
    def extend(prefix):
        if len(prefix) == 2 * len(letters):
            result.append(prefix)
            return
        for a in letters:
            if counts[a]:
                counts[a] -= 1
                extend(prefix + (a,))
                counts[a] += 1
    extend(())
    return result

def canonical(word):
    labels = {}
    result = []
    for a in word:
        if a not in labels:
            labels[a] = len(labels)
        result.append(labels[a])
    return tuple(result)

def accepted_by_components(n, allowed, domain):
    """Swap components at each subset; seed by deletion into smaller subsets.

    This is exhaustive search of the literal rewrite relation. It neither uses
    interval crossings nor piling. All labeled words are generated independently.
    """
    accepted = {(): True}
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            ws = domain[subset]
            lookup = {w: i for i, w in enumerate(ws)}
            parent = list(range(len(ws)))
            def root(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i
            deletion_seeds = []
            for i, w in enumerate(ws):
                for k in range(len(w) - 1):
                    a, b = w[k:k + 2]
                    if a == b:
                        if accepted[w[:k] + w[k + 2:]]:
                            deletion_seeds.append(i)
                    elif frozenset((a, b)) in allowed:
                        v = w[:k] + (b, a) + w[k + 2:]
                        ri, rj = root(i), root(lookup[v])
                        if ri != rj:
                            parent[ri] = rj
            good = {root(i) for i in deletion_seeds}
            for i, w in enumerate(ws):
                accepted[w] = root(i) in good
    return accepted

def census():
    rows = []
    for n in range(5):
        domain = {subset: words(subset) for k in range(n + 1)
                  for subset in itertools.combinations(range(n), k)}
        full = domain[tuple(range(n))]
        canonical_words = {canonical(w) for w in full}
        need(canonical_words == set(candidate.paired_words(n)),
             ('canonical coverage mismatch', n))
        edges = list(itertools.combinations(range(n), 2))
        accepted_count = rejected_count = 0
        canonical_accepted = canonical_rejected = 0
        for mask in range(1 << len(edges)):
            allowed = {frozenset(e) for k, e in enumerate(edges) if mask & (1 << k)}
            accepted = accepted_by_components(n, allowed, domain)
            deps = candidate.dependencies(n, mask)
            for w in full:
                actual = accepted[w]
                need(actual == candidate.piling_identity(w, deps),
                     ('piling discrepancy', n, mask, w))
                needed = candidate.crossing_mask(w, n)
                need(actual == (needed & mask == needed),
                     ('crossing discrepancy', n, mask, w))
                accepted_count += actual
                rejected_count += not actual
                if w in canonical_words:
                    canonical_accepted += actual
                    canonical_rejected += not actual
        row = dict(columns=n, labeled_words=len(full), graphs=1 << len(edges),
                   accepted=accepted_count, rejected=rejected_count,
                   canonical_accepted=canonical_accepted,
                   canonical_rejected=canonical_rejected)
        receipt = json.loads((PKG / 'RESULT.json').read_text())['domain'][n]
        need(canonical_accepted == receipt['accepted'] and
             canonical_rejected == receipt['rejected'], ('receipt mismatch', n))
        rows.append(row)
    return rows

started = time.monotonic()
result = {'python': sys.version, 'census': census()}
result['total_labeled_word_graph_cases'] = sum(r['accepted'] + r['rejected']
                                             for r in result['census'])
result['seconds'] = round(time.monotonic() - started, 3)
result['max_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
result['status'] = 'PASS_INDEPENDENT_LABELED_REWRITE_CLOSURE'
print(json.dumps(result, indent=2, sort_keys=True))
