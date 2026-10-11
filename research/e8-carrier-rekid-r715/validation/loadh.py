import pickle,sys
class Stub:
    def __setstate__(self,s): self.__dict__.update(s)
class U(pickle.Unpickler):
    def find_class(self,mod,name):
        if name=='SH': return Stub
        return super().find_class(mod,name)
def loadh(p): return U(open(p,'rb')).load()
if __name__=='__main__':
    h=loadh(sys.argv[1]); print(type(h),list(h.__dict__.keys()))
    for k,v in h.__dict__.items():
        print(k,type(v),len(v) if hasattr(v,'__len__') else v)
    print(h.content[130], h.frame[130], h.dim[130], h.kids[130], h.need[3])
