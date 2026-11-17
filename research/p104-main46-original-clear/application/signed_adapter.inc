def signed_adapter(root, word):
    expected = digest(canonical(word))
    patches = [
        ("old_word=read(FROZEN/'7481-WORD.json.gz')", "old_word=read(FROZEN/'7605-WORD.json.gz')"),
        ("new_word==read(FROZEN/'COMPOSED-WORD.json.gz'),'Pinned literal composite word'", "new_word==read(FROZEN/'CANDIDATE-WORD.json.gz'),'Pinned literal main46 word'"),
        ("=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'", f"=='{expected}'"),
        ("FROZEN/'7481-NATIVE.json'", "FROZEN/'7605-NATIVE.json'"),
        ('PASS_COMPOSED_7481_7542_COMPLETE_NATIVE', NATIVE_MARKER),
        ("=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'", "=='e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd'"),
        ("FROZEN/'7481-SIGNED.json'", "FROZEN/'7605-SIGNED.json'"),
        ("Q('0.003647081039689')", "Q('0.003650444244716')"),
        ("{1:-34,5:-17,7:17}", "{1:-34,2:17}"),
        ("==110485", "==110349"),
        ("Whole reconstructed #7481 invoice", "Whole reconstructed #7605 invoice"),
        ("  G=load('producer_signed_price_engine',bundle/'gate.py')", """  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')
  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']
  G=load('producer_signed_price_engine',bundle/'gate.py')"""),
        ("Strictly higher than #7481 raw crossing", "Strictly higher than #7605 raw crossing"),
        ("  assert Q(gate['claim'])>Q('0.0036475398278'),'Strictly higher than upper endpoint of #7542 price enclosure'",
         f"  assert Q(gate['claim'])>=Q('{PUBLIC_CLAIM}'),'Conservative public claim is within the proved application'"),
        ("Exact #7481 invoice rejects the new signed claim", "Exact #7605 invoice rejects the new signed claim"),
        ("  price_record=normal(dict(before=before,after=after,gate=gate,price=price,", f"""  public_claim=Q('{PUBLIC_CLAIM}')
  assert public_claim>Q(previous['gate']['raw_bracket'][1])
  assert directed.moment(G.signed(before),public_claim)[1]<0
  public_gate=directed.gate(after,public_claim,public_claim+Q(7,10**14),*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))
  price_record=normal(dict(public_claim_gate=public_gate,before=before,after=after,gate=gate,price=price,"""),
        ('PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION', SIGNED_MARKER),
        ("source_head='89eaa9d8cae37c1540de98f2d29a3abaabb96a2b'", "source_head='e1d2756eecf03e146338239fee81772a99ba8d4c'"),
        ("component_head='71f5acb0409daf208a865482f3349049dbd3251c'", "component_head='93fded4340bb08bc1f99d6f18e47a198456a41df'"),
    ]
    return adapt(RETAINED / 'engines/7544-signed.py', patches, root / 'producer54/validation_signed/run.py')


