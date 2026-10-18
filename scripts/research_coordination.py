#!/usr/bin/env python3
"""Optional advisory board metadata. Reads existing overlap caches; never posts."""
from datetime import datetime, timezone
import json
import re

SCHEMA = 'integer-mult-coordination/v1'
HANDOFF_URL = 'https://github.com/CrocSwap/integer-mult-bounds/discussions/1166'
KINDS = {'CLAIM', 'HANDOFF', 'FINDING', 'DONE', 'RELEASED'}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a string')
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('timestamps need a UTC offset')
    return date


def validate_message(value):
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('unsupported coordination schema')
    if value.get('kind') not in KINDS:
        raise ValueError('unknown coordination kind')
    for key in ('task', 'scope', 'base'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError('missing coordination field: ' + key)
    if not re.fullmatch(r'[0-9a-f]{40}', value['base']):
        raise ValueError('base must be an exact Git commit')
    expiry = value.get('expiry')
    if value['kind'] == 'CLAIM' and not expiry:
        raise ValueError('CLAIM needs an expiry')
    if expiry is not None:
        timestamp(expiry)
    artifact = value.get('artifact')
    if artifact is not None and (not isinstance(artifact, str) or not artifact.startswith('https://')):
        raise ValueError('artifact must be a public HTTPS URL or null')
    return value


def messages(body):
    result, warnings = [], []
    for block in re.findall(r'^```json\s*\n(.*?)^```\s*$', body, re.M | re.S):
        if SCHEMA not in block:
            continue
        try:
            if len(block) > 16384:
                raise ValueError('coordination block exceeds 16 KiB')
            result.append(validate_message(json.loads(block)))
        except (ValueError, TypeError, AttributeError) as exc:
            warnings.append(str(exc))
    if len(result) > 1:
        return [], warnings + ['multiple coordination blocks in one post; edit one canonical block']
    return result, warnings


def board_view(snapshot, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1 or snapshot.get('repository') != 'CrocSwap/integer-mult-bounds':
        raise ValueError('not a canonical overlap cache')
    source = snapshot.get('sources', {}).get('discussions', {})
    warnings = []
    try:
        age = (now - timestamp(source['fetched_at'])).total_seconds()
        fresh = 0 <= age <= 900 and source.get('complete_pagination') is True
    except (KeyError, ValueError, TypeError, AttributeError):
        fresh = False
    if not fresh:
        warnings.append('Discussion snapshot is missing, incomplete or older than 15 minutes; check live threads.')
    rows = []
    for record in source.get('records', []):
        values, errors = messages(record.get('body', ''))
        warnings.extend(record.get('url', '?') + ': ' + error for error in errors)
        for value in values:
            row = dict(value, url=record.get('url'), updated_at=record.get('updated_at'))
            row['claim_unexpired'] = value['kind'] == 'CLAIM' and timestamp(value['expiry']) > now
            rows.append(row)
    return {'handoff_url': HANDOFF_URL, 'snapshot_fresh': fresh,
            'fetched_at': source.get('fetched_at'), 'warnings': warnings,
            'open_handoffs': [r for r in rows if r['kind'] == 'HANDOFF'],
            'claims': [r for r in rows if r['kind'] == 'CLAIM'],
            'scope': 'Advisory leads only. No reservation, review status or automatic task exclusion. Unstructured posts remain relevant.'}
