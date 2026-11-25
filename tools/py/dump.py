import rmhg,gdlg,os,json
root='../../work/dec'
allm={};tot=0;chars=set();uniq=set()
for r,ds,fs in os.walk(root):
  for f in sorted(fs):
    p=os.path.join(r,f); d=open(p,'rb').read(); rel=os.path.relpath(p,root).replace(os.sep,'/')
    for path,s,z in rmhg.walk(d):
        if d[s:s+4]==b'GDLG':
            m=gdlg.parse(d[s:s+z])
            allm[rel+'|'+','.join(map(str,path))]=m
            tot+=len(m); uniq.update(m); [chars.update(x) for x in m]
print(len(allm),tot,len(uniq),len(chars),sum(len(x) for x in uniq))
json.dump(allm,open('../../work/gdlg_all.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
