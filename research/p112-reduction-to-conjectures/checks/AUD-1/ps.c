// AUD-1 Lemma PS / PS+1 independent check. ./ps base.txt ps.in
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
typedef unsigned __int128 u128;
int lab[120],N,NR,rep[64],NC; u128 *M,*CM; int cnv[8000]; double cv[8000][2][8];
static int pc(u128 x){ return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64)); }
static int rk(u128 s){ int b[9]={0}; int r=0; for(int t=0;t<120;t++) if((s>>t)&1){ int v=lab[t]; for(int k=8;k>=0;k--) if((v>>k)&1){ if(!b[k]){b[k]=v;r++;break;} v^=b[k]; } } return r; }
static int rrank(int *ids,int n,int extra_l0,u128 *coset){ // real rank of vectors of candidate ids
  double B[8][8]; int r=0;
  for(int q=0;q<n;q++){ int c=ids[q]; for(int k=0;k<cnv[c];k++){ double v[8]; memcpy(v,cv[c][k],sizeof v);
      for(int i=0;i<r;i++){ int p=0; while(fabs(B[i][p])<1e-9) p++; double f=v[p]/B[i][p]; for(int j=0;j<8;j++) v[j]-=f*B[i][j]; }
      double mx=0; for(int j=0;j<8;j++) if(fabs(v[j])>mx) mx=fabs(v[j]); if(mx>1e-6){ memcpy(B[r],v,sizeof v); r++; if(r==8) return 8; } } }
  return r; }
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); for(int t=0;t<120;t++) fscanf(f,"%d",&lab[t]); fscanf(f,"%d",&N); M=malloc(N*sizeof(u128));
  for(int i=0;i<N;i++){ unsigned long long a,b; fscanf(f,"%llu %llu",&a,&b); M[i]=((u128)b<<64)|a; } fclose(f);
  f=fopen(argv[2],"r"); fscanf(f,"%d",&NR); for(int i=0;i<NR;i++) fscanf(f,"%d",&rep[i]); fscanf(f,"%d",&NC); CM=malloc(NC*sizeof(u128));
  for(int c=0;c<NC;c++){ unsigned long long a,b; fscanf(f,"%llu %llu %d",&a,&b,&cnv[c]); CM[c]=((u128)b<<64)|a; for(int k=0;k<cnv[c];k++) for(int j=0;j<8;j++) fscanf(f,"%lf",&cv[c][k][j]); }
  int cap7=0; for(int i=0;i<N;i++) if(pc(M[i])>cap7) cap7=pc(M[i]);
  long hist[9]={0},histp[9]={0}; int *q0=malloc(NC*sizeof(int)), *qq=malloc(NC*sizeof(int)); static u128 l0set[8000];
  int r0=argc>3?atoi(argv[3]):0, r1=argc>4?atoi(argv[4]):NR; for(int ri=r0;ri<r1;ri++){ int a=rep[ri]; u128 A=M[a]; int n7=0,n8p=0,self7=-1,self8p=-1; printf("rep %d |A|=%d:",a,pc(A));
    for(int b=0;b<N;b++){ u128 U=A|M[b]; int n0=0,nl=0;
      for(int c=0;c<NC;c++){ u128 l=CM[c]&~U; int s=pc(l); if(s>cap7+1) continue; int r=rk(l);
        if(r<=7){ q0[n0++]=c; continue; }
        if(r==8){ u128 ls=0; for(int t=0;t<120;t++) if((l>>t)&1) if(rk(l&~(((u128)1)<<t))<=7) ls|=((u128)1)<<t; if(ls){ l0set[nl]=ls; qq[nl++]=c; } } }
      int Q=rrank(q0,n0,0,0); hist[Q]++;
      int Qp=Q; if(nl){ static int all[16000]; memcpy(all,q0,n0*sizeof(int)); memcpy(all+n0,qq,nl*sizeof(int)); if(rrank(all,n0+nl,0,0)<8) nl=0; } if(nl){ for(int t=0;t<120;t++){ int m=n0; static int tmp[16000]; memcpy(tmp,q0,n0*sizeof(int)); for(int k=0;k<nl;k++) if((l0set[k]>>t)&1) tmp[m++]=qq[k]; if(m>n0){ int z=rrank(tmp,m,0,0); if(z>Qp) Qp=z; } } }
      histp[Qp]++;
      if(Q>=7){ n7++; printf(" B%d(Q%d,|AB|%d)",b,Q,pc(A&M[b])); if(b==a) self7=Q; }
      if(Qp>=8){ n8p++; if(Q<7) printf(" B%d(Q+%d)",b,Qp); if(b==a) self8p=Qp; }
      if(b==a && self7<0) self7=Q; if(b==a && self8p<0) self8p=Qp;
      if(b==a) printf(" [self Q=%d Q+=%d]",Q,Qp);
    }
    printf(" | nQ>=7: %d  nQ+>=8 (max over l0): %d\n",n7,n8p); fflush(stdout); }
  printf("hist Q:"); for(int i=0;i<9;i++) printf(" %d:%ld",i,hist[i]); printf("\nhist Q+ (max over l0):"); for(int i=0;i<9;i++) printf(" %d:%ld",i,histp[i]); printf("\n"); return 0; }
