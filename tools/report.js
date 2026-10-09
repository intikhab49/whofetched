// Join logged hits to minted probes and print who fetched each canary URL.
// Usage: node report.js <hits.json from `wrangler d1 execute --json`> [answers.json: {"<product>": "<code it gave>"}] [round]
const fs = require("fs");

const hits = JSON.parse(fs.readFileSync(process.argv[2], "utf8"))[0].results;
const lines = fs.readFileSync(process.env.WF_PROBES || "probes.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l));
// Correction records ({"type":"correction","token","product","note"}) relabel a probe without rewriting the original line.
const probes = lines.filter((l) => !l.type).map((p) => {
  const fix = lines.find((l) => l.type === "correction" && l.token === p.token);
  return fix ? { ...p, product: `${fix.product} (minted as ${p.product})` } : p;
});
const answers = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], "utf8")) : {};
const round = process.argv[4];
const utc = (ts) => new Date(ts).toISOString().replace("T", " ").slice(0, 19);

for (const p of probes.filter((p) => !round || p.round === round)) {
  const hs = hits.filter((h) => h.token === p.token);
  const got = answers[p.product];
  const verdict = got == null ? "" : got === p.expected_code ? "code MATCH" : `code MISMATCH (got ${got}, expected ${p.expected_code})`;
  console.log(`\n== ${p.round} /${p.mode}/ ${p.product}  minted ${utc(Date.parse(p.minted_at))} UTC  ${verdict}`);
  if (hs.length === 0) console.log("   no fetches logged");
  for (const h of hs) {
    const signed = h.signature_agent ? `  [signed by ${h.signature_agent}]` : "";
    console.log(`   ${utc(h.ts)}  ${h.status}  ${h.ip}  AS${h.asn} ${h.as_org}  ${h.country}/${h.colo}  ${h.http_protocol}  ua=${(h.ua || "").slice(0, 100)}${signed}`);
  }
}

const other = hits.filter((h) => !probes.some((p) => p.token === h.token));
console.log(`\n== other requests (${other.length})`);
for (const h of other) {
  console.log(`   ${utc(h.ts)}  ${h.status}  ${String(h.mode).padEnd(9)} ${String(h.path).slice(0, 36).padEnd(36)} ${h.ip}  AS${h.asn} ${h.as_org}  ${h.country}  ua=${(h.ua || "").slice(0, 80)}`);
}
