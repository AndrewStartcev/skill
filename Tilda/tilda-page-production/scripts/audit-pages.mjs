#!/usr/bin/env node
/**
 * Read-only published-page audit for Tilda (or another public HTML website).
 * Node.js 18+, no packages and no authentication required.
 *
 * Usage:
 *   node scripts/audit-pages.mjs assets/page-matrix.example.json
 *
 * Only pages with "publish": true are checked. Nothing is modified.
 * Static HTML heuristics do not replace visual/browser QA.
 */
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

function getFlag(re, html) {
  const match = re.exec(html);
  return match ? match[1].replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim() : '';
}

function readMeta(html, name) {
  const tags = html.match(/<meta\b[^>]*>/gi) ?? [];
  for (const tag of tags) {
    const attrs = Object.fromEntries(
      [...tag.matchAll(/([a-zA-Z:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g)]
        .map(m => [m[1].toLowerCase(), m[2] ?? m[3] ?? m[4]])
    );
    if ((attrs.name || '').toLowerCase() === name.toLowerCase()) return attrs.content || '';
  }
  return '';
}

function toUrl(path, base) {
  const u = new URL(path, base);
  if (!['https:', 'http:'].includes(u.protocol)) throw Error('Only HTTP(S) URLs supported');
  return u;
}

function normalizeUrl(path, base) {
  const url = toUrl(path, base);
  url.hash = '';
  url.search = '';
  const pathname = url.pathname.replace(/\/+$/, '') || '/';
  return url.origin + pathname;
}

function linkSet(html, base) {
  const urls = new Set();
  const tags = html.match(/<a\b[^>]*>/gi) ?? [];
  for (const tag of tags) {
    const match = /\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(tag);
    if (!match) continue;
    const raw = match[1] ?? match[2] ?? match[3];
    if (!raw || raw.startsWith('#') || /^(?:mailto|tel|javascript):/i.test(raw)) continue;
    try { urls.add(normalizeUrl(raw, base)); } catch { /* Ignore invalid external schemes. */ }
  }
  return urls;
}

function expectObject(obj, label) {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) throw Error(label + ' must be an object');
}

async function audit(manifestFile, options = {}) {
  const raw = await readFile(manifestFile, 'utf8');
  const manifest = JSON.parse(raw);
  expectObject(manifest, 'Manifest');
  if (typeof manifest.baseUrl !== 'string') throw Error('baseUrl must be a string');
  if (!Array.isArray(manifest.pages)) throw Error('pages must be an array');
  const base = toUrl(manifest.baseUrl);
  if (!['https:', 'http:'].includes(base.protocol)) throw Error('Invalid baseUrl');
  const timeoutMs = options.timeoutMs ?? 15000;

  const visited = new Set();
  let tested = 0;
  let failed = 0;
  let warningsCount = 0;

  for (const item of manifest.pages) {
    expectObject(item, 'Each pages[] entry');
    if (!item.publish) continue;
    if (typeof item.path !== 'string') throw Error('Published page missing path');
    const url = toUrl(item.path, base);
    if (url.origin !== base.origin) throw Error('Out-of-site page not allowed: ' + url.href);
    const key = normalizeUrl(url.href, base);
    if (visited.has(key)) throw Error('Duplicate page in manifest: ' + key);
    visited.add(key);
    tested++;
    const problems = [];
    const warnings = [];
    let status = 'NETWORK_ERROR';

    try {
      const response = await fetch(url, {
        redirect: 'follow',
        signal: AbortSignal.timeout(timeoutMs),
        headers: { 'User-Agent': 'TildaPublishedPageAudit/1.0' }
      });
      status = String(response.status);
      if (!response.ok) problems.push('HTTP ' + response.status);
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.toLowerCase().includes('text/html')) {
        problems.push('Not HTML (' + (contentType || 'unknown content-type') + ')');
      } else {
        const html = await response.text();
        const title = getFlag(/<title\b[^>]*>([\s\S]*?)<\/title>/i, html);
        const h1Tags = [...html.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)];
        const h1Text = h1Tags.map(m => m[1].replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim());
        const description = readMeta(html, 'description');
        const robots = readMeta(html, 'robots');

        if (!title) problems.push('Missing title');
        if (!description) warnings.push('Missing meta description');
        if (h1Tags.length !== 1) warnings.push('Expected 1 H1, got ' + h1Tags.length);
        if (/\bnoindex\b/i.test(robots) || /\bnoindex\b/i.test(response.headers.get('x-robots-tag') || '')) {
          warnings.push('Page is marked noindex');
        }
        if (item.expectedH1 && !h1Text.includes(item.expectedH1)) {
          warnings.push('H1 differs from manifest; got: ' + JSON.stringify(h1Text));
        }
        if (item.expectedTitleContains && !title.includes(item.expectedTitleContains)) {
          warnings.push('Title does not contain expected text: ' + item.expectedTitleContains);
        }
        if (Array.isArray(item.requiredLinks)) {
          const links = linkSet(html, response.url);
          for (const target of item.requiredLinks) {
            if (!links.has(normalizeUrl(target, base))) {
              warnings.push('Missing required link: ' + target);
            }
          }
        }
        if (new URL(response.url).origin !== base.origin) {
          warnings.push('Redirected away from expected origin: ' + response.url);
        }
      }
    } catch (err) {
      problems.push('Fetch failed: ' + (err?.message || String(err)));
    }

    if (problems.length) failed++;
    warningsCount += warnings.length;
    console.log('[' + (problems.length ? 'FAIL' : warnings.length ? 'WARN' : 'OK') + '] ' + status + ' ' + url.href);
    for (const p of problems) console.log('  ERROR: ' + p);
    for (const w of warnings) console.log('  WARN: ' + w);
  }

  console.log('\nPublished pages checked: ' + tested + ', failed: ' + failed + ', warnings: ' + warningsCount);
  if (tested === 0) {
    console.error('No publish:true pages in manifest');
    return 2;
  }
  return failed ? 1 : 0;
}

const entry = process.argv[1] ? pathToFileURL(process.argv[1]).href : '';
if (entry === import.meta.url) {
  const file = process.argv[2];
  if (!file) {
    console.error('Usage: node scripts/audit-pages.mjs path/to/page-matrix.json');
    process.exitCode = 2;
  } else {
    audit(file)
      .then(code => { process.exitCode = code; })
      .catch(err => { console.error('Audit error:', err?.message || String(err)); process.exitCode = 2; });
  }
}

export { audit };
