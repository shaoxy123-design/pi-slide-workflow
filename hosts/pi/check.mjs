// Offline metadata preflight. Reads Pi model definitions, never its auth store.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

async function loadPiCompat(packageDir) {
  const packageRequire = createRequire(path.join(packageDir, 'package.json'));
  let compatPath;
  try { compatPath = packageRequire.resolve('@earendil-works/pi-ai/compat'); }
  catch (error) {
    if (error.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error;
    // Pi 0.84 uses an import-only export. Follow Node's package search order,
    // then import that package's declared ESM export instead of guessing a path.
    for (const modulesDir of packageRequire.resolve.paths('@earendil-works/pi-ai/compat') ?? []) {
      const aiDir = path.join(modulesDir, '@earendil-works/pi-ai');
      let manifest;
      try { manifest = JSON.parse(await fs.readFile(path.join(aiDir, 'package.json'), 'utf8')); }
      catch (readError) { if (readError.code === 'ENOENT') continue; throw readError; }
      const entry = manifest.exports?.['./compat'];
      const target = typeof entry === 'string' ? entry : entry?.import;
      if (manifest.name !== '@earendil-works/pi-ai' || typeof target !== 'string') throw new Error('Pi compatibility export is unavailable.');
      compatPath = path.resolve(aiDir, target);
      break;
    }
  }
  if (!compatPath) throw new Error('Pi compatibility package is unavailable.');
  return import(pathToFileURL(compatPath).href);
}

const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) {
  if (!['--pi-package', '--provider', '--thinking', '--main-model'].includes(args[i]) || !args[i + 1] || options[args[i]]) {
    process.stderr.write('Usage: node hosts/pi/check.mjs --pi-package PACKAGE_DIRECTORY --provider PROVIDER [--main-model glm-5.3-flash|glm-5.3] [--thinking low|high|max]\n');
    process.exit(2);
  }
  options[args[i]] = args[i + 1];
}
const report = { check: 'OFFLINE_LOCAL_MODEL_METADATA_AND_SDK', ready: false, auth_store_accessed: false,
  network_used: false, authentication_tested: false, inference_tested: false,
  configured_user_catalog_checked: false, authoring_or_rendering_tested: false,
  selected_thinking: options['--thinking'] ?? 'high', main_model: options['--main-model'] ?? 'glm-5.3-flash' };
try {
  if (!options['--pi-package'] || !/^[a-zA-Z0-9_-]+$/.test(options['--provider'] ?? '')) throw new Error('Package directory and provider are required.');
  if (!['low', 'high', 'max'].includes(report.selected_thinking)) throw new Error('Thinking must be low, high or max.');
  if (!['glm-5.3-flash', 'glm-5.3'].includes(report.main_model)) throw new Error('Main model must be exact glm-5.3-flash or glm-5.3.');
  const packageDir = path.resolve(options['--pi-package']);
  const manifest = JSON.parse(await fs.readFile(path.join(packageDir, 'package.json'), 'utf8'));
  if (manifest.name !== '@earendil-works/pi-coding-agent') throw new Error('Expected the installed Pi coding-agent package.');
  report.pi_version = manifest.version;
  report.provider = options['--provider'];
  const sdk = await import(pathToFileURL(path.join(packageDir, 'dist/index.js')).href);
  const { getSupportedThinkingLevels } = await loadPiCompat(packageDir);
  if (typeof getSupportedThinkingLevels !== 'function') throw new Error('Native thinking capability inspection is unavailable.');
  report.sdk_exports_present = ['createAgentSession', 'createExtensionRuntime', 'ModelRuntime', 'SettingsManager', 'SessionManager'].every(name => typeof sdk[name] === 'function');
  const forbiddenAuth = async () => { report.auth_store_accessed = true; throw new Error('Auth access is prohibited in an offline metadata check.'); };
  const runtime = await sdk.ModelRuntime.create({
    credentials: { read: forbiddenAuth, list: forbiddenAuth, modify: forbiddenAuth, delete: forbiddenAuth },
    allowModelNetwork: false, refreshOnCreate: false,
  });
  report.configured_user_catalog_checked = true;
  report.model_config_valid = !runtime.getError();
  const requiredModels = [...new Set([report.main_model, 'glm-5.3-flash'])];
  report.models = requiredModels.map(id => {
    const model = runtime.getModel(report.provider, id);
    return { id, found: Boolean(model), input: model?.input ?? [], reasoning: model?.reasoning ?? false,
      supported_thinking: model ? getSupportedThinkingLevels(model) : [] };
  });
  report.ready = report.sdk_exports_present && report.model_config_valid
    && report.models.every(m => m.found && m.reasoning && m.input.includes('text') && m.supported_thinking.includes(report.selected_thinking))
    && report.models.find(m => m.id === 'glm-5.3-flash')?.input.includes('image');
  if (!report.ready) report.blocker = 'Required SDK/model metadata is missing or invalid, or the exact requested thinking level is unsupported. No model substitution, thinking downgrade or configuration update was performed.';
  report.note = 'Checks bundled models plus the native local model definitions, without network refresh or auth resolution. Does not establish provider access, image inference, or provider-side thinking effort.';
} catch (error) {
  // Do not print arbitrary provider/config content or environment values.
  report.blocker = `Offline package inspection failed (${error.code ?? error.name ?? 'unknown'}). Check package path and provider compatibility.`;
}
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
process.exitCode = report.ready ? 0 : 2;
