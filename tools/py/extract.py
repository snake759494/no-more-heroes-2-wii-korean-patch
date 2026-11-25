import rmhg,gdlg,os,re,json,collections
root='../../work/dec'
JP=re.compile(r'[぀-ヿ一-鿿]')
order=[];ctx=collections.defaultdict(list)
for r,ds,fs in os.walk(root):
  for f in sorted(fs):
    p=os.path.join(r,f); d=open(p,'rb').read(); rel=os.path.relpath(p,root).replace(os.sep,'/')
    for pp,s,z in rmhg.walk(d):
        if d[s:s+4]==b'GDLG':
            m=gdlg.parse(d[s:s+z])
            if not any(JP.search(x) for x in m): continue
            for i,x in enumerate(m):
                if x not in ctx: order.append(x)
                ctx[x].append('%s|%s#%d'%(rel,','.join(map(str,pp)),i))
json.dump([{'ja':x,'ctx':ctx[x][:3]} for x in order],open('../../work/text/ja_unique.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(order),sum(len(x) for x in order))
# GDLG v1 (Shift-JIS) 문장
import gdlg1
ev=[]
for r,ds,fs in os.walk(root):
  for f in sorted(fs):
    d=open(os.path.join(r,f),'rb').read()
    for pp,s,z in rmhg.walk(d):
        if d[s:s+8]==b'GDLG'+bytes([1,0,0,1]):
            for x in gdlg1.parse(d[s:s+z]):
                x=x.decode('cp932')
                if JP.search(x) and x not in ev: ev.append(x)
json.dump(ev,open('../../work/text/ev_ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(ev))
