/** Pure, fail-closed validation for the small artifact-tool adapter. */
export class BackendError extends Error {
  constructor(code, message) { super(message); this.name = 'BackendError'; this.code = code; }
}
export function requireThat(condition, code, message) {
  if (!condition) throw new BackendError(code, message);
}
function exactKeys(value, keys, label) {
  requireThat(value !== null && typeof value === 'object' && !Array.isArray(value), 'INVALID_PLAN', `${label} must be an object`);
  requireThat(Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key)), 'INVALID_PLAN', `${label} must contain exactly: ${keys.join(', ')}`);
}
export function validatePosition(value, label = 'position') {
  exactKeys(value, ['left', 'top', 'width', 'height'], label);
  requireThat(Object.values(value).every(v => typeof v === 'number' && Number.isFinite(v)), 'INVALID_GEOMETRY', `${label} values must be finite numbers in pixels`);
  requireThat(value.width > 0 && value.height > 0, 'INVALID_GEOMETRY', `${label} width and height must be positive`);
}
export function samePosition(a, b) {
  return ['left', 'top', 'width', 'height'].every(k => Math.abs(a[k] - b[k]) <= 0.02);
}
export function validatePlan(plan, inventory) {
  exactKeys(plan, ['version', 'source_sha256', 'operations'], 'plan');
  requireThat(plan.version === 1, 'INVALID_PLAN', 'Only plan version 1 is supported');
  requireThat(typeof plan.source_sha256 === 'string' && /^[a-f0-9]{64}$/.test(plan.source_sha256), 'INVALID_PLAN', 'source_sha256 must be a lowercase SHA-256 digest');
  requireThat(plan.source_sha256 === inventory.source.sha256, 'SOURCE_MISMATCH', 'Plan source_sha256 does not match this source file; inspect and plan again');
  requireThat(Array.isArray(plan.operations) && plan.operations.length > 0 && plan.operations.length <= 200, 'INVALID_PLAN', 'operations must contain between 1 and 200 entries');
  const ids = new Set(), edits = new Set();
  for (const operation of plan.operations) {
    requireThat(['move_resize', 'set_font_size'].includes(operation?.op), 'UNAUTHORIZED_OPERATION', `Unsupported operation: ${String(operation?.op)}`);
    const payload = operation.op === 'move_resize' ? 'position' : 'font_size_pt';
    exactKeys(operation, ['id', 'slide', 'object_id', 'op', 'expected_position', payload], 'operation');
    requireThat(typeof operation.id === 'string' && /^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/.test(operation.id), 'INVALID_PLAN', 'Each operation needs a short unique id');
    requireThat(!ids.has(operation.id), 'INVALID_PLAN', `Duplicate operation id: ${operation.id}`);
    ids.add(operation.id);
    const slide = inventory.slides.find(s => s.slide === operation.slide);
    requireThat(Number.isInteger(operation.slide) && slide, 'UNKNOWN_SLIDE', `Unknown slide: ${operation.slide}`);
    const object = slide.objects.find(o => o.object_id === operation.object_id);
    requireThat(object, 'UNKNOWN_OBJECT', `Object ${operation.object_id} was not inspected on slide ${operation.slide}`);
    requireThat(object.supported_ops.includes(operation.op), 'UNSUPPORTED_OBJECT', `${operation.op} is not qualified for ${object.kind} ${operation.object_id}`);
    const editKey = `${operation.object_id}:${operation.op}`;
    requireThat(!edits.has(editKey), 'INVALID_PLAN', `Duplicate operation on the same object: ${editKey}`);
    edits.add(editKey);
    validatePosition(operation.expected_position, 'expected_position');
    requireThat(samePosition(operation.expected_position, object.position), 'GEOMETRY_MISMATCH', `Original geometry differs for ${operation.object_id}; inspect and plan again`);
    if (operation.op === 'move_resize') {
      validatePosition(operation.position);
      const p = operation.position;
      requireThat(p.left >= 0 && p.top >= 0 && p.left + p.width <= slide.width && p.top + p.height <= slide.height, 'OUT_OF_BOUNDS', `${operation.object_id} would extend outside slide ${operation.slide}`);
    } else {
      requireThat(typeof operation.font_size_pt === 'number' && Number.isFinite(operation.font_size_pt) && operation.font_size_pt >= 6 && operation.font_size_pt <= 144, 'INVALID_FONT_SIZE', 'font_size_pt must be a finite number from 6 to 144; visual readability still requires review');
    }
  }
  return plan;
}

/** Compare reimported native objects and geometry, in addition to the OOXML guard. */
export function compareInventories(before, after, operations = []) {
  const differences = [];
  if (before.slides.length !== after.slides.length) differences.push('Slide count changed');
  for (const original of before.slides) {
    const next = after.slides.find(s => s.slide === original.slide);
    if (!next) { differences.push(`Slide ${original.slide} disappeared`); continue; }
    if (original.slide_id !== next.slide_id || Math.abs(original.width-next.width)>0.02 || Math.abs(original.height-next.height)>0.02) differences.push(`Slide ${original.slide} identity or dimensions changed`);
    if (original.objects.length !== next.objects.length) differences.push(`Slide ${original.slide} object count changed`);
    if (original.objects.map(o => o.object_id).join('|') !== next.objects.map(o => o.object_id).join('|')) differences.push(`Slide ${original.slide} inspected object order changed`);
    for (const object of original.objects) {
      const actual = next.objects.find(o => o.object_id === object.object_id);
      if (!actual || actual.kind !== object.kind || actual.chart_type !== object.chart_type) {
        differences.push(`Object ${object.object_id} disappeared or changed native type`); continue;
      }
      const move = operations.find(o => o.object_id === object.object_id && o.op === 'move_resize');
      const font = operations.find(o => o.object_id === object.object_id && o.op === 'set_font_size');
      if (object.position && (!actual.position || !samePosition(move?.position ?? object.position, actual.position))) differences.push(`Object ${object.object_id} geometry differs from the plan`);
      if (object.kind === 'textbox' && object.font_size_pt !== null) {
        const expected = font?.font_size_pt ?? object.font_size_pt;
        if (actual.font_size_pt === null || Math.abs(expected-actual.font_size_pt)>0.02) differences.push(`Object ${object.object_id} font size differs from the plan`);
      }
    }
  }
  return { passed: differences.length === 0, differences };
}
