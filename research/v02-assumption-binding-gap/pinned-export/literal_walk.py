# SPDX-License-Identifier: Apache-2.0
# Exact pure function retained from the V02 observer. See SOURCE_MAP.json.

def literal_walk(path, graph):
    """Resolve each component in order; a missing ancestor wins over later '..'."""
    if not isinstance(path, str) or not path.startswith('/'):
        raise ValueError('absolute literal path required')
    pending = path.split('/')[1:]
    parts = []
    links = 0
    while pending:
        item = pending.pop(0)
        if item in ('', '.'):
            continue
        if item == '..':
            if parts:
                parts.pop()
            continue
        named = '/' + '/'.join(parts + [item])
        row = graph.get(named)
        if row is None:
            return {'first_missing': named}
        if row['kind'] == 'symlink':
            links += 1
            if links > 40:
                raise ValueError('symlink loop')
            target = row['link']
            if target.startswith('/'):
                parts = []
            pending = target.split('/') + pending
            continue
        if pending and row['kind'] != 'directory':
            return {'not_directory': named}
        parts.append(item)
    return {'resolved': '/' + '/'.join(parts)}
