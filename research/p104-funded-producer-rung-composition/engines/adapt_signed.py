"""Retarget the authenticated #7481 signed verifier to the literal #7542 composition."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json

OLD_SOURCE = "af1ec8e27b39fdcfe8c1c5ec3eae14c1124c62b5cdcf3c1218482b6291c6ceef"
PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-NATIVE.json": "4f2024c0a84be0389a2f0469a0ea3f27af995b17fa641211c94a34807b8624f9",
    "7481-SIGNED.json": "e5c8d8c0cf4d3f3fc60ffe70eb084cf6c9eadf8e646c74b48762501bf5367474",
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
}
COMPOSED = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
INCUMBENT = "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b"
PEER = "71f5acb0409daf208a865482f3349049dbd3251c"


def digest(value):
    return sha256(value).hexdigest()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="isolated staging directory containing frozen-composition")
    parser.add_argument("source", type=Path, help="unchanged #7481 signed run.py")
    parser.add_argument("output", type=Path, help="new adapted run.py; must not exist")
    args = parser.parse_args()

    frozen = args.root / "frozen-composition"
    for path, expected in PINS.items():
        assert digest((frozen / path).read_bytes()) == expected, path
    splice = json.loads((frozen / "COMPOSITION.json").read_text())
    assert splice["canonical_sha256"] == COMPOSED
    assert splice["heads"]["7481"] == INCUMBENT and splice["heads"]["7542"] == PEER
    assert splice["paid_delta_signed"] == {"1": -34, "5": -17, "7": 17}

    source = args.source.read_bytes()
    assert digest(source) == OLD_SOURCE
    text = source.decode()
    patches = (
        ("old_word=read(SOURCE/'WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')",
         """FROZEN=ROOT/'frozen-composition'
old_word=read(FROZEN/'7481-WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')
assert new_word==read(FROZEN/'COMPOSED-WORD.json.gz'),'Pinned literal composite word'
assert sha256(canonical(new_word)).hexdigest()=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'
assert {k:v for k,v in old_word.items()if k!='program'}=={k:v for k,v in new_word.items()if k!='program'},'Exact native interface metadata'"""),
        ("old_result=read(SOURCE/'NATIVE-RESULT.json');new_result=read(NATIVE)",
         """old_result=read(FROZEN/'7481-NATIVE.json');new_result=read(NATIVE)
assert new_result['status']=='PASS_COMPOSED_7481_7542_COMPLETE_NATIVE'
assert old_result['word_canonical_sha256']=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'"""),
        ("previous=read(SOURCE/'RESULT.json')['price']",
         """previous=read(FROZEN/'7481-SIGNED.json')['price']
  assert Q(previous['gate']['claim'])==Q('0.003647081039689')
  ranks=set(before['P'])|set(after['P'])
  delta={r:after['P'].get(r,0)-before['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=before['P'].get(r,0)}
  assert delta=={1:-34,5:-17,7:17} and after['T']==before['T']
  assert before['S']==after['S']==1424 and not before['empty_root_credits'] and not after['empty_root_credits']
  assert sum(after['P'].values())==110485 and sum(after['T'].values())==22461"""),
        ("Whole reconstructed #7480 invoice", "Whole reconstructed #7481 invoice"),
        ("assert Q(gate['claim'])>Q('0.003646777872835')",
         """assert Q(gate['claim'])>Q(previous['gate']['raw_bracket'][1]),'Strictly higher than #7481 raw crossing'
  assert Q(gate['claim'])>Q('0.0036475398278'),'Strictly higher than upper endpoint of #7542 price enclosure'"""),
        ("directed=G.module('producer_native_comparator',vendor/'interval_gate.py')",
         """directed=G.module('producer_native_comparator',vendor/'interval_gate.py')
  assert directed.moment(G.signed(before),Q(gate['claim']))[1]<0,'Exact #7481 invoice rejects the new signed claim'"""),
        ("    native_baseline_rejects_new_claim=True,old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))",
         """    native_baseline_rejects_new_claim=True,signed_incumbent_rejects_new_claim=True,
    old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))"""),
        ("PASS_CHANGED_485_1455_PRODUCER_COMPLETE_SIGNED_APPLICATION",
         "PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION"),
        ("source_head='58a9d052143f5d85295ed2d0163591c47f89a331',timings=log",
         """source_head='89eaa9d8cae37c1540de98f2d29a3abaabb96a2b',
    component_head='71f5acb0409daf208a865482f3349049dbd3251c',timings=log"""),
    )
    for original, replacement in patches:
        assert text.count(original) == 1, original
        text = text.replace(original, replacement)
    compile(text, str(args.output), "exec")
    with args.output.open("x") as dst:
        dst.write(text)
    print(json.dumps({
        "source_sha256": digest(source),
        "adapted_sha256": digest(text.encode()),
        "immutable_pins": PINS,
        "replacements": [{"source": old, "adapted": new, "count": 1} for old, new in patches],
    }, indent=2))


if __name__ == "__main__":
    assert __debug__
    main()
