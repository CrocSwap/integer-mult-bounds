"""Faithful regular replay from integer quaternion units, without primary imports."""
import hashlib


def require(ok, message):
    if not ok:
        raise ValueError(message)


def quaternion(a, b):
    w,x,y,z = a
    W,X,Y,Z = b
    return (w*W-x*X-y*Y-z*Z, w*X+x*W+y*Z-z*Y,
            w*Y-x*Z+y*W+z*X, w*Z+x*Y-y*X+z*W)


def check(fixtures):
    positive = [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]
    elements = positive + [tuple(-x for x in row) for row in positive]
    multiply = [[elements.index(quaternion(a,b)) for b in elements] for a in elements]
    transcript = hashlib.sha256()
    columns = 0
    for fixture in fixtures:
        targets, word = fixture['targets'], fixture['word']
        r = len(targets)
        size = 8*r
        # Columns of the full F2-linear operator on every dirty input address.
        state = [1 << j for j in range(size)]
        for g,u,v in word:
            require(g in (1,2) and (u & v).bit_count() % 2 == 1, 'independent legal factor')
            new = list(state)
            for role in range(r):
                if not (v >> role & 1):
                    continue
                for address in range(8):
                    delta = 0
                    for source in range(r):
                        if u >> source & 1:
                            delta ^= state[8*source+address] ^ state[8*source+multiply[g][address]]
                    new[8*role+address] ^= delta
            state = new
        expected = [1 << (8*role+multiply[target][address]) for role,target in enumerate(targets) for address in range(8)]
        require(state == expected, 'faithful regular dirty endpoint')
        # Independent bill from target multiplicities, with the cheaper square.
        left,right = fixture['prices']
        cost = sum(left if g==1 else right for g,_,_ in word)
        bound = sum(0 if g==0 else left if g==1 else right if g==2 else 2*min(left,right) for g in targets)
        require(cost >= bound and (not fixture['attaining'] or cost==bound), 'independent tariff')
        width = (size+7)//8
        for column in state:
            transcript.update(column.to_bytes(width,'little'))
        columns += size
    return {'fixtures':len(fixtures), 'regular_columns':columns, 'regular_sha256':transcript.hexdigest(),
            'method':'Integer quaternion multiplication and full faithful F2 regular columns; no primary imports'}
