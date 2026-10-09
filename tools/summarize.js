// Per-probe numbers for the write-up and charts. Reads the RAW hits so distinct-IP counts are exact,
// but writes only aggregates (no IPs) to the summary file, so the summary is safe to publish.
// Usage: node tools/summarize.js <raw-hits.jsonl> <probes.jsonl> <answers.jsonl> <summary.json>
const fs = require("fs");

const [rawPath, probesPath, answersPath, outPath] = process.argv.slice(2);
const readJsonl = (p) => fs.readFileSync(p, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const hits = readJsonl(rawPath);
const lines = readJsonl(probesPath);
const answers = readJsonl(answersPath);

function uaKind(ua) {
  if (!ua) return "none";
  if (/claude-code/.test(ua)) return "Claude-User (Claude Code)";
  for (const t of ["ChatGPT-User", "OAI-SearchBot", "GPTBot", "Claude-User", "ClaudeBot", "PerplexityBot", "Perplexity-User"]) if (ua.includes(t)) return t;
  if (ua === "Google") return "Google (bare)";
  if (/^Mozilla\/5\.0 \(/.test(ua)) return "browser-like, no bot token";
  return ua.slice(0, 40);
}

const probes = lines.filter((l) => !l.type).map((p) => {
  const fix = lines.find((l) => l.type === "correction" && l.token === p.token);
  const fetchedToken = fix?.fetched_token || p.token;
  const page = hits.filter((h) => h.token === fetchedToken);
  const malformed = hits.filter((h) => h.token !== fetchedToken && String(h.path).includes(p.token));
  const all = [...page, ...malformed];
  const ans = answers.find((a) => a.token === p.token);
  const expected = fix?.fetched_expected_code || p.expected_code;
  return {
    round: p.round, mode: p.mode, host: p.url.split("/")[2], product: fix?.product || p.product, minted_as: fix ? p.product : undefined,
    token: p.token, fetched_token: fetchedToken !== p.token ? fetchedToken : undefined,
    page_requests: page.length, malformed_requests: malformed.length,
    distinct_ips: new Set(all.map((h) => h.ip)).size,
    distinct_asns: new Set(all.map((h) => h.asn)).size,
    countries: [...new Set(all.map((h) => h.country))].sort(),
    statuses: [...new Set(all.map((h) => h.status))].sort(),
    ua_kinds: [...new Set(all.map((h) => uaKind(h.ua)))],
    first: all.length ? new Date(Math.min(...all.map((h) => h.ts))).toISOString() : null,
    last: all.length ? new Date(Math.max(...all.map((h) => h.ts))).toISOString() : null,
    reply: ans?.reply ?? null,
    reply_code: ans?.code ?? null,
    code_check: ans?.code ? (ans.code === expected ? "match" : "mismatch") : null,
    note: ans?.note,
  };
});

const robots = hits.filter((h) => h.mode === "robots").map((h) => ({
  time: new Date(h.ts).toISOString(), host: h.host, ua_kind: uaKind(h.ua), asn: h.asn, as_org: h.as_org,
}));

const summary = { generated_at: new Date().toISOString(), source_rows: hits.length, probes, robots };
fs.writeFileSync(outPath, JSON.stringify(summary, null, 2) + "\n");

for (const p of probes) {
  console.log(`${p.round.padEnd(4)} ${("/" + p.mode + "/").padEnd(10)} ${p.product.padEnd(20)} req=${String(p.page_requests).padStart(2)}${p.malformed_requests ? "+" + p.malformed_requests : "  "} ips=${String(p.distinct_ips).padStart(2)} asns=${String(p.distinct_asns).padStart(2)} cc=${p.countries.join(",").padEnd(18)} ${p.statuses.join(",").padEnd(7)} ${p.ua_kinds.join(" | ").padEnd(28)} code=${p.code_check ?? "-"}`);
}
console.log(`robots.txt reads: ${robots.map((r) => `${r.time.slice(11, 19)} ${r.ua_kind}`).join("; ")}`);
