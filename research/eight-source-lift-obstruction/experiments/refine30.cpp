#define main anneal_main
#include "search.cpp"
#undef main
int main(){
 vector<string>seeds={"404623713412310507205215604053","035420602417513104317142306021"};
 mt19937_64 rng(77202);long long trials=0;int best=255;auto st=chrono::steady_clock::now();
 while(chrono::duration<double>(chrono::steady_clock::now()-st).count()<90){
  vector<int>w;for(char c:seeds[rng()%seeds.size()])w.push_back(c-'0');int cur=coverage(w);
  for(int t=0;t<100000;t++){
   auto v=w;int a=rng()%30,b=rng()%30;if(a>b)swap(a,b);
   int move=rng()%3;
   if(move==0)swap(v[a],v[b]);
   else if(move==1)reverse(v.begin()+a,v.begin()+b+1);
   else rotate(v.begin()+a,v.begin()+a+1,v.begin()+b+1);
   int c=coverage(v);double T=.15+.8*pow(1-t/100000.,2);trials++;
   if(c>=cur||generate_canonical<double,53>(rng)<exp((c-cur)/T)){w=v;cur=c;}
   if(cur==256){cout<<"WITNESS trials "<<trials<<" word ";for(int a:w)cout<<a;cout<<endl;return 0;}
  }
 }
 cout<<"INCOMPLETE trials "<<trials<<" no witness"<<endl;
}
