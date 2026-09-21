"""Structural regressions; real PowerPoint behavior is checked in each run."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

spec = importlib.util.spec_from_file_location('group_components', Path(__file__).resolve().parents[1] / 'visual-bank/group_components.py')
grouping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grouping)
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'p': P, 'a': A}


def slide_xml(text=False):
    root = ET.Element(f'{{{P}}}sld')
    tree = ET.SubElement(ET.SubElement(root, f'{{{P}}}cSld'), f'{{{P}}}spTree')
    for index, name, x in [(1, 'motif-a', 100), (2, 'motif-b', 250), (3, 'unrelated', 600)]:
        shape = ET.SubElement(tree, f'{{{P}}}sp')
        nv = ET.SubElement(shape, f'{{{P}}}nvSpPr')
        ET.SubElement(nv, f'{{{P}}}cNvPr', id=str(index), name=name)
        ET.SubElement(ET.SubElement(nv, f'{{{P}}}cNvSpPr'), f'{{{A}}}spLocks', noGrp='1', noRot='1')
        xf = ET.SubElement(ET.SubElement(shape, f'{{{P}}}spPr'), f'{{{A}}}xfrm')
        ET.SubElement(xf, f'{{{A}}}off', x=str(x), y='200')
        ET.SubElement(xf, f'{{{A}}}ext', cx='100', cy='80')
        if text and index == 1:
            ET.SubElement(ET.SubElement(shape, f'{{{P}}}txBody'), f'{{{A}}}t').text = 'Protected source sentence'
    return ET.tostring(root, encoding='utf-8')


class GroupComponentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'source.pptx'
        self.output = self.root/'candidate.pptx'
        self.report = self.root/'report.json'

    def create_source(self, text=False):
        pres = ET.Element(f'{{{P}}}presentation')
        ids = ET.SubElement(pres, f'{{{P}}}sldIdLst')
        ET.SubElement(ids, f'{{{P}}}sldId', {'id': '256', f'{{{R}}}id': 'rIdSecond'})
        ET.SubElement(ids, f'{{{P}}}sldId', {'id': '257', f'{{{R}}}id': 'rIdFirst'})
        rels = ET.Element(f'{{{REL}}}Relationships')
        for ident, part in [('rIdSecond', 'slides/slide2.xml'), ('rIdFirst', 'slides/slide1.xml')]:
            ET.SubElement(rels, f'{{{REL}}}Relationship', Id=ident, Target=part, Type=R+'/slide')
        with zipfile.ZipFile(self.source, 'w') as z:
            z.writestr('ppt/presentation.xml', ET.tostring(pres))
            z.writestr('ppt/_rels/presentation.xml.rels', ET.tostring(rels))
            z.writestr('ppt/slides/slide1.xml', slide_xml(text))
            z.writestr('ppt/slides/slide2.xml', slide_xml(text))

    def group(self, **overrides):
        record = {'slide': 1, 'group_name': 'Topic visual', 'child_names': ['motif-a', 'motif-b'], 'kind': 'illustration'}
        record.update(overrides)
        return grouping.group_components(self.source, self.output, [record], self.report)

    def test_presentation_order_and_identity_geometry(self):
        self.create_source()
        before = self.source.read_bytes()
        result = self.group()
        self.assertEqual(result['changed_parts'], ['ppt/slides/slide2.xml'])
        self.assertEqual(self.source.read_bytes(), before)
        with zipfile.ZipFile(self.source) as src, zipfile.ZipFile(self.output) as out:
            for name in src.namelist():
                if name != 'ppt/slides/slide2.xml': self.assertEqual(src.read(name), out.read(name))
            root = ET.fromstring(out.read('ppt/slides/slide2.xml'))
            group = root.find('p:cSld/p:spTree/p:grpSp', NS)
            self.assertIsNotNone(group)
            self.assertEqual([grouping.geometry(x) for x in group.findall('p:sp', NS)], [(100, 200, 100, 80), (250, 200, 100, 80)])
            xf = group.find('p:grpSpPr/a:xfrm', NS)
            self.assertEqual(xf.find('a:off', NS).attrib, xf.find('a:chOff', NS).attrib)
            self.assertEqual(xf.find('a:ext', NS).attrib, xf.find('a:chExt', NS).attrib)
            for lock in group.findall('.//a:spLocks', NS):
                self.assertNotIn('noGrp', lock.attrib)
                self.assertEqual(lock.get('noRot'), '1')
            self.assertEqual(root.find('p:cSld/p:spTree/p:sp/p:nvSpPr/p:cNvSpPr/a:spLocks', NS).get('noGrp'), '1')

    def test_missing_member_fails_without_output(self):
        self.create_source()
        before = self.source.read_bytes()
        with self.assertRaises(ValueError): self.group(child_names=['motif-a', 'missing'])
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), before)

    def test_illustration_group_rejects_source_text(self):
        self.create_source(text=True)
        with self.assertRaises(ValueError): self.group()
        self.assertFalse(self.output.exists())

    def test_evidence_group_retains_native_label(self):
        self.create_source(text=True)
        self.group(kind='evidence')
        with zipfile.ZipFile(self.output) as z:
            root = ET.fromstring(z.read('ppt/slides/slide2.xml'))
            self.assertEqual([x.text for x in root.findall('.//p:grpSp//a:t', NS)], ['Protected source sentence'])


if __name__ == '__main__':
    unittest.main()
