// SIX: Lemma S66 (exact). For every 6-dim label subspace V1 (orbit reps) and V2 (all), X = Λ(V1) ∪ Λ(V2) [∪ {t} in mode T]:
// H = {directions h : rank_F2 lab(Off(h) \ X) <= 7}  [mode T: some single line t removed additionally, per h (superset)].
// Report max real rank of span H. Directions: data.txt (|Off|<=77 complete list); mode 0 uses |Off|<=76.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef __int128 i128;
int LAB[112]; int PC[112][8]; int ND; int hv[7000][8]; int hv2[7000][8]; int htyp[7000]; int hoff_n[7000]; u128 OFF[7000]; int cap[7000];
int nd_use;
static inline int pc(u128 x){ return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64)); }
int f2rank_mask(u128 R){ int B[9]={0}; int r=0; for(int t=0;t<112;t++) if((R>>t)&1){ int x=LAB[t]; for(int k=8;k>=0;k--){ if(!((x>>k)&1)) continue; if(B[k]) x^=B[k]; else { B[k]=x; r++; break; } } } return r; }
// mode T: exists t in R with rank(R\t) <= 7
int rank_minus_one_le7(u128 R){ int r=f2rank_mask(R); if(r<=7) return 1; if(r>8) return 0; for(int t=0;t<112;t++) if((R>>t)&1){ if(f2rank_mask(R&~(((u128)1)<<t))<=7) return 1; } return 0; }
long long gcdll(long long a,long long b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ long long t=a%b; a=b; b=t;} return a; }
int realrank(int *list0,int n0){ long long Bm[8][8]; int piv[8]; int r=0; static int list[20000]; static int which[20000]; int n=0; for(int i=0;i<n0;i++){ list[n]=list0[i]; which[n++]=0; if(htyp[list0[i]]==2){ list[n]=list0[i]; which[n++]=1; } }
  for(int i=0;i<n;i++){ long long v[8]; for(int k=0;k<8;k++) v[k]= which[i]? hv2[list[i]][k] : hv[list[i]][k];
    for(int j=0;j<r;j++){ int p=piv[j]; if(v[p]==0) continue; long long a=Bm[j][p], b=v[p]; long long g=0; for(int k=0;k<8;k++){ v[k]=a*v[k]-b*Bm[j][k]; } for(int k=0;k<8;k++) g=gcdll(g,v[k]); if(g>1) for(int k=0;k<8;k++) v[k]/=g; }
    int p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) continue; // also need to clear p in earlier rows? not needed for rank (echelon by distinct pivots)
    // ensure pivots distinct: v reduced against all earlier pivots, so its first nonzero may still coincide with no earlier pivot? reduce until first nonzero not a pivot
    int again=1; while(again){ again=0; for(int j=0;j<r;j++){ int q=piv[j]; if(v[q]!=0){ long long a=Bm[j][q], b=v[q]; long long g=0; for(int k=0;k<8;k++) v[k]=a*v[k]-b*Bm[j][k]; for(int k=0;k<8;k++) g=gcdll(g,v[k]); if(g>1) for(int k=0;k<8;k++) v[k]/=g; again=1; } } }
    p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) continue;
    for(int k=0;k<8;k++) Bm[r][k]=v[k]; piv[r]=p; r++; if(r==8) return 8; }
  return r; }
// subspaces
u128 *SUB; int NS=0;
int cmp128(const void*a,const void*b){ u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:x>y; }
int par(int x){ return __builtin_popcount(x)&1; }
int gens[16][112]; int NG=0;
u128 mapmask(u128 m,int g){ u128 o=0; for(int t=0;t<112;t++) if((m>>t)&1) o|=((u128)1)<<gens[g][t]; return o; }
int findidx(u128 m){ int lo=0,hi=NS-1; while(lo<=hi){ int mid=(lo+hi)/2; if(SUB[mid]==m) return mid; if(SUB[mid]<m) lo=mid+1; else hi=mid-1;} return -1; }
int *uf; int fnd(int x){ while(uf[x]!=x){ uf[x]=uf[uf[x]]; x=uf[x];} return x; }
int k; int w[9];
void rec(int d,int *el,int nel,int last){ if(d==k){ u128 m=0; for(int t=0;t<112;t++){ int ok=1; for(int i=0;i<k;i++) if(par(LAB[t]&w[i])){ok=0;break;} if(ok) m|=((u128)1)<<t; } if(m) SUB[NS++]=m; return; }
    for(int x=last+1;x<512;x++){ int in=0; for(int i=0;i<nel;i++) if(el[i]==x){in=1;break;} if(in) continue; // x must be min of x+span
      int ok=1; for(int i=0;i<nel;i++) if((x^el[i])<x){ok=0;break;} if(!ok) continue;
      int el2[512]; for(int i=0;i<nel;i++){ el2[i]=el[i]; el2[nel+i]=el[i]^x; } w[d]=x; rec(d+1,el2,2*nel,x); } }

u128 *enumsub(int sdim,int *cnt){ k=9-sdim; NS=0; SUB=malloc(sizeof(u128)*4000000); int el0[1]={0}; rec(0,el0,1,0);
  qsort(SUB,NS,sizeof(u128),cmp128); int u=0; for(int i=0;i<NS;i++) if(i==0||SUB[i]!=SUB[i-1]) SUB[u++]=SUB[i]; *cnt=u; return SUB; }
u128 *G7; int n7; int THR=20; int *GL[7000]; unsigned char *GC[7000]; int GLn[7000]; long long nfull=0;
int qual(u128 r,int h,int s){ int c=pc(r); if(c>cap[h]+s) return 0; int rk=f2rank_mask(r); if(rk<=7) return 1; if(s==0) return 0;
  if(rk==8){ // coordinates in a basis of span(R); hyperplanes of span = nonzero functionals on F2^8
    int B[9]={0}; int bv[8]; int nb=0; int lst[112]; int nl=0; for(int t=0;t<112;t++) if((r>>t)&1){ lst[nl++]=t; }
    // build basis with coordinate tracking
    int piv[9]; int coordB[9]={0};
    for(int q=0;q<nl;q++){ int x=LAB[lst[q]], cx=0; for(int k2=8;k2>=0;k2--){ if(!((x>>k2)&1)) continue; if(B[k2]){ x^=B[k2]; cx^=coordB[k2]; } else { B[k2]=x; coordB[k2]=cx^(1<<nb); nb++; break; } } }
    // coordinate of each line: reduce its label, accumulating coordB
    int co[112]; for(int q=0;q<nl;q++){ int x=LAB[lst[q]], cx=0; for(int k2=8;k2>=0;k2--){ if(!((x>>k2)&1)) continue; x^=B[k2]; cx^=coordB[k2]; } co[q]=cx; }
    for(int phi=1;phi<256;phi++){ int bad=0; for(int q=0;q<nl;q++) if(__builtin_popcount(co[q]&phi)&1){ if(++bad>s) break; } if(bad<=s) return 1; }
    return 0; }
  int need=c-s; if(need>=THR){ int *L=GL[h]; for(int q=0;q<GLn[h];q++){ int g=L[q]; if(GC[h][q]<need) break; if(pc(r&~G7[g])<=s) return 1; } return 0; }
  nfull++; for(int g=0;g<n7;g++) if(pc(r&~G7[g])<=s) return 1; return 0; }
u128 *V3; int n3=0; int RT=99; int refmax=0;
int refine(u128 X1,u128 X2,int *cand,int nc){ int best=0; static int list[7000];
  for(int q=0;q<n3;q++){ u128 X=X1|X2|V3[q]; int n=0; for(int ci=0;ci<nc;ci++){ int h=cand[ci]; u128 r=OFF[h]&~X; if(pc(r)>cap[h]) continue; if(f2rank_mask(r)<=7) list[n++]=h; }
    if(n){ int rk=realrank(list,n); if(rk>best) best=rk; } }
  return best; }
int main(int argc,char**argv){
  const char*df=argv[1]; int adim=atoi(argv[2]), bdim=atoi(argv[3]), s=atoi(argv[4]), lim=atoi(argv[5]);
  int gw[10]={0,1,2,4,8,12,20,36,64,112};
  FILE*f=fopen(df,"r"); for(int i=0;i<112;i++) fscanf(f,"%d",&LAB[i]); int z; for(int i=0;i<8;i++) fscanf(f,"%d",&z);
  for(int i=0;i<112;i++) for(int k2=0;k2<8;k2++) fscanf(f,"%d",&PC[i][k2]);
  int nn; fscanf(f,"%d",&nn); ND=0;
  for(int i=0;i<nn;i++){ int typ; fscanf(f,"%d",&typ); htyp[ND]=typ; for(int k2=0;k2<8;k2++) fscanf(f,"%d",&hv[ND][k2]); if(typ==2) for(int k2=0;k2<8;k2++) fscanf(f,"%d",&hv2[ND][k2]); char st[4]; fscanf(f,"%s",st); u128 m=0; int c=0; int t;
    while(1){ int ch; do{ ch=fgetc(f);}while(ch==' '); if(ch=='\n'||ch==EOF) break; ungetc(ch,f); fscanf(f,"%d",&t); m|=((u128)1)<<t; c++; }
    u128 m2=0; for(int t2=0;t2<112;t2++){ long long d=0,d2=0; for(int k2=0;k2<8;k2++){ d+=(long long)PC[t2][k2]*hv[ND][k2]; d2+=(long long)PC[t2][k2]*hv2[ND][k2]; } if(d || (typ==2&&d2)) m2|=((u128)1)<<t2; } if(m2!=m){ fprintf(stderr,"off mismatch\n"); exit(1);}
    if(c<=lim){ OFF[ND]=m; hoff_n[ND]=c; ND++; } }
  fclose(f);
  f=fopen("gens.txt","r"); while(1){ int ok=1; for(int t=0;t<112;t++) if(fscanf(f,"%d",&gens[NG][t])!=1){ok=0;break;} if(!ok) break; NG++; } fclose(f);
  int npen=0; for(int h=0;h<ND;h++) npen+=htyp[h]==2; fprintf(stderr,"directions %d (pencils %d), gens %d\n",ND,npen,NG);
  G7=malloc(sizeof(u128)*44000); n7=0;
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){ int w3=w1^w2; if(w3<w2) continue; u128 m=0; for(int t=0;t<112;t++) if(!par(LAB[t]&w1)&&!par(LAB[t]&w2)) m|=((u128)1)<<t; G7[n7++]=m; }
  for(int h=0;h<ND;h++){ int b=0; int cnt[113]={0}; for(int g=0;g<n7;g++){ int c=pc(OFF[h]&G7[g]); cnt[c]++; if(c>b) b=c; } cap[h]=b;
    int tot=0; for(int c=THR;c<=112;c++) tot+=cnt[c]; GL[h]=malloc(sizeof(int)*(tot+1)); GC[h]=malloc(tot+1); GLn[h]=tot;
    int pos[113]; int p=0; for(int c=112;c>=THR;c--){ pos[c]=p; p+=cnt[c]; }
    for(int g=0;g<n7;g++){ int c=pc(OFF[h]&G7[g]); if(c>=THR){ GL[h][pos[c]]=g; GC[h][pos[c]]=c; pos[c]++; } } }
  int na_,nb_; u128 *A=enumsub(adim,&na_); u128 *Bs=enumsub(bdim,&nb_); SUB=A; NS=na_;
  fprintf(stderr,"V1 line sets %d, V2 line sets %d\n",na_,nb_);
  uf=malloc(sizeof(int)*NS); for(int i=0;i<NS;i++) uf[i]=i;
  for(int i=0;i<NS;i++) for(int g=0;g<NG;g++){ int j=findidx(mapmask(SUB[i],g)); if(j<0){ fprintf(stderr,"image not a flat!\n"); exit(1);} int a=fnd(i),b=fnd(j); if(a!=b) uf[a]=b; }
  int nrep=0; int *reps=malloc(sizeof(int)*NS); int *osz=calloc(NS,sizeof(int)); for(int i=0;i<NS;i++) osz[fnd(i)]++; for(int i=0;i<NS;i++) if(fnd(i)==i) reps[nrep++]=i;
  fprintf(stderr,"V1 orbits: %d\n",nrep);
  int only[200]; int nonly=0; if(argc>6){ char*p=argv[6]; while(*p){ only[nonly++]=strtol(p,&p,10); if(*p==',') p++; } }
  if(argc>7){ RT=atoi(argv[7]); int c3; V3=enumsub(3,&c3); n3=c3; fprintf(stderr,"V3 line sets %d\n",n3); }
  int overall=0; int maxcnt=0; long long hist[9]={0};
  int *act=malloc(sizeof(int)*ND); u128 *R1=malloc(sizeof(u128)*ND);
  for(int ri=0;ri<nrep;ri++){ if(nonly){ int f=0; for(int q=0;q<nonly;q++) if(only[q]==ri) f=1; if(!f) continue; } u128 X1=A[reps[ri]]; int na=0; int vmax=0;
    for(int h=0;h<ND;h++){ u128 r=OFF[h]&~X1; if(pc(r)<=cap[h]+gw[bdim]+s){ act[na]=h; R1[na]=r; na++; } }
    for(int j=0;j<nb_;j++){ u128 X2=Bs[j]; int list[7000]; int n=0;
      for(int a=0;a<na;a++){ u128 r=R1[a]&~X2; if(qual(r,act[a],s)) list[n++]=act[a]; }
      if(n>maxcnt) maxcnt=n;
      if(n){ int rk=realrank(list,n); hist[rk]++; if(rk>vmax) vmax=rk; if(rk>=RT){ int e=refine(X1,X2,list,n); if(e>refmax) refmax=e; printf("REFINE rep %d j %d relaxed %d exact-with-3flat %d\n",ri,j,rk,e); fflush(stdout); }
        if(rk>=7 && hist[rk]<=10){ printf("RANK%d rep %d j %d n %d :",rk,ri,j,n); for(int q=0;q<n;q++) printf(" %d",list[q]); printf("\n"); } }
    }
    if(vmax>overall) overall=vmax;
    printf("rep %d lines %d orbit %d active %d maxrank %d nfull %lld\n",ri,pc(X1),osz[reps[ri]],na,vmax,nfull); fflush(stdout);
  }
  printf("REFINE max exact rank %d\n",refmax);
  printf("OVERALL %s V1dim %d V2dim %d s %d lim %d: max real rank %d, max #directions %d; rank histogram (nonempty pairs):",df,adim,bdim,s,lim,overall,maxcnt);
  for(int r=1;r<=8;r++) printf(" %d:%lld",r,hist[r]); printf("\n");
}
