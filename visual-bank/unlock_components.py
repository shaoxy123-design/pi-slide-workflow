#!/usr/bin/env python3
"""Remove exporter-added grouping locks only from explicitly named bank shapes.

Usage: python visual-bank/unlock_components.py INPUT.pptx OUTPUT.pptx
       --names-json component-names.json --report report.json

names-json is a JSON list of exact names returned by recipes.mjs. The helper
supports the current artifact-tool's p:/a: transitional OOXML serialization.
It does not change original shapes, geometry, text, media, relationships, or
other locks. Each name must resolve exactly once. Output must be a new file.
Native PowerPoint group/move/scale/save/reopen validation is still required.
"""
import argparse,copy,hashlib,html,json,re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
SHA=lambda b:hashlib.sha256(b).hexdigest()
def unlock_components(source,output,names,report):
    source,output,report=map(Path,(source,output,report))
    if output.exists() or output.resolve()==source.resolve():raise ValueError('Output must be a new file')
    if report.resolve()in(source.resolve(),output.resolve()):raise ValueError('Report cannot replace a deck')
    if not isinstance(names,list)or not names or any(not isinstance(n,str)or not n for n in names)or len(names)!=len(set(names)):raise ValueError('Provide unique exact component names')
    targets=set(names);found=[];changes=[];parts={}
    original=source.read_bytes()
    with zipfile.ZipFile(source)as z:
        infos=z.infolist()
        for info in infos:
            data=z.read(info.filename);updated=data
            if re.fullmatch(r'ppt/slides/slide\d+\.xml',info.filename):
                root=ET.fromstring(data)
                for shape in root.findall('.//p:sp',NS):
                    nv=shape.find('p:nvSpPr/p:cNvPr',NS)
                    if nv is not None and nv.get('name')in targets:found.append(nv.get('name'))
                def edit(match):
                    block=match.group(0);nv=re.search(r'<p:cNvPr\b[^>]*\bname="([^"]*)"',block)
                    if not nv or html.unescape(nv.group(1))not in targets:return block
                    name=html.unescape(nv.group(1));count=0
                    def lock(m):
                        nonlocal count
                        changed,n=re.subn(r'\snoGrp="(?:1|true)"','',m.group(0));count+=n;return changed
                    changed=re.sub(r'<a:spLocks\b[^>]*>',lock,block)
                    if count:changes.append({'part':info.filename,'name':name,'removed_noGrp':count})
                    return changed
                updated=re.sub(r'<p:sp>.*?</p:sp>',edit,data.decode('utf-8'),flags=re.S).encode('utf-8')
                new=ET.fromstring(updated)
                for shape in new.findall('.//p:sp',NS):
                    nv=shape.find('p:nvSpPr/p:cNvPr',NS)
                    if nv is not None and nv.get('name')in targets:
                        for lock in shape.findall('p:nvSpPr/p:cNvSpPr/a:spLocks',NS):
                            if lock.get('noGrp')in('1','true'):raise ValueError('Unsupported serialization; grouping lock remained')
            parts[info.filename]=updated
        if sorted(found)!=sorted(names):raise ValueError('Each exact name must resolve once in the package')
        if not changes:raise ValueError('No requested grouping locks removed; inspect existing state explicitly')
        with zipfile.ZipFile(output,'w')as out:
            for info in infos:out.writestr(copy.copy(info),parts[info.filename])
    if source.read_bytes()!=original:raise ValueError('Source changed unexpectedly')
    result={'source_sha256':SHA(original),'candidate_sha256':SHA(output.read_bytes()),'requested_component_count':len(names),'removed_grouping_locks':len(changes),'changes':changes,'source_unchanged':True,'claim_boundary':'Only exported noGrp locks removed from exact named components. Native grouping/movement/resizing requires application validation.'}
    report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('output');p.add_argument('--names-json',required=True);p.add_argument('--report',required=True);a=p.parse_args()
    names=json.loads(Path(a.names_json).read_text(encoding='utf-8'))
    r=unlock_components(a.source,a.output,names,a.report)
    print(json.dumps({k:v for k,v in r.items()if k!='changes'}))
if __name__=='__main__':main()
