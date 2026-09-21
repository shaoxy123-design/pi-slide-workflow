import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { BackendError, requireThat } from './backend-core.mjs';
const exec = promisify(execFile);
export const guardPath = fileURLToPath(new URL('../pptx_guard.py', import.meta.url));
export async function sha256(file) { return crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex'); }
export async function writeJson(file, data) { await fs.writeFile(file, JSON.stringify(data, null, 2) + '\n', {flag:'wx'}); }
export async function sourceFile(file) {
  requireThat(path.extname(file).toLowerCase() === '.pptx', 'INVALID_SOURCE', 'Source must be a .pptx file');
  const resolved = await fs.realpath(file);
  requireThat((await fs.stat(resolved)).isFile(), 'INVALID_SOURCE', 'Source must be a regular file');
  return resolved;
}
/** Resolve existing parent links and forbid overwrite, including case aliases. */
export async function newPath(file) {
  const absolute = path.resolve(file);
  const canonical = path.join(await fs.realpath(path.dirname(absolute)), path.basename(absolute));
  try { await fs.lstat(canonical); throw new BackendError('OUTPUT_EXISTS', `Refusing to overwrite existing path: ${canonical}`); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  return canonical;
}
export function distinctPaths(paths) {
  const normalized = paths.map(p => process.platform === 'win32' ? path.resolve(p).toLowerCase() : path.resolve(p));
  requireThat(new Set(normalized).size === normalized.length, 'PATH_COLLISION', 'Source, plan, output, report and evidence paths must be distinct');
}
export async function loadRuntime(modules) {
  requireThat(modules && path.isAbsolute(modules), 'RUNTIME_UNAVAILABLE', 'Set --runtime-modules (or RUNTIME_NODE_MODULES) to the absolute bundled node_modules directory');
  try {
    const req = createRequire(path.join(modules, '__pptx_backend__.cjs'));
    const entry = req.resolve('@oai/artifact-tool');
    const lib = await import(pathToFileURL(entry).href);
    const pkg = JSON.parse(await fs.readFile(path.join(path.dirname(path.dirname(entry)), 'package.json'), 'utf8'));
    return { ...lib, backendVersion: pkg.version };
  } catch (error) { throw new BackendError('RUNTIME_UNAVAILABLE', `Cannot load bundled @oai/artifact-tool: ${error.message}`); }
}
export async function importDeck(runtime, source) {
  return runtime.PresentationFile.importPptx(await runtime.FileBlob.load(source));
}
export async function inventoryOf(deck, source, digest, backendVersion) {
  const snapshot = await deck.inspect({kind:'slide,textbox,shape,image,table,chart',maxChars:1000000});
  requireThat(!snapshot.truncated, 'INCOMPLETE_INSPECTION', 'Inspection was truncated; this deck exceeds the adapter inspection budget');
  const records = snapshot.ndjson.split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
  const slides = records.filter(r => r.kind === 'slide').map(r => {
    const frame = deck.resolve(r.id).frame;
    requireThat(frame && Number.isFinite(frame.width) && frame.width>0 && Number.isFinite(frame.height) && frame.height>0, 'INCOMPLETE_INSPECTION', `Slide ${r.slide} dimensions unavailable`);
    return {slide:r.slide,slide_id:r.id,width:frame.width,height:frame.height,objects:[]};
  });
  requireThat(slides.length > 0 && slides.length === deck.slides.items.length, 'INCOMPLETE_INSPECTION', 'Inspection did not cover every slide');
  const seen = new Set();
  for (const record of records.filter(r => r.kind !== 'slide')) {
    const slide = slides.find(s => s.slide === record.slide);
    requireThat(slide && typeof record.id === 'string' && !seen.has(record.id), 'INCOMPLETE_INSPECTION', 'Missing, duplicate, or unbound native object ID');
    seen.add(record.id);
    const bbox = record.bbox;
    let position = null;
    if (Array.isArray(bbox) && bbox.length === 4) {
      position = Object.fromEntries(['left','top','width','height'].map((key,index) => [key,bbox[index]]));
      // Zero-width connectors can be inventoried, but never edited by this adapter.
      requireThat(Object.values(position).every(Number.isFinite), 'INCOMPLETE_INSPECTION', `Invalid geometry for ${record.id}`);
    }
    const supported = position && position.width > 0 && position.height > 0;
    let font = null;
    if (record.kind === 'textbox') {
      const px = deck.resolve(record.id).text.fontSize;
      if (Number.isFinite(px)) font = px * 0.75;
    }
    const ops = !supported ? [] : record.kind === 'textbox' ? ['move_resize', ...(font === null ? [] : ['set_font_size'])] : record.kind === 'chart' && record.chartType === 'bar' ? ['move_resize'] : [];
    slide.objects.push({object_id:record.id,kind:record.kind,name:record.name??null,chart_type:record.chartType??null,position,font_size_pt:font,supported_ops:ops,...(record.text !== undefined ? {text:record.text} : {})});
  }
  return {version:1,kind:'pptx-backend-inventory',backend:{name:'@oai/artifact-tool',version:backendVersion},source:{path:source,sha256:digest},units:{geometry:'px at 96 DPI',font_size:'pt'},slides,
    limitations:['Supported edits: native text boxes (geometry and whole-box font size), native bar charts (geometry only). Other objects may remain unchanged if the source-specific no-op guard passes.', 'Inspection IDs are bound to this source SHA-256; never synthesize IDs or reuse plans for another source.', 'Every apply performs source-specific no-op qualification and content comparison. Neither proves preservation of every PowerPoint feature.', 'Candidate rendering uses artifact-tool after PPTX reimport. Independent visual and native editability review in a suitable application remains required.']};
}
export async function guard(python, args, reportFile) {
  requireThat(python && path.isAbsolute(python), 'PYTHON_UNAVAILABLE', 'Set --python (or RUNTIME_PYTHON) to the absolute bundled Python executable for the content guard');
  try { await exec(python, [guardPath,...args,'--output',reportFile], {maxBuffer:1024*1024,windowsHide:true}); }
  catch (error) {
    if (error.code !== 1) throw new BackendError('GUARD_ERROR', `Content guard failed: ${error.stderr || error.message}`);
  }
  return JSON.parse(await fs.readFile(reportFile,'utf8'));
}
// Fixed read-only program. A plan cannot supply Python, XML, paths or code here.
const PREFLIGHT = String.raw`
import json, sys, zipfile, xml.etree.ElementTree as ET
findings=[]
P='http://schemas.openxmlformats.org/presentationml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
allowed_ext={
 '{E76CE94A-603C-4142-B9EB-6D1370010A27}': 'discardImageEditData',
 '{D31A062A-798A-4329-ABDD-BBA856620510}': 'defaultImageDpi',
 '{FD5EFAAD-0ECE-453E-9831-46B23BE46B34}': 'chartTrackingRefBased',
 '{FF2B5EF4-FFF2-40B4-BE49-F238E27FC236}': 'creationId',
 '{BB962C8B-B14F-4D97-AF65-F5344CB8AC3E}': 'creationId',
}
allowed_extension_children={
 '{http://schemas.microsoft.com/office/powerpoint/2010/main}discardImageEditData',
 '{http://schemas.microsoft.com/office/powerpoint/2010/main}defaultImageDpi',
 '{http://schemas.microsoft.com/office/powerpoint/2012/main}chartTrackingRefBased',
 '{http://schemas.microsoft.com/office/drawing/2014/main}creationId',
 '{http://schemas.microsoft.com/office/powerpoint/2010/main}creationId',
}
def local(tag): return tag.rsplit('}',1)[-1]
def flag(part,feature):
 item={'part':part,'feature':feature}
 if item not in findings: findings.append(item)
with zipfile.ZipFile(sys.argv[1]) as archive:
 for name in archive.namelist():
  lower=name.lower()
  if lower.startswith(('ppt/diagrams/','ppt/comments/','ppt/commentauthors','ppt/active','ppt/ink/','customxml/')): flag(name,'unsupported_feature_part')
  if lower.endswith(('.bin','.vml')): flag(name,'binary_or_legacy_object')
  if not lower.endswith(('.xml','.rels')): continue
  root=ET.fromstring(archive.read(name))
  for element in root.iter():
   tag=local(element.tag)
   if element.tag.startswith('{'+M+'}'): flag(name,'editable_equation')
   if tag in ('timing','transition','grpSp','oleObj','control','custGeom','cxnSp','videoFile','audioFile','wavAudioFile'): flag(name,'unsupported_'+tag)
   if tag=='cNvPr' and (element.get('descr') or element.get('title')): flag(name,'accessibility_metadata')
   if tag=='xfrm' and any(element.get(attr) not in (None,'0','false') for attr in ('rot','flipH','flipV')): flag(name,'rotated_or_flipped_object')
   if tag=='graphicData' and element.get('uri') not in ('http://schemas.openxmlformats.org/drawingml/2006/chart','http://schemas.openxmlformats.org/drawingml/2006/table'): flag(name,'unsupported_graphic_frame')
   if tag=='extLst':
    for extension in element:
     children=list(extension)
     if extension.get('uri') not in allowed_ext or len(children)!=1 or local(children[0].tag)!=allowed_ext.get(extension.get('uri')) or children[0].tag not in allowed_extension_children or list(children[0]): flag(name,'unqualified_extension')
   if tag=='Relationship' and any(token in element.get('Type','').lower() for token in ('oleobject','diagram','comment','audio','video')): flag(name,'unsupported_relationship')
print(json.dumps({'passed':not findings,'findings':findings,'coverage':'Conservative rejection of known unqualified feature families, not complete OOXML feature validation.'}))
`;
export async function preflightSource(python, source) {
  try {
    const result = await exec(python,['-c',PREFLIGHT,source],{maxBuffer:1024*1024,windowsHide:true});
    return JSON.parse(result.stdout);
  } catch (error) { throw new BackendError('PREFLIGHT_ERROR', `Read-only source preflight failed: ${error.stderr || error.message}`); }
}
export async function renderAll(deck, inventory, directory) {
  await fs.mkdir(directory);
  const files = [];
  for (const item of inventory.slides) {
    const slide = deck.resolve(item.slide_id);
    const imagePath = path.join(directory,`slide-${item.slide}.png`);
    const layoutPath = path.join(directory,`slide-${item.slide}.layout.json`);
    await fs.writeFile(imagePath,new Uint8Array(await (await slide.export({format:'png',scale:1})).arrayBuffer()),{flag:'wx'});
    await fs.writeFile(layoutPath,await (await slide.export({format:'layout'})).text(),{flag:'wx'});
    files.push({slide:item.slide,png:imagePath,layout:layoutPath});
  }
  return files;
}
