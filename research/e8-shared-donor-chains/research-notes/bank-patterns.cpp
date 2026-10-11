#include <bits/stdc++.h>
using namespace std;
int main(int argc,char**argv){ofstream o(argv[1]);o<<setprecision(18);int rr[]={4,5,7,8,9};int x[5]={};function<void(int,int)>rec=[&](int i,int mass){if(i==5){int pad=73-mass;if(pad>48)return;long double cost=73*logl(73)-(pad?pad*logl(pad):0);o<<cost;for(int j:x)o<<","<<j;o<<","<<pad<<"\n";return;}for(x[i]=0;mass+x[i]*rr[i]<=73;x[i]++)rec(i+1,mass+x[i]*rr[i]);};rec(0,0);}
