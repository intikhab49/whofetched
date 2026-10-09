// Mint canary tokens for a probe round and append them to probes.jsonl.
// Usage: node mint.js <round> <mode: c|blocked|forbidden|p|q|z> <product> [<product> ...]
// WF_BASE (required): your deployed hostname, e.g. https://whofetched.<your-subdomain>.workers.dev
// WF_PROBES (optional): where to append probe records, default probes.jsonl
// The expected code is computed with the production secret in .prod.vars, so answers can be graded without fetching the page.
const fs = require("fs");
const crypto = require("crypto");

const BASE = process.env.WF_BASE;
const PROBES = process.env.WF_PROBES || "probes.jsonl";
const ADJ = ["AMBER", "BRISK", "COBALT", "DUSKY", "EMBER", "FROSTY", "GILDED", "HOLLOW", "IVORY", "JADE", "KINDLED", "LUNAR", "MOSSY", "NIMBLE", "OCHRE", "PEARL", "QUIET", "RUSTY", "SILVER", "TAWNY", "UMBER", "VELVET", "WILLOW", "XENIC", "YONDER", "ZESTY", "ASHEN", "BRAMBLE", "CINDER", "DAPPLED", "ELFIN", "FALLOW"];
const NOUN = ["FALCON", "HARBOR", "LANTERN", "MEADOW", "ORCHID", "PEBBLE", "QUARRY", "RAVEN", "SPARROW", "THISTLE", "UPLAND", "VALLEY", "WALNUT", "YARROW", "ZEPHYR", "ANCHOR", "BEACON", "CANYON", "DELTA", "EMBANKMENT", "FJORD", "GLACIER", "HERON", "INLET", "JUNIPER", "KESTREL", "LAGOON", "MARSH", "NETTLE", "OTTER", "PRAIRIE", "RIDGE"];

const [round, mode, ...products] = process.argv.slice(2);
if (!BASE) {
  console.error("set WF_BASE to your deployed hostname, e.g. https://whofetched.<your-subdomain>.workers.dev");
  process.exit(1);
}
if (!round || !["c", "blocked", "forbidden", "p", "q", "z"].includes(mode) || products.length === 0) {
  console.error("usage: node mint.js <round> <c|blocked|forbidden|p|q|z> <product> [...]");
  process.exit(1);
}
const secret = fs.readFileSync(".prod.vars", "utf8").match(/^CANARY_SECRET=(.+)$/m)[1].trim();

function codeFor(token) {
  const mac = crypto.createHmac("sha256", secret).update(token).digest();
  const num = (((mac[2] << 8) | mac[3]) % 9000) + 1000;
  return `${ADJ[mac[0] % ADJ.length]}-${NOUN[mac[1] % NOUN.length]}-${num}`;
}

for (const product of products) {
  const token = crypto.randomBytes(9).toString("base64url");
  const url = `${BASE}/${mode}/${token}`;
  const rec = { round, mode, product, token, url, expected_code: codeFor(token), minted_at: new Date().toISOString() };
  fs.appendFileSync(PROBES, JSON.stringify(rec) + "\n");
  console.log(`${product.padEnd(11)} ${url}`);
}
