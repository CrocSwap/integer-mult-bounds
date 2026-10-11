// Verifier: legality replay (exact-mod-p containment), nondegeneracy of used frames, formal F2 simulation.
// Usage: verify <dir> [residual_out]
#include "sub.hpp"
int main(int argc,char**argv){
    string dir=argv[1];
    Store st; Snapshot sn; sn.load(st,dir,dir+"/249-records.bin");
    int n=sn.n, v=sn.v; size_t NR=sn.rec.size();
    fprintf(stderr,"[load] frames=%zu records=%zu\n",st.S.size(),NR);
    auto C=[&](int c){ auto it=sn.cat2id.find(c); if(it==sn.cat2id.end()){fprintf(stderr,"unknown frame %d\n",c); exit(3);} return it->second; };
    int ZERO=C(sn.ZERO), FULLf=C(sn.FULL);
    vector<int> state(n+1); for(int r=0;r<n;r++) state[r]=C(sn.init[r]); state[n]=ZERO;
    long bad=0; bool copied=false; int copySource=-1; long copies=0, erases=0;
    set<int> used;
    for(size_t k=0;k<NR;k++){ auto&e=sn.rec[k];
        if(e.k==0){
            int o=C(e.b), nw=C(e.c);
            if(state[e.a]!=o){ if(bad<20) fprintf(stderr,"MOVE state mismatch k=%zu role=%d state=%d old=%d\n",k,e.a,state[e.a],o); bad++; }
            if(!st.contains(nw,o)){ if(bad<20) fprintf(stderr,"MOVE not nested k=%zu role=%d\n",k,e.a); bad++; }
            if(st.dim(nw)-st.dim(o)!=e.f){ if(bad<20) fprintf(stderr,"MOVE rank k=%zu role=%d %d vs %d\n",k,e.a,st.dim(nw)-st.dim(o),e.f); bad++; }
            state[e.a]=nw; used.insert(nw);
        } else if(e.k==1){
            int f=C(e.f);
            if(state[e.a]!=f||state[e.b]!=f){ if(bad<20) fprintf(stderr,"ADD frame mismatch k=%zu a=%d(%d) b=%d(%d) f=%d\n",k,e.a,state[e.a],e.b,state[e.b],f); bad++; }
            if(e.a==e.b){ bad++; }
            if(copied&&(e.a==copySource||e.a==n)){ bad++; fprintf(stderr,"mutate in copy window k=%zu\n",k);}
            used.insert(f);
        } else if(e.k==2){ if(copied||e.b!=n||state[e.a]!=C(e.c)) {bad++; fprintf(stderr,"COPY bad k=%zu\n",k);} copied=true; copySource=e.a; state[n]=C(e.f); copies++; }
        else if(e.k==3){ if(!copied||e.a!=copySource||state[e.a]!=C(e.c)||state[n]!=C(e.f)) {bad++; fprintf(stderr,"ERASE bad k=%zu\n",k);} copied=false; erases++; }
    }
    long badfinal=0;
    for(int r=0;r<n;r++) if(state[r]!=C(sn.fin[r])){ if(badfinal<10) fprintf(stderr,"final mismatch role %d\n",r); badfinal++; }
    long degen=0; for(int f:used) if(!st.nondeg(f)) degen++;
    fprintf(stderr,"[legality] violations=%ld final_mismatch=%ld copies=%ld erases=%ld used_frames=%zu degenerate=%ld\n",bad,badfinal,copies,erases,used.size(),degen);
    // formal F2 simulation
    int WD=(n+63)/64;
    vector<u64> val((size_t)(n+1)*WD,0);
    auto row=[&](int r){return &val[(size_t)r*WD];};
    for(int r=0;r<n;r++) row(r)[r/64]|=1ULL<<(r%64);
    for(size_t k=0;k<NR;k++){ auto&e=sn.rec[k];
        if(e.k==1 && (e.c&1)){ u64*pa=row(e.a); u64*pb=row(e.b); for(int w=0;w<WD;w++) pa[w]^=pb[w]; }
        else if(e.k==2){ u64*pa=row(e.a); u64*pt=row(n); for(int w=0;w<WD;w++) pt[w]=pa[w]; }
        else if(e.k==3){ u64*pt=row(n); for(int w=0;w<WD;w++) pt[w]=0; }
    }
    long badX=0,badH=0,badY=0, resid_s0=0, resid_other=0;
    vector<int> sig(n); for(int r=0;r<n;r++) sig[r]=st.dim(C(sn.init[r]));
    FILE*fo= argc>2? fopen(argv[2],"w"):nullptr;
    for(int r=0;r<n;r++){
        u64*p=row(r);
        if(r<v || r>=2*v){
            bool ok=true; for(int w=0;w<WD;w++){ u64 ex=(w==r/64)?(1ULL<<(r%64)):0; if(p[w]!=ex){ok=false;break;} }
            if(!ok){ if(r<v) badX++; else { if(sig[r]<H) badH++; } }
        } else {
            int t=r-v; 
            for(int w=0;w<WD;w++){ u64 ex=0; if(w==t/64) ex|=1ULL<<(t%64); if(w==r/64) ex|=1ULL<<(r%64);
                u64 d=p[w]^ex; while(d){ int b=__builtin_ctzll(d); d&=d-1; int q=w*64+b;
                    if(q>=2*v && q<n && sig[q]==0){ resid_s0++; if(fo) fprintf(fo,"%d %d\n",t,q);} else { resid_other++; if(resid_other<10) fprintf(stderr,"bad residual target %d var %d (sig %d)\n",t,q,q<n?sig[q]:-1);} } }
        }
    }
    if(fo) fclose(fo);
    fprintf(stderr,"[F2] X_not_restored=%ld H_not_restored=%ld resid_sigma0=%ld resid_other=%ld\n",badX,badH,resid_s0,resid_other);
    return 0;
}
