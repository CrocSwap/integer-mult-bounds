import pickle,sys
from ls import optimize
from check import check
import ls2
W2=pickle.load(open(sys.argv[1],'rb'))
W3=optimize(W2,passes=10)
print(check(W3,'post-LS1'))
W4=ls2.run(W3,rounds=5)
print(check(W4,'post-LS2'))
pickle.dump(W4,open(sys.argv[2],'wb'))
