// Check logged IPs against the IP-range files AI operators publish for their crawlers and fetchers.
// Usage: node verify-ips.js <ip> [<ip> ...]
const LISTS = {
  "OpenAI ChatGPT-User": ["https://openai.com/chatgpt-user.json"],
  "OpenAI OAI-SearchBot": ["https://openai.com/searchbot.json"],
  "OpenAI GPTBot": ["https://openai.com/gptbot.json"],
  "Perplexity PerplexityBot": ["https://www.perplexity.com/perplexitybot.json", "https://www.perplexity.ai/perplexitybot.json"],
  "Perplexity Perplexity-User": ["https://www.perplexity.com/perplexity-user.json", "https://www.perplexity.ai/perplexity-user.json"],
  "Google user-triggered fetchers": ["https://developers.google.com/static/search/apis/ipranges/user-triggered-fetchers-google.json"],
  "Google user-triggered fetchers (other)": ["https://developers.google.com/static/search/apis/ipranges/user-triggered-fetchers.json"],
  "Google special crawlers": ["https://developers.google.com/static/search/apis/ipranges/special-crawlers.json"],
  "Googlebot": ["https://developers.google.com/static/search/apis/ipranges/googlebot.json"],
  "Bingbot": ["https://www.bing.com/toolbox/bingbot.json"],
};

const toInt = (ip) => ip.split(".").reduce((a, o) => (a << 8) + Number(o), 0) >>> 0;
function inCidr(ip, cidr) {
  const [base, bits] = cidr.split("/");
  const mask = Number(bits) === 0 ? 0 : (~0 << (32 - Number(bits))) >>> 0;
  return (toInt(ip) & mask) === (toInt(base) & mask);
}

async function load(urls) {
  for (const u of urls) {
    try {
      const r = await fetch(u, { headers: { accept: "application/json" } });
      if (!r.ok) continue;
      const j = await r.json();
      const prefixes = (j.prefixes || []).map((p) => p.ipv4Prefix).filter(Boolean);
      return { url: u, prefixes, stamp: j.creationTime || j.updated || null };
    } catch {}
  }
  return null;
}

(async () => {
  const ips = process.argv.slice(2);
  for (const [name, urls] of Object.entries(LISTS)) {
    const list = await load(urls);
    if (!list) { console.log(`${name.padEnd(40)} list unavailable`); continue; }
    const hits = ips.filter((ip) => list.prefixes.some((c) => inCidr(ip, c)));
    console.log(`${name.padEnd(40)} ${String(list.prefixes.length).padStart(4)} ranges  ${hits.length ? "MATCH: " + hits.join(", ") : "-"}`);
  }
})();
