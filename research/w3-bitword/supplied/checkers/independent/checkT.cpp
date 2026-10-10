// Independent check of a word: legality replay (exact mod-p subspaces), nondegeneracy of used frames,
// and exact formal F2 replay over ALL columns (x, y, every helper).
#include "sub.hpp"
int main(int argc,char**argv){
    string dir=argv[1], recf=argv[2];
    Store st; Snapshot sn; sn.load(st,dir,recf);
    int n=sn.n,v=sn.v; size_t NR=sn.rec.size();
    auto C=[&](int c){auto it=sn.cat2id.find(c); if(it==sn.cat2id.end()){fprintf(stderr,"unknown frame %d\n",c);exit(1);} return it->second;};
    int ZERO=C(sn.ZERO);
    vector<int> state(n+1,ZERO); for(int r=0;r<n;r++) state[r]=C(sn.init[r]);
    long bad=0; map<int,long> hist; long mass=0; bool copied=false; int center=-1; long copies=0;
    set<int> used; for(int r=0;r<n;r++){used.insert(state[r]); used.insert(C(sn.fin[r]));}
    for(size_t k=0;k<NR;k++){ auto&e=sn.rec[k];
        if(e.k==0){ int o=C(e.b), nw=C(e.c);
            if(state[e.a]!=o){ if(bad<5) fprintf(stderr,"MOVE old mismatch at %zu\n",k); bad++; }
            if(!st.contains(nw,o)){ if(bad<5) fprintf(stderr,"MOVE not nested at %zu\n",k); bad++; }
            if(st.dim(nw)-st.dim(o)!=e.f){ if(bad<5) fprintf(stderr,"MOVE rank mismatch at %zu\n",k); bad++; }
            if(e.f>0){hist[e.f]++; mass+=e.f;}
            state[e.a]=nw; used.insert(nw);
        } else if(e.k==1){ int f=C(e.f);
            if(state[e.a]!=f||state[e.b]!=f){ if(bad<5) fprintf(stderr,"ADD frame mismatch at %zu (a=%d b=%d)\n",k,e.a,e.b); bad++; }
            if(e.a==e.b){bad++;}
            if(copied && (e.a==center || e.a==n)){ if(bad<5) fprintf(stderr,"mutation in copy window %zu\n",k); bad++; }
            if((e.a==n||e.b==n)&&!copied){bad++;}
            used.insert(f);
        } else if(e.k==2){ int c=C(e.c);
            if(copied||e.b!=n||state[e.a]!=c||e.z!=st.dim(c)){ fprintf(stderr,"bad COPY %zu\n",k); bad++; }
            copied=true; center=e.a; state[n]=C(e.f); hist[e.z]++; mass+=e.z; copies++; used.insert(c);
        } else if(e.k==3){
            if(!copied||e.b!=n||e.a!=center||state[e.a]!=C(e.c)||state[n]!=C(e.f)){ fprintf(stderr,"bad ERASE %zu\n",k); bad++; }
            copied=false;
        } else {bad++;}
    }
    long badfin=0; for(int r=0;r<n;r++) if(state[r]!=C(sn.fin[r])) badfin++;
    long degen=0; for(int f:used) if(!st.nondeg(f)) degen++;
    fprintf(stderr,"legality: bad=%ld badfinal=%ld copies=%ld usedframes=%zu degenerate=%ld mass=%ld\n",bad,badfin,copies,used.size(),degen,mass);
    // formal F2 replay
    int WD=(n+63)/64; vector<u64> val((size_t)(n+1)*WD,0);
    auto row=[&](int r){return &val[(size_t)r*WD];};
    for(int r=0;r<n;r++) row(r)[r/64]|=1ULL<<(r%64);
    for(size_t k=0;k<NR;k++){ auto&e=sn.rec[k];
        if(e.k==1&&(e.c&1)){ u64*a=row(e.a),*b=row(e.b); for(int w=0;w<WD;w++) a[w]^=b[w]; }
        else if(e.k==2){ memcpy(row(n),row(e.a),WD*8); }
        else if(e.k==3){ memset(row(n),0,WD*8); }
    }
    long badx=0,bady=0,badh=0;
    for(int r=0;r<n;r++){ u64*p=row(r);
        for(int w=0;w<WD;w++){ u64 want=(w==r/64)?(1ULL<<(r%64)):0;
            if(r>=v&&r<2*v && w==(r-v)/64) want^=1ULL<<((r-v)%64);
            if(p[w]!=want){ if(r<v)badx++; else if(r<2*v)bady++; else badh++; break; } } }
    bool tempz=true; for(int w=0;w<WD;w++) if(row(n)[w]) tempz=false;
    fprintf(stderr,"formal F2 (all %d columns): x bad=%ld y bad=%ld helpers bad=%ld temp zero=%d\n",n,badx,bady,badh,(int)tempz);
    printf("{\"bad\":%ld,\"badfinal\":%ld,\"degenerate\":%ld,\"mass\":%ld,\"f2_bad\":%ld}\n",bad,badfin,degen,mass,badx+bady+badh);
}
