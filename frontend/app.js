const API_BASE = window.location.origin;
let allFindings = [];
let allAgents = [];

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const view = tab.dataset.view;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('view-' + view).classList.add('active');
    if (view === 'agents' && allAgents.length === 0) loadAgents();
  });
});

async function loadFindings() {
  try {
    const res = await fetch(API_BASE + '/findings');
    allFindings = await res.json();
    document.getElementById('stat-findings').textContent = allFindings.length + ' findings';
    const types = [...new Set(allFindings.map(f => f.type))].sort();
    const typeSel = document.getElementById('filter-type');
    types.forEach(t => {
      const o = document.createElement('option');
      o.value = t; o.textContent = t;
      typeSel.appendChild(o);
    });
    renderFindings();
  } catch (e) {
    document.getElementById('findings-list').innerHTML = '<p class="error">Failed to load findings: ' + e.message + '</p>';
  }
}

function renderFindings() {
  const search = document.getElementById('filter-search').value.toLowerCase();
  const type = document.getElementById('filter-type').value;
  const sev = document.getElementById('filter-severity').value;

  let filtered = allFindings.filter(f => {
    if (search && !(f.description + f.file).toLowerCase().includes(search)) return false;
    if (type && f.type !== type) return false;
    if (sev && f.severity !== sev) return false;
    return true;
  });

  document.getElementById('findings-list').innerHTML = filtered.map(f => {
    const safe = encodeURIComponent(JSON.stringify(f));
    return '<div class="finding-card sev-' + f.severity + '">' +
      '<div class="finding-header">' +
        '<span class="badge sev-' + f.severity + '">' + f.severity + '</span>' +
        '<span class="finding-type">' + f.type + '</span>' +
        '<span class="finding-file">' + f.file + (f.line ? ':' + f.line : '') + '</span>' +
      '</div>' +
      '<p class="finding-desc">' + escapeHtml(f.description) + '</p>' +
      '<button class="map-btn" data-finding="' + safe + '">Show control mappings →</button>' +
    '</div>';
  }).join('');

  if (filtered.length === 0) {
    document.getElementById('findings-list').innerHTML = '<p>No findings match the filters.</p>';
  }

  document.querySelectorAll('.map-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const finding = JSON.parse(decodeURIComponent(btn.dataset.finding));
      showMappings(finding);
    });
  });
}

document.getElementById('filter-search').addEventListener('input', renderFindings);
document.getElementById('filter-type').addEventListener('change', renderFindings);
document.getElementById('filter-severity').addEventListener('change', renderFindings);

async function showMappings(finding) {
  const res = await fetch(API_BASE + '/map', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(finding)
  });
  const mappings = await res.json();
  alert('Mappings for ' + finding.type + ':\n\n' + mappings.map(m => m.framework + ' ' + m.control_id + ' — ' + m.title).join('\n'));
}

async function loadAgents() {
  try {
    const res = await fetch(API_BASE + '/agents');
    allAgents = await res.json();
    document.getElementById('agents-grid').innerHTML = allAgents.map(a =>
      '<div class="agent-card ' + (a.is_real ? 'agent-real' : 'agent-stub') + '">' +
        '<h3>' + a.name.replace(/_/g, ' ') + '</h3>' +
        '<p class="agent-desc">' + a.description + '</p>' +
        '<span class="agent-status">' + (a.is_real ? '✅ Working' : '🔧 Scaffolded') + '</span>' +
        '<button data-agent="' + a.name + '">Run Agent →</button>' +
      '</div>'
    ).join('');

    document.querySelectorAll('[data-agent]').forEach(btn => {
      btn.addEventListener('click', () => runAgent(btn.dataset.agent));
    });
  } catch (e) {
    document.getElementById('agents-grid').innerHTML = '<p class="error">Failed to load agents.</p>';
  }
}

async function runAgent(name) {
  const context = {};
  if (name === 'control_mapping' && allFindings.length > 0) context.finding = allFindings[0];
  if (name === 'compliance') context.question = 'Do we encrypt data at rest?';

  const res = await fetch(API_BASE + '/agents/' + name + '/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(context)
  });
  const result = await res.json();
  document.getElementById('agent-output').classList.remove('hidden');
  document.getElementById('agent-output-title').textContent = name.replace(/_/g, ' ') + ' — Result';
  document.getElementById('agent-output-body').textContent = JSON.stringify(result, null, 2);
  document.getElementById('agent-output').scrollIntoView({ behavior: 'smooth' });
}

function closeAgentOutput() {
  document.getElementById('agent-output').classList.add('hidden');
}

document.getElementById('run-audit-btn').addEventListener('click', async () => {
  const framework = document.getElementById('audit-framework').value;
  const btn = document.getElementById('run-audit-btn');
  btn.disabled = true;
  btn.textContent = 'Running audit...';
  try {
    const res = await fetch(API_BASE + '/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ framework })
    });
    const report = await res.json();
    renderAudit(report);
  } catch (e) {
    document.getElementById('audit-result').innerHTML = '<p class="error">Audit failed: ' + e.message + '</p>';
  }
  btn.disabled = false;
  btn.textContent = 'Run Audit';
});

function renderAudit(report) {
  const score = parseInt(report.score.split('/')[0]);
  const total = parseInt(report.score.split('/')[1]);
  const pct = total > 0 ? Math.round(score / total * 100) : 0;
  const gaps = report.items.filter(i => i.status === 'gap').length;
  const compliant = report.items.filter(i => i.status === 'compliant').length;
  const missing = report.items.filter(i => i.status === 'missing_policy').length;
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  let html =
    '<div class="report-header print-only">' +
      '<h1>SentinelIQ Compliance Audit Report</h1>' +
      '<p class="report-meta">Framework: <strong>' + report.framework + '</strong> &middot; Generated: ' + date + '</p>' +
      '<p class="report-meta">Source: acme-payments-demo (GitHub) &middot; 136 findings analyzed</p>' +
    '</div>' +

    '<div class="audit-score">' +
      '<h2>' + report.framework + '</h2>' +
      '<div class="score-big">' + report.score + '</div>' +
      '<div class="score-bar"><div class="score-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="audit-summary">' +
        '<span class="summary-item">✅ ' + compliant + ' compliant</span>' +
        '<span class="summary-item">❌ ' + gaps + ' gaps</span>' +
        '<span class="summary-item">⚠️ ' + missing + ' missing policy</span>' +
      '</div>' +
      '<button class="print-btn" onclick="window.print()">📄 Download PDF</button>' +
    '</div>' +

    '<div class="audit-items">';

  report.items.forEach(item => {
    html += '<div class="audit-item status-' + item.status + '">' +
      '<div class="audit-item-header">' +
        '<span class="status-badge">' + item.status.replace(/_/g, ' ') + '</span>' +
        '<strong>' + item.control_id + '</strong> — ' + item.title +
      '</div>' +
      '<p class="evidence-count">' + item.evidence.length + ' evidence finding(s)' +
        (item.evidence.length > 0 ? ' &middot; e.g. <code>' + escapeHtml(item.evidence[0].file) + (item.evidence[0].line ? ':' + item.evidence[0].line : '') + '</code>' : '') +
      '</p>' +
      (item.remediation ? '<p class="remediation">💡 ' + item.remediation + '</p>' : '') +
    '</div>';
  });

  html += '</div>';

  html +=
    '<div class="report-footer print-only">' +
      '<p>Generated by SentinelIQ — self-hosted compliance engine</p>' +
      '<p>This report must be reviewed by a qualified security professional. ' +
      'Findings are derived from static analysis; verify against the current standard text.</p>' +
    '</div>';

  document.getElementById('audit-result').innerHTML = html;
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

loadFindings();
