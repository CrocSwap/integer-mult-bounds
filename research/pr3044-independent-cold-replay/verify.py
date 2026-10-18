#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Data-only R2 audit. No author engine imports; exact rational sparse operators
and GF(2) row elimination. Local scoped evidence, not supplier admission.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PARENT = ROOT / "research/rank7-joint-endframes/data"
SOURCE = ROOT / "research/rank7-shared-restore-fanin"
TOUCHED = (18, 22, 40, 54)
W = [256,128,64,34,17,11,4]
E42 = [256,128,64,34,16,10,4,1]
FULL = [256,128,64,32,16,8,4,2,1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    out = dict(pairs)
    need(len(out) == len(pairs), 'duplicate JSON key')
    return out


def read(path):
    raw = path.read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique_pairs)


def basis(vectors):
    """A pivot dictionary gives exact rank/membership without enumerating span."""
    out = {}
    for value in vectors:
        need(type(value) is int and 0 <= value < 512, 'invalid vector')
        while value:
            pivot = value.bit_length() - 1
            if pivot in out:
                value ^= out[pivot]
            else:
                out[pivot] = value
                break
    return out


def contained(small, big):
    return len(basis([*small, *big])) == len(basis(big))


def addresses(op):
    if op[0] == 'add':
        return (op[1], op[2])
    if op[0] in ('scale', 'warp'):
        return (op[1],)
    raise ValueError('unknown operation ' + str(op[0]))


def symbolic(ops):
    """A sparse row maps independent dirty input symbols to Q coefficients."""
    rows = {}
    def row(r):
        return rows.setdefault(r, {r: Fraction(1)})
    for op in ops:
        kind, dst = op[:2]
        need(kind in ('add', 'scale'), 'non-scalar restore operation')
        if kind == 'scale':
            coefficient = Fraction(op[2], op[3])
            need(coefficient != 0, 'noninvertible scale')
            rows[dst] = {key: value * coefficient for key, value in row(dst).items()}
        else:
            src, numerator, denominator = op[2:5]
            coefficient = Fraction(numerator, denominator)
            updated = dict(row(dst))
            for key, value in row(src).items():
                updated[key] = updated.get(key, Fraction(0)) + coefficient * value
                if not updated[key]:
                    del updated[key]
            rows[dst] = updated
    # Remove identity rows, so the same independent identity extension is implicit.
    return {r: values for r, values in rows.items() if values != {r: Fraction(1)}}


def scalar_encoding(ops):
    out = []
    for op in ops:
        if op[0] == 'add':
            out.append((op[0], op[1], op[2], Fraction(op[3],op[4]), tuple(op[5])))
        elif op[0] == 'scale':
            out.append((op[0], op[1], Fraction(op[2],op[3]), tuple(op[4])))
        else:
            raise ValueError('non-scalar prefix')
    return out


def inverse_cleanup_prefix(word):
    private = {int(r) for r in word['helper_final']}
    def renamed(r):
        return r + 704 if r in private else r
    result = []
    for op in reversed(word['restore']):
        if op[0] == 'add':
            q = -Fraction(op[3], op[4])
            result.append(['add', renamed(op[1]), renamed(op[2]), q.numerator, q.denominator, FULL])
        elif op[0] == 'scale':
            q = 1 / Fraction(op[2], op[3])
            result.append(['scale', renamed(op[1]), q.numerator, q.denominator, FULL])
        else:
            raise ValueError('non-scalar restore prefix')
    return result


def frame_itinerary(word):
    # Only these four data registers matter for R2; they have rank-one entry
    # frames and no coordinate warps. We verify that latter premise from data.
    need(not any(w[1] in TOUCHED for w in word['warps']), 'touched external warp')
    need(not set(TOUCHED) & set(word['centers']), 'omitted centre path')
    need(not set(TOUCHED) & {int(r) for r in word['start_extra']}, 'non-port entry frame')
    for phase in ('precondition', 'compensation'):
        need(not any(set(addresses(op)) & set(TOUCHED) for op in word[phase]),
             'omitted scalar contact in ' + phase)
    need(not any({op['source'], op['target']} & set(TOUCHED)
                 for op in word['initial_corrections']), 'omitted initial correction')
    current = {r: [word['ports'][r]] for r in TOUCHED}
    jumps = Counter()
    history = {r: [] for r in TOUCHED}
    def advance(r, frame, label):
        need(contained(current[r], frame), 'frame regresses at ' + label + '/' + str(r))
        old, new = len(basis(current[r])), len(basis(frame))
        if new > old:
            jumps[new - old] += 1
            history[r].append([label, old, new])
        current[r] = frame
    for phase in ('A', 'B', 'restore'):
        for i, op in enumerate(word[phase]):
            contacts = set(addresses(op)) & set(TOUCHED)
            if not contacts:
                continue
            need(op[0] != 'warp', 'touched inline warp')
            for r in sorted(contacts):
                advance(r, op[-1], phase + ':' + str(i))
    for r in TOUCHED:
        advance(r, FULL, 'exit')
    need(sum(rank * count for rank, count in jumps.items()) == 32, 'wrong touched rank mass')
    return dict(sorted(jumps.items())), history


def apply_r1(parent, edits, provider):
    out = deepcopy(parent)
    selected = edits['edits'][provider]
    need(len(selected) == 1, 'unexpected R1 hunk count')
    edit = selected[0]
    need(edit['id'] == 'R1' and edit['section'] == 'restore', 'unexpected R1 edit')
    start, stop = edit['start'], edit['stop']
    need(out['restore'][start:stop] == edit['old'], 'R1 preimage mismatch')
    out['restore'][start:stop] = deepcopy(edit['new'])
    return out


def expected_r2(r1):
    ops = r1['restore']
    expected = {
        162: ['add',18,40,1,1,E42],
        163: ['add',18,54,-2,1,E42],
        175: ['add',22,40,1,1,E42],
        176: ['add',22,45,-1,1,E42],
        177: ['add',22,54,-2,1,E42],
    }
    for i, op in expected.items():
        need(ops[i] == op, 'R2 preimage mismatch at ' + str(i))
    contacts = [i for i in range(162, len(ops)) if set(addresses(ops[i])) & {40,54}]
    need(contacts == [162,163,175,177], 'unexpected dirty-source contact')
    # R1 is already applied and lies later than these four original locations.
    out = []
    for i, op in enumerate(ops):
        if i == 162:
            out.append(['add',40,54,-2,1,W])
        if i not in (163,177):
            out.append(deepcopy(op))
    out.append(['add',40,54,2,1,FULL])
    return out


def check(parent, released, edits, provider):
    need(set(parent) == set(released), 'word key set changed')
    for key in parent:
        if key not in ('report','restore','cleanup'):
            need(parent[key] == released[key], 'unrelated changed word field: ' + key)
    r1 = apply_r1(parent, edits, provider)
    need(symbolic(parent['restore']) == symbolic(r1['restore']), 'R1 restore operator changed')
    need(released['restore'] == expected_r2(r1), 'released R2 literal mismatch')
    need(len(r1['restore']) == len(released['restore']) == 204, 'R2 scalar count changed')
    need(symbolic(r1['restore']) == symbolic(released['restore']), 'dirty restore operator changed')
    p_inv, r_inv = inverse_cleanup_prefix(parent), inverse_cleanup_prefix(released)
    need(scalar_encoding(parent['cleanup'][:len(p_inv)]) == scalar_encoding(p_inv), 'parent cleanup prefix mapping mismatch')
    need(scalar_encoding(released['cleanup'][:len(r_inv)]) == scalar_encoding(r_inv), 'released cleanup is not inverse restore')
    need(parent['cleanup'][len(p_inv):] == released['cleanup'][len(r_inv):], 'cleanup remainder changed')
    before, bh = frame_itinerary(r1)
    after, ah = frame_itinerary(released)
    need(before == {1:20,2:1,3:2,4:1}, 'unexpected R1 touched profile')
    need(after == {1:18,2:2,3:2,4:1}, 'unexpected R2 touched profile')
    for r in (18,22,40):
        need([x[1:] for x in bh[r]] == [x[1:] for x in ah[r]], 'unrelated touched itinerary changed')
    # The saved full profile is not used to derive the above frame delta.
    return {'provider':provider,'restore_operations':204,'sparse_nonidentity_rows':len(symbolic(released['restore'])),
            'r1_touched_profile':before,'r2_touched_profile':after,'r1_history':bh,'r2_history':ah,
            'unchanged_cleanup_tail':len(parent['cleanup'])-len(p_inv)}


def controls(parent, released, edits, provider):
    results = []
    def must_fail(name, f):
        try:
            f()
        except ValueError:
            results.append(name)
        else:
            raise ValueError('accepted negative control ' + name)
    r1 = apply_r1(parent, edits, provider)
    target = symbolic(r1['restore'])
    wrong = deepcopy(released['restore']); wrong[162][3] = -1
    must_fail('wrong_aggregation_coefficient', lambda: need(symbolic(wrong) == target, 'wrong coefficient'))
    missing = deepcopy(released['restore'][:-1])
    must_fail('missing_dirty_restoration', lambda: need(symbolic(missing) == target, 'missing restoration'))
    observer = deepcopy(released['restore']); observer.insert(170,['add',703,40,1,1,E42])
    reference = deepcopy(r1['restore']); reference.insert(170,['add',703,40,1,1,E42])
    must_fail('intervening_source_observer', lambda: need(symbolic(observer) == symbolic(reference), 'observer'))
    regressed = deepcopy(released); regressed['restore'][-1][-1] = W
    must_fail('unpaid_early_frame_restoration', lambda: frame_itinerary(regressed))
    lost = deepcopy(released); lost['restore'][162][-1] = E42
    must_fail('aggregation_frame_loses_saving', lambda: need(frame_itinerary(lost)[0] == {1:18,2:2,3:2,4:1}, 'wrong profile'))
    bad_cleanup = deepcopy(released); bad_cleanup['cleanup'][0][3] = 2
    must_fail('cleanup_inverse_sign', lambda: check(parent,bad_cleanup,edits,provider))
    return results


def audit(release_dir=None, release_pattern="WORD-{provider}.json.gz"):
    for entry in read(PACKAGE / "SOURCES.json")["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            need(actual == entry["sha256"], "pinned input changed: " + entry["path"])
    edits = read(SOURCE / "vendor/R1.json")
    output = {"algorithm": "sparse rational row propagation and GF2 pivot elimination", "providers": []}
    for provider in ("base", "extra"):
        parent = read(PARENT / f"WORD-{provider}.json.gz")
        published = read(SOURCE / "evidence" / f"WORD-{provider}.json.gz")
        released = published if release_dir is None else read(
            release_dir / release_pattern.format(provider=provider))
        need(released == published, "fresh word differs from complete published JSON payload")
        result = check(parent, released, edits, provider)
        result["rejected_controls"] = controls(parent, released, edits, provider)
        output["providers"].append(result)
    return json.loads(json.dumps(output))


def check_saved_evidence():
    """Integrity of recorded observations only; not a fresh native replay."""
    directory = PACKAGE / "evidence"
    manifest = read(directory / "SHA256SUMS.json")
    actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in directory.iterdir() if p.name != "SHA256SUMS.json"}
    need(actual == manifest, "saved evidence inventory or bytes changed")
    for stage in read(directory / "STAGES.json"):
        need(stage["exit_code"] == 0, "recorded stage failed")
        need(stage["log_sha256"] == manifest[stage["stage"] + ".log.txt"],
             "saved stage log binding")
    need(hashlib.sha256(gzip.decompress(
        (directory / "PREFIX-AND-INVOICE.json.gz").read_bytes())).hexdigest()
        == read(directory / "FRESH-BINDINGS.json")["checked_record_sha256"]["invoice"],
        "saved invoice payload differs from observed invoice")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--release-pattern", default="WORD-{provider}.json.gz")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    check_saved_evidence()
    output = audit(args.release_dir, args.release_pattern)
    if args.emit:
        print(json.dumps(output, sort_keys=True, indent=2))
    else:
        need(output == read(PACKAGE / "LOCAL-RESULT.json"), "local receipt differs")
        print("PASS_INDEPENDENT_R2_DATA_AUDIT providers=2 controls=12 delta=-2H1+H2")


if __name__ == "__main__":
    main()
