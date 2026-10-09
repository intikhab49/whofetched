// Turn a raw hits export (JSONL, one D1 row per line) into the public evidence file.
// Usage: WF_OPERATOR_IPS=<your ip>[,<ip>] node tools/redact.js <raw-hits.jsonl> <hits.redacted.jsonl>
//
// Full IPs are kept only for the big cloud and AI-company networks, where they identify a company, not a person.
// Everything else (proxy exits, home ISPs) is cut to /24 or /48, and the operator's own address becomes "operator".
const fs = require("fs");

const KEEP_FULL_ASN = new Set([8075, 15169, 396982, 14618, 16509]); // Microsoft, Google, Google Cloud, Amazon (x2)
const DROP_HEADERS = new Set(["cf-connecting-ip", "x-real-ip", "x-forwarded-for", "true-client-ip", "cf-ray", "cf-visitor", "cf-ipcountry", "cdn-loop", "cf-worker"]);
const operator = new Set((process.env.WF_OPERATOR_IPS || "").split(",").map((s) => s.trim()).filter(Boolean));

const [src, out] = process.argv.slice(2);
if (!src || !out) {
  console.error("usage: WF_OPERATOR_IPS=<ip> node tools/redact.js <raw-hits.jsonl> <hits.redacted.jsonl>");
  process.exit(1);
}

const prefix = (ip) =>
  ip.includes(":") ? `${ip.split(":").slice(0, 3).join(":")}::/48` : `${ip.split(".").slice(0, 3).join(".")}.0/24`;

const rows = fs.readFileSync(src, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const redacted = rows.map((r) => {
  const isOperator = operator.has(r.ip);
  const headers = {};
  for (const [k, v] of Object.entries(JSON.parse(r.headers_json || "{}"))) if (!DROP_HEADERS.has(k)) headers[k] = v;
  return {
    id: r.id,
    time: new Date(r.ts).toISOString(),
    host: r.host,
    method: r.method,
    path: r.path,
    mode: r.mode,
    token: r.token,
    status: r.status,
    ip: isOperator ? "operator" : KEEP_FULL_ASN.has(r.asn) ? r.ip : prefix(r.ip),
    asn: isOperator ? null : r.asn,
    as_org: isOperator ? null : r.as_org,
    country: isOperator ? null : r.country,
    colo: isOperator ? null : r.colo,
    http_protocol: r.http_protocol,
    tls_version: r.tls_version,
    ua: r.ua,
    headers,
  };
});

fs.writeFileSync(out, redacted.map((r) => JSON.stringify(r)).join("\n") + "\n");
const cut = redacted.filter((r) => r.ip.endsWith("/24") || r.ip.endsWith("/48")).length;
console.log(`${redacted.length} rows -> ${out}: ${redacted.filter((r) => r.ip === "operator").length} operator, ${cut} cut to a prefix, ${redacted.length - cut} kept in full or operator`);
