import pickle
cand=pickle.load(open('cand.pkl','rb')); S=[27,1,14,4,11,17,10,8]
pickle.dump([cand[i] for i in S],open('kd.pkl','wb'))
