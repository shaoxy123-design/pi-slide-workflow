#!/usr/bin/env python3
"""Package exact named native components as one delivered group per topic.

python visual-bank/group_components.py INPUT.pptx OUTPUT.pptx
  --groups-json GROUPS.json --report REPORT.json

GROUPS.json is a list of {slide, group_name, child_names, kind, insert_before?}.
kind is illustration, existing_banner, evidence, or text_emphasis. Illustration
groups reject source text. Noncontiguous source evidence/banner groups should
specify insert_before to preserve the original text reading order. The helper
keeps child geometry unchanged and uses identity coordinate transforms. Native
PowerPoint move/resize/save/reopen checks remain required after packaging.
Slide numbers follow presentation order, resolved through package relationships.
Native graphicFrames and rotated members are deliberately unsupported until a
qualified transform implementation is provided. Shapes, pictures and existing
groups with unrotated explicit transforms are supported by this narrow helper.
"""
import argparse,copy,hashlib,json,posixpath,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
for prefix,uri in NS.items():ET.register_namespace(prefix,uri)
def tag(prefix,name):return '{'+NS[prefix]+'}'+name
sha=lambda b:hashlib.sha256(b).hexdigest()
def shape_name(element):
    node=element.find('.//p:cNvPr',NS)
    return node.get('name') if node is not None else None
def geometry(element):
    transform=element.find('p:spPr/a:xfrm',NS)
    if transform is None:transform=element.find('p:grpSpPr/a:xfrm',NS)
    if transform is None:raise ValueError(f'Missing transform: {shape_name(element)}')
    if int(transform.get('rot','0'))%21600000:raise ValueError('Rotated members require a qualified bounds implementation')
    off=transform.find('a:off',NS);ext=transform.find('a:ext',NS)
    if off is None or ext is None:raise ValueError('Incomplete transform')
    return tuple(int(v)for v in(off.get('x'),off.get('y'),ext.get('cx'),ext.get('cy')))
def group_components(source,output,specs,report):
    source,output,report=map(Path,(source,output,report))
    if output.exists()or output.resolve()==source.resolve():raise ValueError('Output must be a new file')
    if report.exists()or report.resolve()in(source.resolve(),output.resolve()):raise ValueError('Report must be a new separate file')
    if not isinstance(specs,list)or not specs:raise ValueError('Group specifications required')
    original=source.read_bytes();changed={};receipts=[]
    with zipfile.ZipFile(source)as z:
        presentation=ET.fromstring(z.read('ppt/presentation.xml'))
        relationships=ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
        relmap={r.get('Id'):r for r in relationships}
        slide_parts=[]
        for item in presentation.findall('p:sldIdLst/p:sldId',NS):
            rel=relmap.get(item.get(tag('r','id')))
            if rel is None or rel.get('TargetMode')=='External' or not rel.get('Type','').endswith('/slide'):raise ValueError('Invalid presentation slide relationship')
            target=rel.get('Target','')
            part=posixpath.normpath(target.lstrip('/')if target.startswith('/')else posixpath.join('ppt',target))
            if not part.startswith('ppt/slides/')or part not in z.namelist():raise ValueError('Invalid slide part target')
            slide_parts.append(part)
        for spec in specs:
            slide=spec['slide'];group_name=spec['group_name'];names=spec['child_names'];kind=spec.get('kind','illustration')
            if not isinstance(slide,int)or slide<1:raise ValueError('Invalid slide')
            if not isinstance(group_name,str)or not group_name:raise ValueError('Missing group name')
            if len(names)<2 or len(names)!=len(set(names)):raise ValueError('Groups require at least two distinct exact member names')
            if kind not in('illustration','existing_banner','evidence','text_emphasis'):raise ValueError('Unknown group kind')
            if slide>len(slide_parts):raise ValueError('Slide outside presentation order')
            part=slide_parts[slide-1]
            root=changed.setdefault(part,ET.fromstring(z.read(part)))
            tree=root.find('p:cSld/p:spTree',NS)
            if tree is None:raise ValueError('Missing slide shape tree')
            children=list(tree);lookup={}
            for child in children:
                name=shape_name(child)
                if name is not None:lookup.setdefault(name,[]).append(child)
            if group_name in lookup:raise ValueError('Group name already exists')
            if any(len(lookup.get(name,[]))!=1 for name in names):raise ValueError('Each member must resolve exactly once at the top level')
            selected=[child for child in children if shape_name(child)in names]
            if kind=='illustration' and any(''.join(child.itertext()).strip()for child in selected):
                # OOXML text lives in a:t; formatting metadata contains no prose.
                if any(any((t.text or '').strip()for t in child.findall('.//a:t',NS))for child in selected):raise ValueError('Source text cannot be bundled into illustration groups')
            anchor=spec.get('insert_before')
            if anchor is None:anchor_index=min(children.index(c)for c in selected)
            else:
                if len(lookup.get(anchor,[]))!=1:raise ValueError('insert_before must resolve exactly once')
                anchor_index=children.index(lookup[anchor][0])
            bounds=[geometry(c)for c in selected]
            left=min(b[0]for b in bounds);top=min(b[1]for b in bounds)
            width=max(b[0]+b[2]for b in bounds)-left;height=max(b[1]+b[3]for b in bounds)-top
            if width<=0 or height<=0:raise ValueError('Nonpositive group extent')
            max_id=max(int(c.get('id','0'))for c in root.findall('.//p:cNvPr',NS))
            group=ET.Element(tag('p','grpSp'));nv=ET.SubElement(group,tag('p','nvGrpSpPr'))
            ET.SubElement(nv,tag('p','cNvPr'),{'id':str(max_id+1),'name':group_name})
            ET.SubElement(nv,tag('p','cNvGrpSpPr'));ET.SubElement(nv,tag('p','nvPr'))
            props=ET.SubElement(group,tag('p','grpSpPr'));xf=ET.SubElement(props,tag('a','xfrm'))
            ET.SubElement(xf,tag('a','off'),{'x':str(left),'y':str(top)});ET.SubElement(xf,tag('a','ext'),{'cx':str(width),'cy':str(height)})
            ET.SubElement(xf,tag('a','chOff'),{'x':str(left),'y':str(top)});ET.SubElement(xf,tag('a','chExt'),{'cx':str(width),'cy':str(height)})
            removed_locks=0
            for child in selected:
                for locks in child.findall('.//a:spLocks',NS):
                    if locks.get('noGrp')in('1','true'):del locks.attrib['noGrp'];removed_locks+=1
                tree.remove(child);group.append(child)
            insert_index=sum(1 for child in children[:anchor_index]if child not in selected)
            tree.insert(insert_index,group)
            assert [geometry(c)for c in list(group)[2:]]==bounds
            receipts.append({'slide':slide,'group_name':group_name,'kind':kind,'child_names':[shape_name(c)for c in selected],'child_count':len(selected),'selection_unit':'native_group','bounds_emu':{'left':left,'top':top,'width':width,'height':height},'child_geometry_preserved':True,'removed_noGrp_locks':removed_locks})
        with zipfile.ZipFile(output,'w')as out:
            for info in z.infolist():
                data=ET.tostring(changed[info.filename],encoding='utf-8',xml_declaration=True)if info.filename in changed else z.read(info.filename)
                out.writestr(copy.copy(info),data)
    if source.read_bytes()!=original:raise ValueError('Source changed')
    result={'source_sha256':sha(original),'candidate_sha256':sha(output.read_bytes()),'group_count':len(receipts),'groups':receipts,'changed_parts':list(changed),'source_unchanged':True,'claim_boundary':'Native group structure and identity child transforms verified. Application selection/move/resize/save/reopen still required.'}
    report.write_text(json.dumps(result,indent=2),encoding='utf-8');return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('output');p.add_argument('--groups-json',required=True);p.add_argument('--report',required=True);a=p.parse_args()
    result=group_components(a.source,a.output,json.loads(Path(a.groups_json).read_text(encoding='utf-8')),a.report)
    print(json.dumps({k:v for k,v in result.items()if k!='groups'}))
if __name__=='__main__':main()
