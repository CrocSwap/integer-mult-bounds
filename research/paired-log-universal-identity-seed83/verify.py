#!/usr/bin/env python3
"""Noncommutative integer-polynomial certificate for PR1998's ordered inverse.

Copyright 2026 Sricharan Vagvala (@theon199). Apache-2.0.
Substantial OpenAI Codex assistance. No predecessor implementation is imported.
"""
import argparse
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RECIPE = "research/community-reconciliation-third100-audit/regenerated/pr377-outputs/work/odd-stages/RECIPE-9.json.gz"
RECIPE_SHA256 = "910fffd7b8980f1130d8bbec56d5ac34f92986c2a2c480b6aea40754b4b832ac"
CLAIM_SHA256 = "b1da940380e3ab650959f789c53e9e513a75db90d1cdac9b3040dd8b204a4f8f"
TYPES = ("V",) * 8 + ("L",) * 9
SIZE = len(TYPES)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def token(kind, stage):
    require(kind in ("R", "P", "Z") and type(stage) is int and 0 <= stage < 9,
            "invalid operator symbol")
    return 3 * stage + "RPZ".index(kind)


def label(symbol):
    return "RPZ"[symbol % 3] + str(symbol // 3)


def endpoints(symbol):
    require(type(symbol) is int and 0 <= symbol < 27, "invalid token")
    return ("V", "L") if symbol % 3 == 0 else ("L", "V")


@dataclass
class Expression:
    codomain: str
    # (original input block, ordered operator word) -> integer coefficient.
    # Words are written in multiplication order, acting rightmost first.
    terms: dict


class Algebra:
    def __init__(self, disabled=()):
        self.disabled = frozenset(disabled)

    def normal(self, word):
        stack = []
        for symbol in word:
            if (stack and stack[-1] % 3 == 0 and symbol % 3 in (1, 2)
                    and stack[-1] // 3 == symbol // 3
                    and symbol not in self.disabled):
                stack.pop()  # R_s P_s = R_s Z_s = identity on L.
            else:
                stack.append(symbol)
        return tuple(stack)

    def zero(self, codomain):
        require(codomain in ("V", "L"), "unknown module")
        return Expression(codomain, {})

    def identity(self):
        return [Expression(space, {(j, ()): 1}) for j, space in enumerate(TYPES)]

    def add(self, *summands):
        require(bool(summands), "empty sum")
        space = summands[0][1].codomain
        result = {}
        for coefficient, expression in summands:
            require(type(coefficient) is int, "noninteger coefficient")
            require(expression.codomain == space, "ill-typed addition")
            for monomial, value in expression.terms.items():
                result[monomial] = result.get(monomial, 0) + coefficient * value
                if not result[monomial]:
                    del result[monomial]
        return Expression(space, result)

    def act(self, kind, stage, expression):
        symbol = token(kind, stage)
        source, target = endpoints(symbol)
        require(expression.codomain == source, "ill-typed operator action")
        result = {}
        for (j, word), coefficient in expression.terms.items():
            monomial = (j, self.normal((symbol,) + word))
            result[monomial] = result.get(monomial, 0) + coefficient
            if not result[monomial]:
                del result[monomial]
        return Expression(target, result)

    def substitute(self, operator, values):
        require(len(values) == SIZE, "wrong block count")
        require(tuple(v.codomain for v in values) == TYPES, "wrong input modules")
        result = []
        for expression in operator:
            terms = [(1, self.zero(expression.codomain))]
            for (j, word), coefficient in expression.terms.items():
                value = values[j]
                for symbol in reversed(word):
                    value = self.act("RPZ"[symbol % 3], symbol // 3, value)
                terms.append((coefficient, value))
            result.append(self.add(*terms))
        return result


def forward(algebra, values, recipe):
    """Literal chronological event semantics, independently transcribed."""
    a = algebra
    x, y, logs = list(values[:4]), list(values[4:8]), list(values[8:])
    for event in recipe:
        if event["kind"] == "terminal":
            continue  # Claim uses the boundary before the signed exchange.
        if event["kind"] == "bridge":
            dst, src, c = event["dst"], event["src"], event["coefficient"]
            x[dst] = a.add((1, x[dst]), (c, x[src]))
            y[src] = a.add((1, y[src]), (-c, y[dst]))
            continue
        require(event["kind"] == "local", "unknown event")
        s, j = event["stage"], event["pair"]
        if event["reverse"]:
            old = y[j]
            query = a.act("R", s, old)
            x[j] = a.add((1, x[j]), (-1, old))
            y[j] = a.add((1, old), (-1, a.act("P", s, query)),
                         (1, a.act("Z", s, logs[s])))
        else:
            query = a.act("R", s, x[j])
            x[j] = a.add((1, x[j]), (-1, a.act("Z", s, query)),
                         (1, a.act("P", s, logs[s])))
            y[j] = a.add((1, y[j]), (1, x[j]))
        logs[s] = query
    return x + y + logs


def reverse_events(algebra, values, recipe):
    """Reference inverse by undoing recorded events, without the closed decoder."""
    a = algebra
    x, y, logs = list(values[:4]), list(values[4:8]), list(values[8:])
    for event in reversed(recipe):
        if event["kind"] == "terminal":
            continue
        if event["kind"] == "bridge":
            dst, src, c = event["dst"], event["src"], event["coefficient"]
            x[dst] = a.add((1, x[dst]), (-c, x[src]))
            y[src] = a.add((1, y[src]), (c, y[dst]))
            continue
        s, j = event["stage"], event["pair"]
        if event["reverse"]:
            query = a.act("R", s, y[j])
            y[j] = a.add((1, y[j]), (-1, a.act("Z", s, query)),
                         (1, a.act("P", s, logs[s])))
            x[j] = a.add((1, x[j]), (1, y[j]))
        else:
            old = x[j]
            query = a.act("R", s, old)
            y[j] = a.add((1, y[j]), (-1, old))
            x[j] = a.add((1, old), (-1, a.act("P", s, query)),
                         (1, a.act("Z", s, logs[s])))
        logs[s] = query
    return x + y + logs


def closed_decoder(algebra, values, omitted_query=None):
    """PR1998 README equations, without its rational-matrix implementation."""
    a = algebra
    x, y, logs = values[:4], values[4:8], values[8:]
    c = [x[0]]
    for j in range(1, 4):
        c.append(a.add((1, x[j]), (-1, c[j - 1])))
    eta = [None] * 9
    eta[8] = a.act("R", 8, c[3])
    d_next = c[3]
    original_x, original_y = [None] * 4, [None] * 4
    for j in reversed(range(4)):
        b, f = 2 * j + 1, 2 * j + 2
        previous = c[j - 1] if j else a.zero("V")
        original_y[j] = a.add((-1, previous), (-1, c[j]),
                              (-1, a.act("Z", f, logs[f])),
                              (1, a.act("P", f, eta[f])))
        qb = a.zero("L") if omitted_query == b else a.act("R", b, y[j])
        eta[b] = a.add((1, qb), (-1, a.act("R", b, d_next)))
        d = a.add((-1, d_next), (1, a.act("P", b, logs[b])),
                  (-1, a.act("Z", b, eta[b])), (-1, original_y[j]))
        qe = a.zero("L") if omitted_query == 2 * j else a.act("R", 2 * j, y[j])
        eta[2 * j] = a.add((1, qe), (1, a.act("R", 2 * j, d)))
        if j:
            original_x[j] = a.add((1, y[j]), (1, d), (-1, previous))
        else:
            original_x[0] = a.add((1, y[0]), (1, d),
                                  (-1, a.act("P", 0, eta[0])),
                                  (1, a.act("Z", 0, logs[0])))
        d_next = d
    return original_x + original_y + eta


def slow_normal(word, rightmost=False):
    """Independent whole-word rewrite; does not call the stack normalizer."""
    word = list(word)
    while True:
        sites = [i for i in range(len(word) - 1)
                 if word[i] % 3 == 0 and word[i + 1] % 3 in (1, 2)
                 and word[i] // 3 == word[i + 1] // 3]
        if not sites:
            return tuple(word)
        site = sites[-1] if rightmost else sites[0]
        del word[site:site + 2]


def normalizer_controls():
    a = Algebra()
    count = 0
    # Seed 83 chooses stages 8 and 3; the main identities use all nine stages.
    alphabet = tuple(token(kind, stage) for stage in (8, 3) for kind in "RPZ")
    frontier = [("V", ()), ("L", ())]
    for length in range(9):
        for space, word in frontier:
            require(a.normal(word) == slow_normal(word) == slow_normal(word, True),
                    "normalizer disagreement")
            count += 1
        if length < 8:
            frontier = [(target, (symbol,) + word)
                        for space, word in frontier for symbol in alphabet
                        for source, target in [endpoints(symbol)] if source == space]
    cross_stage = (token("R", 8), token("P", 3))
    require(a.normal(cross_stage) == cross_stage, "cross-stage cancellation")
    product = (token("Z", 8), token("R", 3), token("P", 3), token("R", 8))
    swapped = (token("P", 3), token("R", 8), token("Z", 8), token("R", 3))
    require(a.normal(product) != a.normal(swapped), "operator order lost")
    try:
        a.act("P", 0, a.identity()[0])
    except ValueError as error:
        require(str(error) == "ill-typed operator action", "wrong typing failure")
    else:
        raise ValueError("ill-typed action accepted")
    return count


def serial(matrix):
    return [{"codomain": row.codomain,
             "terms": [[j, coefficient, [label(s) for s in word]]
                       for (j, word), coefficient in sorted(row.terms.items())]}
            for row in matrix]


def check(recipe):
    a = Algebra()
    identity = a.identity()
    word = forward(a, identity, recipe)
    decoder = closed_decoder(a, identity)
    inverse = reverse_events(a, identity, recipe)
    require(decoder == inverse, "closed decoder disagrees with reverse events")
    require(a.substitute(decoder, word) == identity, "decoder after word is not identity")
    require(a.substitute(word, decoder) == identity, "word after decoder is not identity")
    hidden = set(8 + s for s in (1, 3, 5, 7))
    visible = word[:4] + word[8:]
    require(all(j not in hidden for row in visible for j, _ in row.terms),
            "odd-log hiding identity")
    controls = []
    for symbol in (token(kind, s) for s in range(9) for kind in "PZ"):
        weaker = Algebra(disabled=(symbol,))
        w = forward(weaker, weaker.identity(), recipe)
        d = closed_decoder(weaker, weaker.identity())
        require(weaker.substitute(d, w) != weaker.identity()
                or weaker.substitute(w, d) != weaker.identity(),
                "missing premise undetected: R" + str(symbol // 3) + label(symbol))
        controls.append("disable_R" + str(symbol // 3) + label(symbol))
    for site, event in enumerate(recipe):
        if event["kind"] == "terminal":
            continue
        omitted = recipe[:site] + recipe[site + 1:]
        mutant = forward(a, identity, omitted)
        require(a.substitute(decoder, mutant) != identity, "missing event undetected")
        controls.append("omit_event_" + str(site))
        if event["kind"] == "bridge":
            changed = [dict(e) for e in recipe]
            changed[site]["coefficient"] *= -1
            mutant = forward(a, identity, changed)
            require(a.substitute(decoder, mutant) != identity, "bridge sign undetected")
            controls.append("negate_bridge_" + str(site))
    for s in range(8):
        mutant = closed_decoder(a, identity, omitted_query=s)
        require(a.substitute(mutant, word) != identity, "missing reader undetected")
        controls.append("omit_Y_query_R" + str(s))
    normal_words = normalizer_controls()
    return {"schema_version": 1, "status": "PASS_PAIRED_LOG_UNIVERSAL_IDENTITY",
            "algebra": "typed Z-linear operator words; only R_s P_s = R_s Z_s = I_L",
            "recipe_sha256": RECIPE_SHA256, "pr1998_readme_sha256": CLAIM_SHA256,
            "blocks": SIZE, "stages": 9, "two_sided_block_identities": 2 * SIZE * SIZE,
            "reverse_decoder_block_identities": SIZE * SIZE,
            "hidden_odd_input_logs": sorted(hidden),
            "normalizer_words": normal_words, "normalizer_max_length": 8,
            "rejected_controls": controls,
            "forward": serial(word), "decoder": serial(decoder),
            "scope": "Symbolic certificate for the fixed controller; no native invoice, observation-rank theorem, Lean proof or new kappa."}


def load_inputs():
    raw = (ROOT / RECIPE).read_bytes()
    require(sha256(raw).hexdigest() == RECIPE_SHA256, "controller source drift")
    recipe = json.loads(gzip.decompress(raw))
    require(len(recipe) == 19 and recipe[-1] == {"kind": "terminal", "pairs": 4},
            "wrong controller boundary")
    raw_claim = (PACKAGE / "references/PR1998-README.md").read_bytes()
    require(sha256(raw_claim).hexdigest() == CLAIM_SHA256, "PR1998 claim source drift")
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    certificate = check(load_inputs())
    path = PACKAGE / "CERTIFICATE.json.gz"
    if args.write_certificate:
        raw = (json.dumps(certificate, indent=2) + "\n").encode("utf-8")
        path.write_bytes(gzip.compress(raw, mtime=0))
    else:
        expected = json.loads(gzip.decompress(path.read_bytes()))
        require(json.dumps(certificate, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "certificate mismatch")
    print(certificate["status"] + " blocks=17 stages=9 two_sided_identities=578"
          + " normalizer_words=" + str(certificate["normalizer_words"])
          + " controls=" + str(len(certificate["rejected_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
