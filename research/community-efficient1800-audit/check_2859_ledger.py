import ast,hashlib,json,pathlib
R=pathlib.Path('/tmp/pr-efficient1800/combined-2859');P=pathlib.Path('/tmp/pr-efficient1800')
p=R/'scripts/verify_pr_reconciliation.py';raw=p.read_bytes();tree=ast.parse(raw)
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
stop=next(i for i,x in enumerate(main.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='package' for t in x.targets))
assert ast.unparse(main.body[stop]).endswith("'research/coordinated-frames-and-entrance-banks'"),ast.unparse(main.body[stop])
main.body=main.body[:stop]
ns={'__file__':str(p),'__name__':'scoped_ledger_check'}
exec(compile(tree,str(p),'exec'),ns);ns['main']()
d=json.load(open(R/'docs/research/pr-ledger.json'))
result={'status':'PASS','records':len(d['pull_requests']),'verifier_sha256':hashlib.sha256(raw).hexdigest(),'ledger_sha256':hashlib.sha256((R/'docs/research/pr-ledger.json').read_bytes()).hexdigest(),'scope':'Execute unchanged ledger-validation prefix: immutable starting inventory, complete family decisions, exact head/attribution/disposition/remaining-question checks and every ledger source hash. Historical archived-package replays after this boundary are outside this incremental check.'}
(P/'provenance-2859-ledger-prefix.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
