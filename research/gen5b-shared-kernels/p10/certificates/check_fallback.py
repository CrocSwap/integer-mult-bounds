"""Reuse exact chart and bank verifiers for the fixed15 fallback."""
from check_candidate_charts import run as charts,support
from check_role_banks import run as banks
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 charts(bridge_path=support.OUTPUT/'bridge15/bridge-result.json',case='15')
 banks(case='15')
