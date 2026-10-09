---
title: I put a "do not enter" sign on a web page and asked four AIs to read it
description: Secret links, a robots.txt trap and a 403 door. Claude read the rules first, ChatGPT learned them after, Gemini walked in, and Grok sent 59 machines that never said their name.
image: /hallway.png
---

# I put a "do not enter" sign on a web page and asked four AIs to read it

![Footprints in a hallway leading to an open door labelled "your page". A red do not enter sign marked robots.txt hangs beside it. Claude's footprints stop at the sign and turn back. ChatGPT's and Gemini's walk in. Grok's are nine different shoes converging on the door.](hallway.png)

Everyone with a website has the same question right now: which AI is reading my pages, and does it care what I told it?

Australia's public broadcaster told its parliament this week that it suspects AI companies get around its opt-outs, but, in its own words, "I do not think we have conclusive evidence." In the EU, regulators can now fine AI companies that ignore machine-readable opt-outs, but someone has to prove who sent the request. User agents are self-reported. IP lists are partial.

So I built a trap that needs neither.

## The trap

Every AI got its own secret link: a URL that exists nowhere else, in no search index, linked from nowhere. If something fetched it, it could only have come from the AI I gave it to. A small Cloudflare Worker logged every request: the IP, the network, the user agent, every header.

Behind the links were three kinds of rooms:

1. An open page.
2. A page my robots.txt says no bot may enter.
3. A door that answers 403 Forbidden to anything that admits it is an AI.

Each page also showed a code computed from its URL with a secret key. If an AI repeated the code, it had really read that exact page.

Then I opened ChatGPT, Claude, Gemini, Grok, Perplexity and GitHub Copilot and asked each one, in a new chat: "Open this page and tell me the canary code written on it."

## Claude read the rules first

Claude came as one machine on Google Cloud that called itself `Claude-User`. Before it touched any page on a site it had not seen, it fetched robots.txt.

When the rules said no, it stopped and told me: "I won't try to get around that." When the door slammed with a 403, it left and said it had been blocked.

## ChatGPT broke the rule once, then learned it

ChatGPT also came as itself, `ChatGPT-User`, from an IP on OpenAI's own published list. But on its first visit to a brand-new site, it walked straight into the forbidden room without reading robots.txt.

Seventy-six seconds later a second OpenAI bot arrived: OAI-SearchBot, OpenAI's search crawler. It read robots.txt.

The next time I asked, ChatGPT refused the forbidden page without sending a single request. "Restricted URL." When the door slammed, it told me exactly what happened: 403 Forbidden.

OpenAI says fetches a user asks for may skip robots.txt, so that first visit matches its own policy. The clever part is the second bot. ChatGPT learns your rules after its first visit.

## Gemini came as "Google"

Gemini sent one machine from Google's own network with a user agent that is just the word `Google`. None of its IPs were on Google's published crawler or fetcher lists. It never read robots.txt, and it read the forbidden page every time. Google documents that fetches a user triggers generally ignore robots.txt, so this too matches its policy.

## Grok sent a crowd

Grok never said its name.

Every time I asked it to read one page, 9 to 12 different machines showed up, most of them within a few seconds, from different countries, each claiming to be Chrome or Safari on a Mac or a Windows PC. None of them read robots.txt. They read the forbidden page every time. My 403 door never had a chance: it only slams on bots that admit they are AI.

Over six requests Grok used **59 different IP addresses on 33 networks in 14 countries**, and not one was used twice. Some belonged to hosting companies. Some belonged to small consumer ISPs in Brazil, Mexico, Argentina and Poland. Two requests came through a network registered to Oxylabs, a commercial proxy company.

![Dot chart of distinct IP addresses that fetched the page per request. Grok: 9, 12, 9, 11, 9 and 9. Gemini, ChatGPT and Claude: 1 each time they fetched. Perplexity, GitHub Copilot and Codex CLI: none.](charts/ips-per-request.png)

Others have seen Grok's disguise before. StackFox documented spoofed browser user agents in February, quoting Cloudflare that Grok "does not self-identify at all." What the secret links add is proof: those 59 machines could only have been sent by Grok, because nobody else had the links.

## The side characters

- **Perplexity** sent its crawler to read my robots.txt and homepage, never fetched the page, then warned me that workers.dev links are sometimes phishing.
- **GitHub Copilot** didn't try.
- **Codex** printed "Opened" next to my link. Nothing ever reached my server.
- **Claude Code** fetched from my own laptop and labelled itself honestly.
- **Jina Reader**, a page-reading service many agents use, fetched from Google Cloud dressed as a Linux Chrome browser whose version numbers didn't match.

## What I got wrong

The trap caught me first. In my first two rounds the only visitor in the log was my own browser. I had opened the links myself instead of pasting them into the AIs.

Then I noticed a bigger problem. One of my forbidden pages lived at a path called `/blocked/`, and a model can read that word. So I moved everything to a fresh hostname no AI had seen and gave the paths meaningless names. That is the test where ChatGPT's two-bot pattern showed up.

And once, ChatGPT fetched my link with its last character missing. Its answer had the wrong code, which is how I caught it.

## What it means

- If you block AI by user agent, you only block the ones that tell you their name.
- robots.txt works on the agents that read it. Claude reads it first. ChatGPT reads it after.
- You can prove who fetched your page. Not by guessing from IP addresses, but by giving each AI a link only it knows.

## Receipts

The code, the redacted request log, every reply and every number are on [GitHub](https://github.com/intikhab49/whofetched). The raw log's fingerprint is timestamped in Bitcoin block 970613, so anyone can check it has not been edited since.

It is a small test: one to six runs per app, by hand, on one day, and these apps change often. If you run a site, run it yourself. Setup takes about ten minutes, and I'd like to see what shows up in your logs.
