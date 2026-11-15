import sys, pickle, jl, pricekit as pk; import scan3 as scan2
W=pk.load(sys.argv[1]); M=jl.Word(W); allr=[]
for r in range(M.n): allr+=scan2.scan_main(M,r)
allr.sort(key=lambda r:r['d']); print('all-public candidates',len(allr))
for r in allr[:20]: print(r['m'],'main' if r['m'] in M.mains else 'helper','G',r['G'],'P/X/N',r['P'],r['X'],r['N'],'d %.4f slid %d units %s'%(r['d'],r['slid'],r['units']))
pickle.dump(allr,open(sys.argv[2],'wb'))
