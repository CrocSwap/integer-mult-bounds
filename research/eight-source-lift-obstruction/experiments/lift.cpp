#define main anneal_main
#include "search.cpp"
#undef main
int main(){
 mt19937_64 rng(150725); vector<int>w; for(int i=0;i<7;i++)for(int j=0;j<(i<5?4:2);j++)w.push_back(i);
 auto st=chrono::steady_clock::now(); int best=0,parents=0;long long lifts=0;
 while(chrono::duration<double>(chrono::steady_clock::now()-st).count()<90){
  shuffle(w.begin(),w.end(),rng);int cur=coverage(w);
  for(int t=0;t<40000;t++){
   int a=rng()%24,b=rng()%24;swap(w[a],w[b]);int c=coverage(w);double T=.1+2*pow(1-t/40000.,2);
   if(c>=cur||generate_canonical<double,53>(rng)<exp((c-cur)/T))cur=c;else swap(w[a],w[b]);
   if(cur!=128)continue;
   parents++;
   for(int a=0;a<24;a++)for(int b=a;b<24;b++)for(int c=b;c<24;c++)for(int d=c;d<24;d++){
    vector<int>v;for(int i=0;i<24;i++){for(int x:{a,b,c,d})if(x==i)v.push_back(7);v.push_back(w[i]);}
    int cov=coverage(v);lifts++;
    if(cov>best){best=cov;cout<<"best "<<best<<" parents "<<parents<<" lifts "<<lifts<<" word ";for(int x:v)cout<<x;cout<<endl;}
    if(cov==256)return 0;
   }
   break;
  }
 }
 cout<<"INCOMPLETE sampled parents "<<parents<<" lifts "<<lifts<<" best "<<best<<endl;
}
