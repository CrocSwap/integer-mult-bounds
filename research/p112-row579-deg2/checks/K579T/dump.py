from base import *
from collections import Counter
import sys
cls=sys.argv[1]; ch=chain(cls); X=xvals(ch)
c=[8-Counter(X[t]).most_common(1)[0][1] for t in range(120)]
print(' '.join(map(str,lab))); print(' '.join(map(str,c)))
