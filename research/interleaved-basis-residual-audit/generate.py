"""Produce candidate multipliers and response values for the direct checker.

This producer is not an acceptance check. Ali Romman with OpenAI Codex
assistance. Apache-2.0.
"""

from pathlib import Path
import gzip
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit


def functional(g, observation, order):
    remaining = dict(observation)
    multipliers = {}
    for key in reversed(order):
        factor = remaining.pop(key, 0)
        if factor:
            multipliers[key] = factor
            for donor, coefficient in g['forms'][key].items():
                audit.add(remaining, donor, factor * coefficient)
    return dict(multipliers=audit.packed(multipliers), expansion=audit.packed(remaining))


def response(g, pulse, entrance, order):
    values = {}
    for key in order:
        value = pulse.get(key, 0)
        for donor, coefficient in g['forms'][key].items():
            value += coefficient * (entrance.get(~donor, 0) if donor < 0 else values.get(donor, 0))
        if value:
            values[key] = value
    return audit.packed(values)


def identity(g, role, order):
    return dict(row=functional(g, {g['first'] + role: 1}, order),
                column=response(g, {}, {role: 1}, order))


def main():
    result = []
    for role, variant, restriction, split, g0, g in audit.cases():
        order0, order = audit.schedule(g0), audit.schedule(g)
        decoded = {g['first'] + key: value for key, value in audit.row(split['return_covector']).items()}
        item = dict(role=role, variant=variant, restriction_graph=audit.signature(g0), split_graph=audit.signature(g),
                    restriction=functional(g0, audit.observations(restriction), order0),
                    restriction_identity=identity(g0, restriction['role'], order0),
                    split_identity=identity(g, split['role'], order),
                    readout=functional(g, audit.row(split['readout']), order),
                    calibration=functional(g, audit.difference(audit.row(split['calibration']), decoded), order),
                    pulse=response(g, audit.row(split['pulse']), {}, order),
                    steering=response(g, {}, audit.row(split['source_direction']), order))
        result.append(item)
        print('GENERATED', role, variant, flush=True)
    raw = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    (audit.ROOT / 'CERTIFICATE.json.gz').write_bytes(gzip.compress(raw, mtime=0))


if __name__ == '__main__':
    main()
