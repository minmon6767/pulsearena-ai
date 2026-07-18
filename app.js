// app.js — PulseArena AI frontend
//
// Bootstraps the shared context graph once on page load, then wires up
// each tab to its agent. Every button click is just: read state off the
// graph, call the agent, render whatever comes back (live GenAI text or
// the fallback — the UI doesn't really care which, it just shows a small
// flag either way).

import { StadiumContextGraph } from "./core/contextGraph.js";
import { SUPPORTED_LANGUAGES } from "./core/i18n.js";
import { askWayfinder } from "./agents/wayfinder.js";
import { crowdMarshalBriefing } from "./agents/crowdMarshal.js";
import { accessCompanionAssist } from "./agents/accessCompanion.js";
import { greenRouteRecommend } from "./agents/greenRoute.js";
import { opsSituationReport } from "./agents/opsCommander.js";

const graph = new StadiumContextGraph(42);

const EXAMPLE_QUESTIONS = [
  "Where's the nearest accessible restroom?",
  "Which gate has the shortest line right now?",
  "Is there somewhere quiet I can pray before the match?",
  "Where can I refill my water bottle?",
];

async function main() {
  await graph.bootstrap();
  await checkGenaiStatus();
  renderSidebarFacts();
  renderExampleChips();
  populateLanguageSelect();
  renderGateTable();
  renderTransitTable();
  renderIncidentLog();
  wireTabs();
  wireButtons();
}

// ---------------------------------------------------------------------
// GenAI status check — a cheap way to tell the user up front whether
// they're looking at live model output or the offline fallback path.
// ---------------------------------------------------------------------
async function checkGenaiStatus() {
  const pill = document.getElementById("genaiStatus");
  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ systemPrompt: "ping", userPrompt: "Reply with the single word: ok", maxTokens: 10 }),
    });
    const data = res.ok ? await res.json() : { live: false };
    if (data.live) {
      pill.textContent = "GenAI: LIVE (Claude API connected)";
      pill.className = "status-pill status-live";
    } else {
      pill.textContent = "GenAI: Offline fallback mode — add ANTHROPIC_API_KEY in Netlify to enable live responses.";
      pill.className = "status-pill status-offline";
    }
  } catch {
    pill.textContent = "GenAI: Offline fallback mode (no function reachable — expected if running without Netlify).";
    pill.className = "status-pill status-offline";
  }
}

function renderSidebarFacts() {
  document.getElementById("factVenue").textContent = graph.venue.venue_name || "—";
  document.getElementById("factMatch").textContent = graph.venue.match || "—";
  document.getElementById("factWeather").textContent = `${graph.weather.condition}, ${graph.weather.tempC}°C`;
  document.getElementById("factTick").textContent = graph.tick;
}

function renderExampleChips() {
  const row = document.getElementById("exampleQuestions");
  row.innerHTML = "";
  for (const q of EXAMPLE_QUESTIONS) {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.type = "button";
    chip.textContent = q;
    chip.addEventListener("click", () => {
      document.getElementById("fanQuestion").value = q;
    });
    row.appendChild(chip);
  }
}

function populateLanguageSelect() {
  const select = document.getElementById("languageSelect");
  select.innerHTML = "";
  for (const lang of SUPPORTED_LANGUAGES) {
    const opt = document.createElement("option");
    opt.value = lang;
    opt.textContent = lang;
    select.appendChild(opt);
  }
}

function renderGateTable() {
  const tbody = document.querySelector("#gateTable tbody");
  const gates = Object.values(graph.gates).sort((a, b) => b.waitMin - a.waitMin);
  tbody.innerHTML = gates
    .map(
      (g) => `
      <tr>
        <td>${g.name}</td>
        <td>${g.queueLen}</td>
        <td>${g.waitMin}</td>
        <td>${g.trend}</td>
        <td>${g.accessible ? "✅" : "—"}</td>
      </tr>`
    )
    .join("");

  const chart = document.getElementById("gateChart");
  const maxWait = Math.max(...gates.map((g) => g.waitMin), 1);
  chart.innerHTML = gates
    .map((g) => {
      const heightPct = Math.max((g.waitMin / maxWait) * 100, 3);
      return `
      <div class="bar-col">
        <div class="bar" style="height:${heightPct}%" title="${g.waitMin} min"></div>
        <div class="bar-label">${g.id}</div>
      </div>`;
    })
    .join("");
}

function renderTransitTable() {
  const tbody = document.querySelector("#transitTable tbody");
  tbody.innerHTML = Object.values(graph.transit)
    .map(
      (t) => `
      <tr>
        <td>${t.name}</td>
        <td>${t.mode.replace(/_/g, " ")}</td>
        <td>${t.loadPct}%</td>
        <td>${t.co2GPerKmPerPerson}</td>
      </tr>`
    )
    .join("");
}

function renderIncidentLog() {
  const box = document.getElementById("incidentLog");
  if (graph.incidents.length === 0) {
    box.innerHTML = `<p>No incidents logged yet — try advancing the simulation a few times from the sidebar.</p>`;
    return;
  }
  box.innerHTML =
    "<strong>Recent incident log:</strong>" +
    [...graph.incidents]
      .reverse()
      .map((inc) => `<div class="incident-item">t=${inc.tick} — ${inc.message}</div>`)
      .join("");
}

function wireTabs() {
  const buttons = document.querySelectorAll(".tab-btn");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

function showResult(elId, text, { warn = false, genaiLive = null } = {}) {
  const el = document.getElementById(elId);
  el.classList.remove("hidden");
  el.classList.toggle("warn", warn);
  el.textContent = text;
  if (genaiLive !== null) {
    const flag = document.createElement("span");
    flag.className = "genai-flag";
    flag.textContent = `GenAI live: ${genaiLive}`;
    el.appendChild(flag);
  }
}

function setBusy(btn, busy, busyLabel) {
  if (busy) {
    btn.dataset.originalLabel = btn.textContent;
    btn.textContent = busyLabel;
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalLabel || btn.textContent;
    btn.disabled = false;
  }
}

function wireButtons() {
  document.getElementById("advanceBtn").addEventListener("click", () => {
    graph.advance();
    renderSidebarFacts();
    renderGateTable();
    renderTransitTable();
    renderIncidentLog();
  });

  document.getElementById("askWayfinderBtn").addEventListener("click", async () => {
    const btn = document.getElementById("askWayfinderBtn");
    const question = document.getElementById("fanQuestion").value.trim();
    if (!question) return;
    const language = document.getElementById("languageSelect").value;

    setBusy(btn, true, "Wayfinder is checking live stadium data…");
    const result = await askWayfinder(graph, question, language);
    setBusy(btn, false);
    showResult("fanResult", result.text, { genaiLive: result.live });
  });

  document.getElementById("crowdMarshalBtn").addEventListener("click", async () => {
    const btn = document.getElementById("crowdMarshalBtn");
    setBusy(btn, true, "Crowd Marshal is analysing queues…");
    const result = await crowdMarshalBriefing(graph);
    setBusy(btn, false);
    showResult("crowdResult", result.text, { warn: result.surgeDetected, genaiLive: result.live });
  });

  document.getElementById("accessBtn").addEventListener("click", async () => {
    const btn = document.getElementById("accessBtn");
    const request = document.getElementById("accessRequest").value.trim();
    if (!request) return;
    const needType = document.getElementById("needType").value;

    setBusy(btn, true, "AccessAI Companion is finding the best option…");
    const result = await accessCompanionAssist(graph, request, needType);
    setBusy(btn, false);
    showResult("accessResult", result.text, { genaiLive: result.live });
  });

  document.getElementById("greenRouteBtn").addEventListener("click", async () => {
    const btn = document.getElementById("greenRouteBtn");
    const partySize = parseInt(document.getElementById("partySize").value, 10) || 1;
    const distanceKm = parseFloat(document.getElementById("distanceKm").value) || 1;

    setBusy(btn, true, "GreenRoute is comparing options…");
    const result = await greenRouteRecommend(graph, partySize, distanceKm);
    setBusy(btn, false);
    showResult("greenResult", result.text, { genaiLive: result.live });

    const metrics = document.getElementById("greenMetrics");
    metrics.classList.remove("hidden");
    metrics.innerHTML = `
      <div class="metric-card">
        <div class="metric-label">Estimated trip CO2</div>
        <div class="metric-value">${result.estimatedCo2Kg} kg</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">CO2 saved vs worst option</div>
        <div class="metric-value">${result.co2SavedKg} kg</div>
      </div>`;
  });

  document.getElementById("opsBtn").addEventListener("click", async () => {
    const btn = document.getElementById("opsBtn");
    setBusy(btn, true, "Ops Commander is fusing all agent outputs…");
    const result = await opsSituationReport(graph);
    setBusy(btn, false);
    showResult("opsResult", result.text, { warn: result.surgeDetected, genaiLive: result.live });

    const details = document.getElementById("opsSubDetails");
    details.classList.remove("hidden");
    document.getElementById("opsSubJson").textContent = JSON.stringify(result.subAgentOutputs, null, 2);
  });
}

main();
