"""Emit bounded-depth list declarations without changing public chunk boundaries."""


def flat_list(name, element_type, entries, block_size=16):
    """Named cons suffixes reduce elaborator stack use; their contents are literal."""
    assert entries and block_size > 0
    blocks = [entries[i:i + block_size] for i in range(0, len(entries), block_size)]
    lines = []
    for i in reversed(range(len(blocks))):
        tail = '[]' if i + 1 == len(blocks) else f'{name}_tail{i + 1}'
        body = ' ::\n  '.join([*blocks[i], tail])
        declaration = name if i == 0 else f'{name}_tail{i}'
        lines.append(f'def {declaration} : List {element_type} :=\n  {body}')
    return lines


def split_nodes(out, prefix, first_import, namespace, declarations, block_size=1000):
    """Keep each declaration intact, distributing sequential nodes across modules."""
    assert declarations and block_size > 0
    previous = first_import
    for i, start in enumerate(range(0, len(declarations), block_size)):
        module = f'{prefix}{i:02d}'
        text = [f'import {previous}', 'set_option maxRecDepth 100000',
                'set_option maxHeartbeats 0', f'namespace {namespace}',
                'open TreeReplay (Tree)', *declarations[start:start + block_size],
                f'end {namespace}']
        (out / (module + '.lean')).write_text('\n'.join(text) + '\n')
        previous = module
    return previous
