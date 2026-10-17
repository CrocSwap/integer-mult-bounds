// impl A, row 602 variant: qualification with one global extra line l0 (the 1-piece support):
// h qualifies for (A,B,l0) iff rank(Off(h)\(A|B|{l0})) <= 7. For each rep A, every B: N(A) = {B : exists l0 (or none) with span >= 8}.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef long long ll;
int lab[120]; static u128 M[44000]; int nm,nr,nc; int rep[64]; u128 OFF[5000]; int nv[5000]; ll V[5000][2][8];
int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int rk(u128 x){int b[9],nb=0; for(int t=0;t<120;t++) if((x>>t)&1){int v=lab[t]; for(int i=0;i<nb;i++){int w=v^b[i]; if(w<v)v=w;} if(v){if(nb==9) return 10; b[nb++]=v; for(int i=nb-1;i>0&&b[i]>b[i-1];i--){int s=b[i];b[i]=b[i-1];b[i-1]=s;}}} return nb;}
ll gcdl(ll a,ll b){if(a<0)a=-a;if(b<0)b=-b;while(b){ll t=a%b;a=b;b=t;}return a;}
ll Bs[8][8]; int piv[8]; int nb;
int addv(ll*v0){ll v[8]; memcpy(v,v0,sizeof v);
 for(int i=0;i<nb;i++){int p=piv[i]; if(v[p]){ll a=Bs[i][p],c=v[p]; ll g=0; for(int k=0;k<8;k++){v[k]=a*v[k]-c*Bs[i][k]; g=gcdl(g,v[k]);} if(g>1) for(int k=0;k<8;k++) v[k]/=g;}}
 int p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) return 0; memcpy(Bs[nb],v,sizeof v); piv[nb++]=p; return 1;}
void hexin(FILE*f,u128*x){char s[64]; fscanf(f,"%s",s); u128 r=0; for(char*c=s;*c;c++){int d=(*c<='9')?*c-'0':*c-'a'+10; r=r*16+d;} *x=r;}
int base[5000],nbase; int fixc[5000]; u128 fixl[5000]; int nfix;
int main(){
 FILE*f=fopen("ka.in","r"); fscanf(f,"%d %d %d",&nm,&nr,&nc); for(int i=0;i<nm;i++) hexin(f,&M[i]); for(int i=0;i<nr;i++) fscanf(f,"%d",&rep[i]);
 for(int i=0;i<nc;i++){hexin(f,&OFF[i]); fscanf(f,"%d",&nv[i]); for(int j=0;j<nv[i];j++) for(int k=0;k<8;k++) fscanf(f,"%lld",&V[i][j][k]);}
 FILE*g=fopen("lab.in","r"); for(int t=0;t<120;t++) fscanf(g,"%d",&lab[t]);
 for(int r=0;r<nr;r++){u128 A=M[rep[r]]; int nN=0; u128 Ucov=A; int selfsp=0;
  for(int b=0;b<nm;b++){u128 U=A|M[b]; nbase=0; nfix=0; u128 anyl=0;
   for(int c=0;c<nc;c++){u128 L=OFF[c]&~U; int s=pc(L); if(s>37) continue; int q=rk(L); if(q<=7&&s<=36){base[nbase++]=c;continue;}
     if(q==8){u128 fl=0; for(int t=0;t<120;t++) if((L>>t)&1) if(pc(L)-1<=36 && rk(L&~(((u128)1)<<t))<=7) fl|=((u128)1)<<t; if(fl){fixc[nfix]=c; fixl[nfix++]=fl; anyl|=fl;}}}
   int best=0; nb=0; for(int i=0;i<nbase;i++) for(int j=0;j<nv[base[i]];j++) addv(V[base[i]][j]); best=nb;
   for(int t=0;t<120;t++) if((anyl>>t)&1){ nb=0; for(int i=0;i<nbase;i++) for(int j=0;j<nv[base[i]];j++) addv(V[base[i]][j]);
      for(int i=0;i<nfix;i++) if((fixl[i]>>t)&1) for(int j=0;j<nv[fixc[i]];j++) addv(V[fixc[i]][j]); if(nb>best) best=nb; }
   if(b==rep[r]) selfsp=best;
   if(best>=8){nN++; Ucov|=M[b]; printf("   B=%d |B|=%d |A&B|=%d span=%d\n",b,pc(M[b]),pc(A&M[b]),best);}}
  printf("rep %d |A|=%d: |N8(A)| (any l0) = %d, self-span %d\n",rep[r],pc(A),nN,selfsp); fflush(stdout);}
}
