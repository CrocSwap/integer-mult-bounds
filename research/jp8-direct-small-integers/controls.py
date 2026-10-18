"""Dense Fraction-matrix checks separate from the sparse integer replay.

Michał Ciemięga (@zewelor), with substantial OpenAI Codex assistance.
Apache-2.0. Both implementations were written in one AI session.
"""
from fractions import Fraction as Q
from lower import lower

T, S, W = ("T", 0), ("S", 0), ("W", 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_word(q, word, cost):
    rows = {T: [Q(1), Q(0), Q(0)], S: [Q(0), Q(1), Q(0)], W: [Q(0), Q(0), Q(1)]}
    reads = 0
    for ins in word:
        op, dst = ins[:2]
        need(dst in (T, W), "source mutation")
        if op in ("add", "subtract"):
            src = ins[2]
            need(src in rows and src != dst, "source alias")
            rows[dst] = [a + (1 if op == "add" else -1)*b for a, b in zip(rows[dst], rows[src])]
            reads += int(src == S)
        elif op == "clear":
            rows[dst] = [Q(0)]*3
        elif op == "copy":
            rows[dst] = rows[ins[2]].copy()
            reads += int(ins[2] == S)
        elif op in ("double", "halve", "negate"):
            factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[op]
            rows[dst] = [factor*x for x in rows[dst]]
        else:
            raise ValueError("unknown primitive")
        need(all(x.denominator == 1 for r in rows.values() for x in r), "fractional excursion")
        need(all(sum(abs(x) for x in r) <= 1+abs(q) for r in rows.values()), "magnitude excursion")
    need(rows == {T: [Q(1), Q(q), Q(0)], S: [Q(0), Q(1), Q(0)], W: [Q(0)]*3}, "endpoint or dirt")
    need(len(word) == cost, "unpaid instruction")
    need(reads == abs(q), "source read count")
    return {"cost": cost, "source_reads": reads, "columns": 3}


def run(baseline):
    positives = {}
    for q in (3, -3, 2, -2):  # Seed29 selects magnitude3 for the first control.
        op = ["add", list(T), list(S), q, 1]
        word = lower(op, baseline)
        positives[str(q)] = check_word(q, word, abs(q)+1)
        check_word(q, word[-1:]+word[:-1], abs(q)+1)  # Early clear is equivalent.
        need(lower(["add", list(T), list(S), 2*q, 2], baseline) == word, "reduced coefficient")
    good = lower(["add", list(T), list(S), 3, 1], baseline)
    cases = {
        "missing_clear": (good[:-1], 3, "endpoint or dirt"),
        "missing_repeat": (good[1:], 3, "endpoint or dirt"),
        "wrong_sign": ([("subtract", T, S)]+good[1:], 4, "endpoint or dirt"),
        "private_dirt_read": ([("add", T, W)]+good[1:], 4, "endpoint or dirt"),
        "clear_source": (good[:-1]+[("clear", S)], 4, "source mutation"),
        "restore_source_after_mutation": ([("double", S),("halve", S)]+good, 6, "source mutation"),
        "endpoint_neutral_grid_excursion": ([("halve", T),("double", T)]+good, 6, "fractional excursion"),
        "endpoint_neutral_growth": ([("double", T)]*3+[("halve", T)]*3+good, 10, "magnitude excursion"),
        "uncharged_clear": (good+[("clear", W)], 4, "unpaid instruction"),
    }
    rejected = {}
    for name, (word, cost, reason) in cases.items():
        try:
            check_word(3, word, cost)
        except ValueError as error:
            need(str(error) == reason, "wrong rejection reason: " + name + ": " + str(error))
            rejected[name] = str(error)
        else:
            raise ValueError("accepted negative control: " + name)
    invalid = {
        "source_target_alias": ["add", list(T), list(T), 3, 1],
        "work_alias": ["add", list(T), list(W), 3, 1],
        "zero": ["add", list(T), list(S), 0, 1],
        "nondyadic": ["add", list(T), list(S), 2, 3],
    }
    for name, op in invalid.items():
        try:
            lower(op, baseline)
        except ValueError:
            rejected[name] = "invalid macro rejected by retained PR696 validation"
        else:
            raise ValueError("accepted invalid macro: " + name)
    return {"positive_words": positives, "equivalent_early_clears": 4,
            "reduced_coefficient_positives": 4, "rejections": rejected}
