// NMH2 LZ compressor/decompressor
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef unsigned char u8;
static u8* rd(const char*p,long*n){FILE*f=fopen(p,"rb");if(!f){perror(p);exit(1);}fseek(f,0,2);*n=ftell(f);fseek(f,0,0);u8*b=malloc(*n+16);fread(b,1,*n,f);fclose(f);return b;}
static void wr(const char*p,u8*b,long n){FILE*f=fopen(p,"wb");fwrite(b,1,n,f);fclose(f);}
#define HB 20
#define MAXLEN 8195
int main(int argc,char**argv){
  if(argc<4){fprintf(stderr,"usage: c|d in out [depth]\n");return 1;}
  long n;u8*in=rd(argv[2],&n);
  if(argv[1][0]=='d'){
    uint32_t us=in[0]|in[1]<<8|in[2]<<16|in[3]<<24,cs=in[4]|in[5]<<8|in[6]<<16|in[7]<<24;u8 esc=in[8];
    u8*o=malloc(us+16);long i=9,k=0;
    while(i<cs){u8 b=in[i++];if(b!=esc){o[k++]=b;continue;}u8 x=in[i++];if(x==esc){o[k++]=esc;continue;}if(x>esc)x--;
      long L=x>>3;if(x&4)L|=in[i++]<<5;int m=x&3;long d=in[i++];if(m){d|=in[i++]<<8;if(m==2)d|=in[i++]<<16;}
      long ln=L+4;d++;for(long j=0;j<ln;j++,k++)o[k]=o[k-d];}
    if(k!=us)fprintf(stderr,"size mismatch %ld %u\n",k,us);
    wr(argv[3],o,us);return 0;}
  int depth=argc>4?atoi(argv[4]):64;
  long cnt[256]={0};for(long i=0;i<n;i++)cnt[in[i]]++;
  int esc=0;for(int c=1;c<256;c++)if(cnt[c]<cnt[esc])esc=c;
  u8*o=malloc(n*2+64);long k=9;
  int32_t*head=malloc(sizeof(int32_t)<<HB);memset(head,0xff,sizeof(int32_t)<<HB);
  int32_t*prev=malloc(sizeof(int32_t)*n);
  #define H(p) ((((uint32_t)in[p]<<16)^((uint32_t)in[p+1]<<8)^in[p+2])*2654435761u>>(32-HB))
  long i=0;
  while(i<n){
    long best=0,bd=0;
    if(i+4<=n){
      uint32_t h=H(i);long c=head[h];int dd=depth;
      long maxl=n-i;if(maxl>MAXLEN)maxl=MAXLEN;
      while(c>=0&&dd-->0&&i-c<=0x100000){
        if(in[c+best]==in[i+best]){long l=0;while(l<maxl&&in[c+l]==in[i+l])l++;
          if(l>best){best=l;bd=i-c;if(l==maxl)break;}}
        c=prev[c];}
    }
    long D=bd-1;
    int cost= best>=4 ? (3+(best-4>=32)+(D>=256)+(D>=65536)) : 99;
    if(best>=4 && cost<best){
      long L=best-4;int m=D<256?0:(D<65536?1:2);
      int v=((L&31)<<3)|(L>=32?4:0)|m;
      o[k++]=esc;o[k++]=v>=esc?v+1:v;
      if(L>=32)o[k++]=L>>5;
      o[k++]=D&255;if(m){o[k++]=(D>>8)&255;if(m==2)o[k++]=(D>>16)&255;}
      for(long j=0;j<best;j++){if(i+3<=n){uint32_t h=H(i);prev[i]=head[h];head[h]=i;}i++;}
    } else {
      if(in[i]==esc){o[k++]=esc;o[k++]=esc;}else o[k++]=in[i];
      if(i+3<=n){uint32_t h=H(i);prev[i]=head[h];head[h]=i;}i++;
    }
  }
  o[0]=n;o[1]=n>>8;o[2]=n>>16;o[3]=n>>24;o[4]=k;o[5]=k>>8;o[6]=k>>16;o[7]=k>>24;o[8]=esc;
  wr(argv[3],o,k);return 0;}
