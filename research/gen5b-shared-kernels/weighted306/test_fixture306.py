"""One focused aggregate shared by this suite; historical suites are not run."""
from functools import lru_cache
@lru_cache(None)
def load_fixture():
 import context306 as c
 import verify306
 verify306.run(check=(c.HERE/'certificates/combined156.json').exists())
 return verify306.REVIEW_DATA
