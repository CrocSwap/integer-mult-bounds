import sys
sys.path.insert(0,'../intcaller')
import ic1
from ic1 import val,partitions
k=13
need=ic1.BAR*k/104
print('need sum val >',need)
print('pure',val(2,(2,)),'chord',val(2,(1,1)))
hubs=[(P,val(13,P)) for P in partitions(13,11)]
Rs=[(P,val(6,P)) for P in partitions(6,11)]
hubs.sort(key=lambda x:-x[1])
print(hubs[:5],hubs[-3:])
print(Rs)
