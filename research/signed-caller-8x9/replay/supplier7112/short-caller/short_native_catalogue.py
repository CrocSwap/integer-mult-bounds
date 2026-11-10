from pathlib import Path
import gzip, hashlib, json, sys
root=Path(__file__).resolve().parent
path=root/"upstream_native_catalogue.py"
code=path.read_text()
start=code.index("    pins=json.loads",code.index("def module("))
end=code.index("    spec=",start)
code=code[:start]+'''    need(sha256(path.read_bytes()).hexdigest()==engine_pins[relative],'engine source hash')
'''+code[end:]
start=code.index("    raw=(PACKAGE/'data/final.json.gz')")
end=code.index("    main_fields",start)
code=code[:start]+'''    raw=(HERE.parent/'WORD.json.gz').read_bytes()
    word=json.loads(gzip.decompress(raw))
    need(sha256(json.dumps(word,sort_keys=True,separators=(',', ':')).encode()).hexdigest()==expected_word,'canonical word hash')
'''+code[end:]
code=code.replace("ROOT=HERE.parents[3]\nPACKAGE=ROOT/'research/shared-wire-split-composition'","PACKAGE=HERE/'admission-source'")
r=json.loads((root.parent/"RESULT.json").read_text())
expected=r["word_canonical_sha256"]
engine_pins={"frozen/clifford_exact.py":"2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
             "frozen/native_verify.py":"3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38"}
if sys.argv[1:]==["--size"]:
 w=json.loads(gzip.decompress((root.parent/"WORD.json.gz").read_bytes()))
 m=set(w['live'])|{x+112 for x in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
 print(len({(e[2],e[3]) for e in w['program'] if e[0]=='MOVE'} |
           {(w['initial'][r],w['final'][r]) for r in range(w['public']) if r not in m}))
else:
 exec(compile(code,str(path),"exec"),dict(globals(),__file__=str(path),expected_word=expected))
