def authenticate():
    for relative, pin in read(RETAINED / 'PINS.json').items():
        path = RETAINED / relative
        assert not path.is_symlink() and path.resolve().is_relative_to(RETAINED)
        assert digest(path.read_bytes()) == pin, relative
    assert digest((PEER / 'word.json.gz').read_bytes()) == 'aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527'
    pins = {
        'data/7605-WORD.json.gz': '37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d',
        'data/7605-NATIVE.json': '0ada1e2e7de8887e6ebbd16cda3c8b9738d71873857657ff4fa6e180653cf888',
        'data/7605-SIGNED.json': '0dda72ce4f1612ee6c8b6f4078b538f972d24b0108552d6ec50e545a1458cc16',
        'data/7605-FINAL.json': 'f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add',
        'data/edits7610.json': 'a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9',
    }
    assert all(digest((HERE / path).read_bytes()) == pin for path, pin in pins.items())
    spec = importlib.util.spec_from_file_location('helper757_build_control', HERE / 'build.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    old = read(HERE / 'data/7605-WORD.json.gz')
    assert build.build_word() == old
    edits = read(HERE / 'data/edits7610.json')
    tape = old['program']
    assert len(tape) == edits['base_events'] + 5 == 76636 and not edits['append']
    removed = {clock + 5: expected for clock, expected in edits['delete']}
    inserted = {clock + 5 if clock else 0: events for clock, events in edits['insert_before']}
    assert len(removed) == len(edits['delete']) and len(inserted) == len(edits['insert_before'])
    assert all(tape[clock] == expected for clock, expected in removed.items())
    program = [event for clock, old_event in enumerate(tape)
               for event in inserted.get(clock, []) + ([] if clock in removed else [old_event])]
    word = read(HERE / 'data/word.json.gz')
    assert word == {**old, 'program': program}
    assert digest(canonical(word)) == 'aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916'
    bill = build.invoice()
    bill['paid']['1'] -= 34
    bill['paid']['2'] += 17
    assert read(HERE / 'data/invoice-new.json') == bill
    return word


