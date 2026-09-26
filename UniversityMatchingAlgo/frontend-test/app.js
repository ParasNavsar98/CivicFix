const SAMPLE_PROBLEMS = [
  {
    problemId: "JH-2026-001245",
    location: { district: "Ranchi", state: "Jharkhand", latitude: 23.3441, longitude: 85.3096 },
    classification: {
      problemSummary: "Garbage is being burned near a school, creating smoke exposure for students and nearby residents.",
      primaryDomain: "Environment",
      secondaryDomains: ["Healthcare"],
      subcategory: "Pollution",
      severity: "HIGH",
      urgency: "HIGH",
      researchRequired: false,
      governmentActionPossible: true,
      requiredExpertise: ["Environmental Management", "Public Health"],
      requiredResources: ["Waste collection", "Waste disposal infrastructure"],
      confidence: 0.91
    }
  },
  {
    problemId: "WB-2026-000871",
    location: { district: "Kolkata", state: "West Bengal", latitude: 22.5726, longitude: 88.3639 },
    classification: {
      problemSummary: "Farmers report unexplained pest migration destroying crops across several fields.",
      primaryDomain: "Agriculture",
      secondaryDomains: [],
      subcategory: "Pest Management",
      severity: "MODERATE",
      urgency: "MODERATE",
      researchRequired: true,
      governmentActionPossible: true,
      requiredExpertise: ["Agriculture", "Computer Vision"],
      requiredResources: ["IoT monitoring"],
      confidence: 0.85
    }
  },
  {
    problemId: "JH-2026-002210",
    location: { district: "Dhanbad", state: "Jharkhand", latitude: 23.7957, longitude: 86.4304 },
    classification: {
      problemSummary: "Residents report structural cracks appearing on a local bridge after heavy rainfall.",
      primaryDomain: "Infrastructure",
      secondaryDomains: [],
      subcategory: "Structural Safety",
      severity: "HIGH",
      urgency: "HIGH",
      researchRequired: false,
      governmentActionPossible: true,
      requiredExpertise: ["Civil Engineering"],
      requiredResources: [],
      confidence: 0.88
    }
  }
];

function apiBase() {
  return document.getElementById("apiBase").value.replace(/\/$/, "");
}

function populateSampleProblems() {
  const select = document.getElementById("sampleProblem");
  SAMPLE_PROBLEMS.forEach((p, i) => {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = `${p.problemId} — ${p.classification.primaryDomain}/${p.classification.subcategory}`;
    select.appendChild(opt);
  });
}
populateSampleProblems();

function loadSampleProblem() {
  const idx = document.getElementById("sampleProblem").value;
  if (idx === "") return;
  const p = SAMPLE_PROBLEMS[idx];
  document.getElementById("problemId").value = p.problemId;
  document.getElementById("classificationJson").value = JSON.stringify(p.classification, null, 2);
  document.getElementById("locDistrict").value = p.location.district;
  document.getElementById("locState").value = p.location.state;
}

async function runMatching() {
  const out = document.getElementById("matchingOutput");
  out.textContent = "Running...";
  try {
    const problemId = document.getElementById("problemId").value.trim();
    const classification = JSON.parse(document.getElementById("classificationJson").value);
    const location = {
      district: document.getElementById("locDistrict").value.trim(),
      state: document.getElementById("locState").value.trim()
    };

    const res = await fetch(`${apiBase()}/api/matching/${encodeURIComponent(problemId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ classification, location })
    });
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);

    if (res.ok) {
      await loadAssignments();
    }
  } catch (err) {
    out.textContent = "Error: " + err;
  }
}

async function loadAssignments() {
  const problemId = document.getElementById("problemId").value.trim();
  if (!problemId) return;
  const res = await fetch(`${apiBase()}/api/assignments/by-problem/${encodeURIComponent(problemId)}`);
  const assignments = await res.json();

  const tbody = document.querySelector("#assignmentTable tbody");
  tbody.innerHTML = "";
  if (!Array.isArray(assignments)) return;

  assignments.forEach(a => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${a.rank}</td>
      <td>${a.universityId}</td>
      <td>${a.score}</td>
      <td><span class="badge ${a.status}">${a.status}</span></td>
      <td>
        ${a.status === "SENT" ? `
          <button onclick="acceptAssignment('${a.assignmentId}')">Accept</button>
          <button class="danger" onclick="rejectAssignment('${a.assignmentId}')">Reject</button>
        ` : ""}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function acceptAssignment(assignmentId) {
  const res = await fetch(`${apiBase()}/api/assignments/${assignmentId}/accept`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) { alert(JSON.stringify(data)); return; }
  await loadAssignments();
}

async function rejectAssignment(assignmentId) {
  const reason = prompt("Rejection reason (required):", "Insufficient current capacity.");
  if (!reason) return;
  const res = await fetch(`${apiBase()}/api/assignments/${assignmentId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason })
  });
  const data = await res.json();
  if (!res.ok) { alert(JSON.stringify(data)); return; }
  await loadAssignments();
}

async function searchMarketplace() {
  const params = new URLSearchParams();
  const domain = document.getElementById("fDomain").value.trim();
  const state = document.getElementById("fState").value.trim();
  const stage = document.getElementById("fStage").value.trim();
  if (domain) params.append("domain", domain);
  if (state) params.append("state", state);
  if (stage) params.append("developmentStage", stage);

  const res = await fetch(`${apiBase()}/api/marketplace/solutions?${params.toString()}`);
  const solutions = await res.json();

  const tbody = document.querySelector("#solutionsTable tbody");
  tbody.innerHTML = "";
  if (!Array.isArray(solutions)) return;

  solutions.forEach(s => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${s.solutionId}</td>
      <td>${s.title || ""}</td>
      <td>${(s.supportNeeded || []).join(", ")}</td>
      <td><button onclick="document.getElementById('interestSolutionId').value='${s.solutionId}'">Use for Interest</button></td>
    `;
    tbody.appendChild(tr);
  });
}

async function expressInterest() {
  const solutionId = document.getElementById("interestSolutionId").value.trim();
  const partnerId = document.getElementById("interestPartnerId").value.trim();
  const support = document.getElementById("interestSupport").value.split(",").map(s => s.trim()).filter(Boolean);
  const message = document.getElementById("interestMessage").value;

  const res = await fetch(`${apiBase()}/api/marketplace/${encodeURIComponent(solutionId)}/interest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ partnerId, supportOffered: support, contribution: {}, message })
  });
  const data = await res.json();
  if (!res.ok) { alert(JSON.stringify(data)); return; }
  await listInterests();
}

async function listInterests() {
  const solutionId = document.getElementById("interestSolutionId").value.trim();
  if (!solutionId) return;
  const res = await fetch(`${apiBase()}/api/solutions/${encodeURIComponent(solutionId)}/interests`);
  const interests = await res.json();

  const tbody = document.querySelector("#interestsTable tbody");
  tbody.innerHTML = "";
  if (!Array.isArray(interests)) return;

  interests.forEach(i => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i.interestId}</td>
      <td>${i.partnerId}</td>
      <td><span class="badge ${i.status}">${i.status}</span></td>
      <td>
        ${i.status === "PENDING" ? `
          <button onclick="acceptInterest('${i.interestId}')">Accept</button>
          <button class="danger" onclick="rejectInterestPrompt('${i.interestId}')">Reject</button>
        ` : ""}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function devHeaders() {
  return {
    "Content-Type": "application/json",
    "X-Dev-User-Id": document.getElementById("devUniversityId").value.trim(),
    "X-Dev-Role": "SPOC"
  };
}

async function acceptInterest(interestId) {
  const res = await fetch(`${apiBase()}/api/interests/${interestId}/accept`, {
    method: "POST",
    headers: devHeaders()
  });
  const data = await res.json();
  if (!res.ok) { alert(JSON.stringify(data)); return; }
  alert("Collaboration created: " + data.collaborationId);
  await listInterests();
}

async function rejectInterestPrompt(interestId) {
  const reason = prompt("Rejection reason (required):", "Not a fit for this solution.");
  if (!reason) return;
  const res = await fetch(`${apiBase()}/api/interests/${interestId}/reject`, {
    method: "POST",
    headers: devHeaders(),
    body: JSON.stringify({ reason })
  });
  const data = await res.json();
  if (!res.ok) { alert(JSON.stringify(data)); return; }
  await listInterests();
}
