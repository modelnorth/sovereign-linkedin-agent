---
name: sovereign-linkedin-agent
description: >-
  Autonomous, Anti-Ban LinkedIn Intelligence & Sovereign Growth Engine by ModelNorth (modelnorth.com).
  Controls live authenticated Brave/Chrome browser over CDP or executes programmatic MCP graph queries
  to scout enterprise leads, score decision makers, synthesize high-status sovereign AI outreach,
  publish company page updates, and manage LinkedIn inboxes with zero-ban telemetry.
triggers:
  - linkedin
  - /linkedin
  - linkedin agent
  - modelnorth linkedin
  - linkedin outreach
  - linkedin scout
  - linkedin company post
  - sovereign linkedin
---

# 🛡️ ModelNorth Sovereign LinkedIn Agent

The **ModelNorth Sovereign LinkedIn Agent** is an autonomous, open-source intelligence and growth engine created by **ModelNorth** ([modelnorth.com](https://modelnorth.com)). It bridges programmatic Model Context Protocol (MCP) tools with an authentic, anti-ban Chrome DevTools Protocol (CDP) stealth browser.

Official Website: [https://modelnorth.com](https://modelnorth.com)  
License: **ModelNorth Sovereign Open License (MN-SL v1.0)**

---

## ⚡ Key Capabilities

1. **Anti-Ban Perimeter Defense (Stealth CDP):**
   - Attaches to your authentic, locally signed-in Brave or Chrome browser (`http://127.0.0.1:9222`).
   - Strips `navigator.webdriver`, masks WebGL/Canvas fingerprinting, and cleans CDP runtime flags.
   - Injects stochastic Bezier curve mouse paths and Gaussian keystroke cadences.
2. **High-Ticket ICP Lead Matrix:**
   - Evaluates executives (CTOs, CISOs, Heads of AI, Managing Directors) across the GCC and global enterprise.
   - Computes an autonomous 0–100 Seniority and Sovereignty Alignment Score.
   - Exports clean deduplicated CSV and JSON dossiers.
3. **OpenTelemetry Observability:**
   - Instruments every browser action, governor check, and publication step with standard distributed spans.
   - Records latency (ms), token accounting, and execution proof into an append-only sovereign flight ledger (`otel_traces.jsonl`).
4. **Autonomous Content Queue & Publishing Scheduler:**
   - Manages structured content calendar with scheduled publishing dates and rich media attachments.
   - Auto-publishes queued thought leadership updates with human typing cadence and proof logging.
5. **Contextual Sovereign Outreach Synthesizer:**
   - Synthesizes personalized connection notes strictly under LinkedIn's 300-character cap.
   - Generates high-status, non-salesy technical peer InMails highlighting on-prem LLMs, custom MCP servers, and air-gapped data sovereignty.
4. **Autonomous Company Page Pilot:**
   - Publishes thought-leadership posts, image graphics, and PDF carousels directly to the ModelNorth Company Page feed.
5. **Deterministic Safety Governor:**
   - Enforces strict daily limits (25 invites, 40 messages, 80 profile views).
   - Pauses execution during off-peak curfew hours to mimic realistic executive working patterns.

---

## 🛠️ CLI Quickstart

Run commands from the repository or agent workspace:

```bash
# Check status and CDP connectivity
python -m sovereign_linkedin.cli status

# Launch Brave in anti-ban CDP debugging mode
python -m sovereign_linkedin.cli launch-browser

# Scout enterprise leads in Dubai / GCC (offline evaluation)
python -m sovereign_linkedin.cli scout --role "Chief Technology Officer" --location "Dubai, UAE" --limit 15

# Live Anti-Ban Browser Lead Scraper over CDP
python -m sovereign_linkedin.cli scout --role "Chief Technology Officer" --location "Dubai, UAE" --limit 20 --live --export-csv

# View content calendar queue
python -m sovereign_linkedin.cli queue

# Publish the next pending post from queue (with OpenTelemetry tracing)
python -m sovereign_linkedin.cli publish-next --force

# Inspect recent OpenTelemetry distributed traces & latencies
python -m sovereign_linkedin.cli traces --limit 10

# Synthesize personalized connection note and direct message
python -m sovereign_linkedin.cli synthesize --name "Faisal Al-Otaibi" --company "Sovereign Cloud" --headline "VP of Engineering" --angle sovereign

# Publish technical update to ModelNorth Company Page
python -m sovereign_linkedin.cli post-company --text "Announcing ModelNorth Sovereign Agent OS..." --media "assets/modelnorth-emblem.svg"
```

---

## 🔒 Invariants & Safety Rules

1. **Zero-Trust Credential Security:** Never enter or log your LinkedIn password in code. All actions execute through your authentic local session.
2. **Never Exceed Hard Limits:** The Safety Governor halts automation if daily invite (25) or message (40) caps are reached.
3. **Active Working Hours Only:** The agent will pause if local system time is outside 08:00 – 20:00 to prevent night-time bot detection flags.
