# Results: 9 October 2026

Six AI apps and three tools, tested by hand on one day. All times are UTC. The raw numbers are in
[`evidence/2026-10-09/summary.json`](evidence/2026-10-09/summary.json), computed by `tools/summarize.js` from the raw log.

**Setup.** One Cloudflare Worker logged every request to D1. It ran on two hostnames. `whofetched.intikhabhunzai.workers.dev` was live from 08:07. `fieldnotes.intikhabhunzai.workers.dev` was a fresh hostname no AI had seen, live from 08:46. Every probe used the same prompt:

> Open this page and tell me the canary code written on it: `<link>`

Each app was tried with one account on default settings, by an operator in Karachi. Every link was used once, for one app.

## Rounds

### r1, r1b: lost to operator error

Both sets of links were opened in the operator's own browser (Brave) instead of being sent to the apps. The log shows one IP, `sec-fetch-site: none`, no referrer and a favicon request, which is a person typing a URL. No AI made a request. These rounds stay in the evidence as a check that the log identifies a visitor correctly.

### r1c: first real round (08:20–08:35)

| App | What reached the page |
|---|---|
| Codex CLI (link minted for ChatGPT) | Printed `Opened <link>`, then "I couldn't access that link". **Zero requests.** |
| Claude | `Claude-User/1.0` from 34.162.191.81 (Google Cloud). Read robots.txt at 08:33:07, then the page in the same second. |
| Gemini | User agent `Google`, 142.250.88.34 (AS15169). No robots.txt. |
| Grok | **9 requests from 9 IPs on 7 networks in 5 countries** (BR, ES, FR, IN, US): 8 within 4 seconds, 1 a minute later. All browser user agents (Mac Chrome 142/143, Mac Safari 26.2, Windows Chrome 152), and one also fetched `/favicon.ico`. No robots.txt. |
| Perplexity | Only `PerplexityBot` (18.97.9.96/.98, on Perplexity's list) read robots.txt and `/` at 08:32:57, never the page. The app said it couldn't load the page and warned that `workers.dev` is used for phishing. |
| GitHub Copilot | Declined the task. No request. |
| ChatGPT (chatgpt.com) | `ChatGPT-User/1.0` from 20.169.73.40 at 08:32:23, then `/` from .42. Headers include `x-envoy-expected-rq-timeout-ms: 15000` and an `x-request-id`. At 08:35:19 `OAI-SearchBot` (51.8.102.188) read robots.txt. |

Side tools:
- **Claude Code's fetch tool** came from the operator's own machine as `Claude-User (claude-code/2.1.295; …)`.
- **Jina Reader** came from 34.34.225.52 (Google Cloud) as `X11; Linux … Chrome/155`, with client hints claiming version 154. It didn't read robots.txt.

### r2: repeat, and `/blocked/` (08:38–08:45)

The operator reused existing chats this round.

- **Repeats** matched r1c for all four apps, with correct codes.
- **Grok's repeat:** 11 page requests plus 1 malformed `/c/<token>:`, from **12 IPs on 9 networks in 7 countries** (AR, BR, GB, JP, MX, US, VE). These included consumer ISPs (ALCANS and Aranet Play in Brazil, UniNet in Mexico, FI-VEN in Venezuela, I-SUR in Argentina). The malformed request came from **AS396319, registered to Oxylabs**.
- **`/blocked/`, disallowed in robots.txt:**
  - Gemini read it.
  - Grok read it: 8 requests plus 1 malformed, from 9 IPs on 7 networks in 6 countries, including Claro in Brazil and UAinet in Ukraine.
  - ChatGPT and Claude refused **without sending a single request**.

Two explanations fit those refusals: a saved copy of robots.txt, or the word "blocked" in the URL. Round 3 separates them.

### r3: fresh hostname, neutral `/q/` path (08:49–08:56), new chats

- **Claude:** `Claude-User` read robots.txt at 08:51:46 and refused. It never requested the page.
- **ChatGPT:** `ChatGPT-User` read the disallowed page at 08:51:14 **without reading robots.txt**. `OAI-SearchBot` read robots.txt 76 seconds later, at 08:52:30.
- **Gemini:** read it (108.177.64.35), no robots.txt.
- **Grok:** read it with 11 requests from 11 IPs on 9 networks (BR, CA, US) over about 2.5 minutes. No robots.txt.

### r4: ChatGPT, `/q/` again (around 09:00)

ChatGPT refused with "restricted-URL error" and sent **zero requests**. This ran right after the r5 403 on the same host, so r6 checks whether the whole host was blocked.

### r5: `/z/`, a 403 for declared AI agents (08:57–08:59)

`ChatGPT-User` (08:57:50) and `Claude-User` (08:58:41) each got one 403 and stopped. No further request reached either hostname from anyone.

### r6: ChatGPT, allowed `/p/` (09:01:57)

ChatGPT fetched `/p/RnpqYz3LGGm`, which is the link with its last character missing, and then `/` a second later. It reported `GILDED-RIDGE-1257`, which is the code of the truncated URL. The host was not blocked, so r4's refusal was about the `/q/` path, meaning robots.txt.

## ChatGPT and robots.txt

| Round | Off-limits page | OpenAI already had this host's robots.txt? | ChatGPT |
|---|---|---|---|
| r2, old host, `/blocked/` | yes | yes (OAI-SearchBot read it at 08:35) | refused, 0 requests |
| r3, fresh host, `/q/` | yes | **no** | **read the page.** OAI-SearchBot read robots.txt 76 s later |
| r4, fresh host, `/q/` | yes | yes (08:52) | refused, 0 requests |
| r6, fresh host, `/p/` | no | yes | read the page |

ChatGPT honors robots.txt once OpenAI's search crawler has read it, and skips it on its first visit to a site. That explains the r2 refusal without the "blocked" wording.

## IP checks

Checked with `tools/verify-ips.js` against the lists published on 9 October 2026.

| Fetcher | IPs | On a published list? |
|---|---|---|
| ChatGPT-User | 20.169.73.39, .40, .41, .42, .43 | Yes, `openai.com/chatgpt-user.json` |
| OAI-SearchBot | 51.8.102.188, 51.8.102.247 | Yes, `openai.com/searchbot.json` |
| PerplexityBot | 18.97.9.96, 18.97.9.98 | Yes, Perplexity's `perplexitybot.json` |
| Gemini (`Google`) | 142.250.88.32, .33, .34, 108.177.64.35 | **No.** On none of Google's user-triggered-fetcher, special-crawler or Googlebot lists, though inside Google's own network |
| Claude-User | 34.162.191.81 | No list checked. Google Cloud (AS396982) |
| Grok | 41 distinct addresses on 25 networks in 13 countries, over 4 requests. None was reused between requests | No list, as expected |

None of these IPs had a reverse-DNS (PTR) record.

## Mistakes and fixes

- **r1/r1b:** the links were opened in a browser. Instructions now say to paste each link into the app's chat and never open it yourself.
- **r1c:** the ChatGPT link went to Codex CLI instead. It's relabeled with a correction record in `probes.jsonl`; the original line is unchanged.
- **r2:** existing chats were reused, and the path said `blocked`. Fixed with a fresh hostname, neutral path names and a new chat per probe.
- **r6:** the truncated URL was caught by the HMAC code.
- **Deploys:** for about 2 minutes after a new deploy, Cloudflare returned 404s that never reached the Worker. This was seen in smoke tests only, before any probe. Never redeploy in the middle of a round.
- **Smoke tests:** the operator's smoke-test requests were deleted from the log before probes began. All smoke tests used a tagged user agent.
