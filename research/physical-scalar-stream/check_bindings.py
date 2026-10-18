"""Recompile literal source templates without repeating the capacity audit."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import scalar_sources
from literal_templates import TEMPLATES,POLICIES


def need(condition,message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":")).encode()


def run():
    need(not any(name in sys.modules for name in ("replay_parent","contractions","frames","tariff","words")),
         "cold provider binding namespace")
    package = scalar_sources.exports()["pr3090"]
    records = json.loads((package/"VENDOR.json").read_text())["files"]
    for row in records:
        need(sha256((package/row["path"]).read_bytes()).hexdigest() == row["sha256"], "frozen coefficient provider bytes")
    lower = scalar_sources.module("binding_lower",package/"vendor/lowering/lower.py")
    sys.path.insert(0,str(package/"vendor/native/vendor/parent"))
    import replay_parent as parent
    from contractions import produce
    from tariff import produce as tariff_parent
    parent.check_pins()
    expected = json.loads((package/"RESULT.json").read_text())
    inherited = json.loads((package/"vendor/native/RESULT.json").read_text())
    union,results = set(),{}
    with tempfile.TemporaryDirectory(prefix="scalar-source-binding-") as directory:
        for provider in ("base","extra"):
            raw = parent.read(package/f"vendor/native/vendor/parent/vendor/WORD-{provider}.json.gz")
            word = produce(tariff_parent(raw),parent.read(package/"vendor/native/vendor/parent/EDITS.json"))
            programs,checks = parent.compile_word(word,Path(directory)/provider)
            need(checks == inherited["providers"][provider]["native_checks"], "inherited complete compiler binding")
            need(sha256(canonical(word)).hexdigest() == expected["providers"][provider]["word_sha256"], "produced provider word binding")
            for direction,events in programs.items():
                counts,templates = Counter(),{}
                digests = {policy:sha256() for policy in POLICIES}
                totals = {policy:dict(instructions=0,source_writes=0,scratch_macros=0,maximum_length=0) for policy in POLICIES}
                active,cut = False,None
                for index,event in enumerate(events):
                    if event[0] == "phase":
                        if event[1] == "A":
                            active = True
                        elif active:
                            need(event[1] == "centers", "complete prelude/A binding endpoint")
                            cut = index
                            break
                        continue
                    if event[0] != "scalar":
                        continue
                    gate = event[1]
                    key = (gate[0],*gate[-2:])
                    need(key[0] in ("add","scale"), "literal prelude/A scalar kind")
                    counts[key] += 1
                    if key not in templates:
                        templates[key] = {policy:lower.certify(*key,policy=policy) for policy in POLICIES}
                    for policy,recipe in templates[key].items():
                        row = totals[policy]
                        row["instructions"] += len(recipe)
                        row["source_writes"] += sum(op[1] == 1 for op in recipe)
                        row["scratch_macros"] += int(any(op[1] == 2 for op in recipe))
                        row["maximum_length"] = max(row["maximum_length"],len(recipe))
                        digests[policy].update(canonical([index,recipe]))
                need(cut == 11743 and sum(counts.values()) == 9992 and len(templates) == 29,
                     "actual complete literal macro inventory")
                expected_stream = expected["providers"][provider]["streams"][direction]
                for policy,row in totals.items():
                    prior = expected_stream["policies"][policy]
                    need((row["instructions"],row["source_writes"],row["scratch_macros"],digests[policy].hexdigest()) ==
                         (prior["single_component_instructions"],prior["source_writes"],prior["scratch_macros"],prior["recipe_sha256"]),
                         "literal policy counts and recipe hashes match source receipt")
                union.update(templates)
                inventory = [[*key,count] for key,count in sorted(counts.items())]
                results[provider+"/"+direction] = dict(events=len(events),stop=cut,macros=sum(counts.values()),
                    templates=len(templates),inventory_sha256=sha256(canonical(inventory)).hexdigest(),
                    program_sha256=sha256(canonical(events)).hexdigest(),
                    policies={policy:dict(**totals[policy],sha256=digests[policy].hexdigest()) for policy in POLICIES},
                    first_nonunit=events[109:111])
    need(tuple(sorted(union)) == TEMPLATES, "complete literal template union including denominator spellings")
    return dict(streams=results,union=len(union),union_sha256=sha256(canonical(sorted(union))).hexdigest(),
                scope="Bounded source compilation and literal template binding only; no new normalized-row/capacity/frame audit or physical full-caller claim")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_SCALAR_SOURCE_BINDINGS")
