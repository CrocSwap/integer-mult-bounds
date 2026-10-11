#pragma once
string sha256(vector<uint8_t> s){
 const uint32_t K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
 uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19}; uint64_t len=uint64_t(s.size())*8;s.push_back(0x80);while(s.size()%64!=56)s.push_back(0);for(int j=7;j>=0;j--)s.push_back(uint8_t(len>>(8*j)));
 auto rr=[](uint32_t x,int n){return (x>>n)|(x<<(32-n));};
 for(size_t p=0;p<s.size();p+=64){uint32_t w[64];for(int j=0;j<16;j++)w[j]=(uint32_t(s[p+4*j])<<24)|(uint32_t(s[p+4*j+1])<<16)|(uint32_t(s[p+4*j+2])<<8)|s[p+4*j+3];for(int j=16;j<64;j++){uint32_t a=rr(w[j-15],7)^rr(w[j-15],18)^(w[j-15]>>3),b=rr(w[j-2],17)^rr(w[j-2],19)^(w[j-2]>>10);w[j]=w[j-16]+a+w[j-7]+b;}
 uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],z=h[7];for(int j=0;j<64;j++){uint32_t t=z+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^((~e)&g))+K[j]+w[j],u=(rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c));z=g;g=f;f=e;e=d+t;d=c;c=b;b=a;a=t+u;}h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=z;}
 ostringstream o;o<<hex<<setfill('0');for(auto x:h)o<<setw(8)<<x;return o.str();
}

