"""A one-axis under-return must fail during an actual dirty typed fixture."""
from pathlib import Path
import runpy,sys
root=Path(__file__).resolve().parent
runtime=Path(sys.argv[1]).resolve();sys.path.insert(0,str(runtime))
from typed_transport import TypedPlan

class UnderReturn(TypedPlan):
    damaged=False
    def send_prefix(self,*args,**kwargs):
        width=super().send_prefix(*args,**kwargs)
        if width>1 and not UnderReturn.damaged:
            UnderReturn.damaged=True
            return width-1
        return width

source=root/'successor/peer/research/frequency-weighted-native-multiplier/check_calendar.py'
check=runpy.run_path(str(source))['run']
check.__globals__['TypedPlan']=UnderReturn
try:
    check()
except (AssertionError,ValueError,ArithmeticError,IndexError) as error:
    assert UnderReturn.damaged
    print('PASS_CORRUPTED_ONE_AXIS_PREFIX_REJECTED',type(error).__name__)
else:
    raise AssertionError('The one-axis under-return escaped its real dirty caller')
