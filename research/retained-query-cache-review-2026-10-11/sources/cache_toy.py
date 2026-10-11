"""Three independent scalar columns; no frame/physical supplier admission."""
import json

def replay(column, omit=None):
    dirt, old_source, correction = column
    cached = dirt + old_source
    changed_source = old_source + correction
    delivered = cached
    if omit != 'subtract_changed_source':
        cached -= changed_source
    if omit != 'add_correction':
        cached += correction
    return cached, delivered

basis = [(1,0,0),(0,1,0),(0,0,1)]
for col in basis:
    restored, delivered = replay(col)
    assert restored == col[0] and delivered == col[0] + col[1]
for omission in ['subtract_changed_source', 'add_correction']:
    assert any(replay(col, omission)[0] != col[0] for col in basis)
print(json.dumps({'status':'PASS_SCALAR_CACHE_TOY', 'columns':3, 'omission_controls':2,
                  'scope':'Scalar saved-value and dirty restoration algebra only; exact frame availability, target dirt cancellation and full chronological inverse remain required.'}))
