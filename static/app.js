/**
 * Delta Support Agent — Demo UI Frontend Logic
 * Dependency-free vanilla JS.
 *
 * Key change: each send creates a single .interaction-group containing
 * the customer message, the response section (labelled ASSISTANT or
 * DRAFT RESPONSE — HUMAN REVIEW REQUIRED), and the decision card.
 * The grouping makes it impossible to confuse an escalated draft with
 * an automatically sent response.
 */

// ── DOM refs ────────────────────────────────────────────────────────────────
const chatWindow   = document.getElementById('chatWindow');
const msgInput     = document.getElementById('msgInput');
const sendBtn      = document.getElementById('sendBtn');
const charCount    = document.getElementById('charCount');
const clearBtn     = document.getElementById('clearBtn');
const quickBtns    = document.querySelectorAll('.quick-btn');

const pipelineSteps = {
  safety:     document.getElementById('ps-safety'),
  intent:     document.getElementById('ps-intent'),
  policy:     document.getElementById('ps-policy'),
  retrieval:  document.getElementById('ps-retrieval'),
  generation: document.getElementById('ps-generation'),
  routing:    document.getElementById('ps-routing'),
};

const attachBtn         = document.getElementById('attachBtn');
const fileInput         = document.getElementById('fileInput');
const attachmentPreview = document.getElementById('attachmentPreview');

let isLoading = false;
let conversationHistory = [];
let attachedFile = null;

// ── Utils ────────────────────────────────────────────────────────────────────
function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function autoResizeInput() {
  msgInput.style.height = 'auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight, 140) + 'px';
}

function formatFileSize(bytes) {
  if (!bytes || bytes < 1024) return (bytes || 0) + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function renderAttachmentPreview() {
  if (!attachmentPreview) return;
  if (!attachedFile) {
    attachmentPreview.style.display = 'none';
    attachmentPreview.innerHTML = '';
    if (attachBtn) attachBtn.classList.remove('has-file');
    return;
  }
  attachmentPreview.style.display = 'flex';
  if (attachBtn) attachBtn.classList.add('has-file');
  attachmentPreview.innerHTML = `
    <div class="file-chip">
      <span>📎</span>
      <span class="file-chip-name">${esc(attachedFile.name)}</span>
      <span class="file-chip-size">(${esc(attachedFile.size)})</span>
      <button class="file-chip-remove" type="button" title="Remove attachment" aria-label="Remove attachment">✕</button>
    </div>
  `;
  const rm = attachmentPreview.querySelector('.file-chip-remove');
  if (rm) {
    rm.addEventListener('click', () => {
      attachedFile = null;
      if (fileInput) fileInput.value = '';
      renderAttachmentPreview();
    });
  }
}

if (attachBtn && fileInput) {
  attachBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    const f = fileInput.files[0];
    if (!f) return;
    attachedFile = {
      name: f.name,
      size: formatFileSize(f.size),
      type: f.type || 'document'
    };
    renderAttachmentPreview();
  });
}

function hideWelcome() {
  const w = document.getElementById('welcomeState');
  if (w) {
    w.style.transition = 'opacity 0.22s';
    w.style.opacity = '0';
    setTimeout(() => w.remove(), 240);
  }
}

// Scroll so the whole group is visible, anchoring the top of it.
function scrollToGroup(el) {
  requestAnimationFrame(() => {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

// ── Pipeline animation ───────────────────────────────────────────────────────
function resetPipeline() {
  Object.values(pipelineSteps).forEach(el => el.classList.remove('active','done'));
}

async function animatePipeline() {
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const keys = ['safety','intent','policy','retrieval','generation','routing'];
  for (const k of keys) {
    if (pipelineSteps[k]) pipelineSteps[k].classList.add('active');
    await delay(220);
    if (pipelineSteps[k]) { pipelineSteps[k].classList.remove('active'); pipelineSteps[k].classList.add('done'); }
  }
}

// ── Build interaction group ──────────────────────────────────────────────────
/**
 * Creates a single visual block:
 *
 * [CUSTOMER]
 *   message bubble (right-aligned)
 *
 * [ASSISTANT]  ← for AUTO_HANDLE
 * [DRAFT RESPONSE — HUMAN REVIEW REQUIRED]  ← for ESCALATE
 *   reply bubble
 *
 * [DECISION CARD]
 *   intent | confidence | policy | retrieval | flags | reason
 */
function buildInteractionGroup(customerText, data, attachment) {
  const group = document.createElement('div');
  group.className = 'interaction-group';

  const decision = data.final_decision || 'UNKNOWN';
  const isEscalate = decision === 'ESCALATE';
  const isAuto = decision === 'AUTO_HANDLE';

  const att = attachment || data.attachment;
  const attHtml = att ? `<div class="bubble-attachment">📎 ${esc(att.name)} <span style="opacity:0.75">(${esc(att.size || 'Attached')})</span></div>` : '';

  // ── 1. CUSTOMER row ──
  const customerHtml = `
    <div class="customer-label-row">
      <span class="msg-label">Customer</span>
    </div>
    <div class="customer-row">
      <div class="msg-bubble user-bubble">
        <div class="bubble-text">${esc(customerText)}</div>
        ${attHtml}
      </div>
      <div class="customer-avatar" title="You (Customer)">👤</div>
    </div>`;

  // ── 2. RESPONSE section with Delta Agent Figure ──
  const replyText = data.reply || '(No reply generated)';
  const bubbleClass = isEscalate ? 'agent-bubble draft-bubble' : 'agent-bubble';

  const responseSectionHtml = `
    <div class="response-section">
      <div class="agent-chat-row">
        <div class="agent-avatar-wrap">
          <img src="/static/delta_agent.jpg" alt="David - Delta Customer Service Specialist" class="agent-avatar-img">
          <span class="online-badge" title="Active Delta Specialist"></span>
        </div>
        <div class="agent-content-area">
          <div class="agent-meta-header">
            <span class="agent-name">David</span>
            <span class="agent-brand-pill">Delta Airlines</span>
            <span class="agent-tag ${isEscalate ? 'tag-draft' : 'tag-auto'}">${isEscalate ? '⚠️ Human Review Draft' : '✅ Verified Assistant'}</span>
          </div>
          ${isEscalate ? `
            <div class="draft-banner">
              <span class="draft-banner-icon">⚠</span>
              <span class="draft-banner-text">DRAFT — HUMAN REVIEW REQUIRED</span>
              <span class="draft-banner-sub">Not sent automatically</span>
            </div>` : ''}
          <div class="msg-bubble ${bubbleClass}">
            ${esc(replyText)}
          </div>
          ${data.is_fallback ? '<div class="fallback-notice">⚠ Safe fallback — schema or validation failure</div>' : ''}
        </div>
      </div>
    </div>`;

  // ── 3. DECISION CARD ──
  const badgeClass = isEscalate ? 'escalate' : isAuto ? 'auto' : 'error';
  const badgeIcon  = isEscalate ? '⚠' : isAuto ? '✅' : '❌';

  const conf = typeof data.intent_confidence === 'number' ? data.intent_confidence : null;
  const confPct = conf !== null ? Math.round(conf * 100) : null;
  const confClass = conf === null ? '' : conf >= 0.75 ? 'high' : conf >= 0.60 ? 'mid' : 'low';

  // Confidence row
  const confRowHtml = confPct !== null ? `
    <div class="dc-row">
      <span class="dc-label">Confidence</span>
      <div class="conf-wrap">
        <div class="conf-bg"><div class="conf-fill ${confClass}" style="width:${confPct}%"></div></div>
        <span class="conf-pct">${confPct}%</span>
      </div>
    </div>` : '';

  // Safety flags
  const flagsHtml = (data.safety_flags && data.safety_flags.length > 0) ? `
    <div class="dc-row">
      <span class="dc-label">Safety</span>
      <div class="flag-row">
        ${data.safety_flags.map(f => `<span class="flag-chip">🚨 ${esc(f)}</span>`).join('')}
      </div>
    </div>` : '';

  // Retrieval
  const retText = data.retrieval_used
    ? `<strong>${data.retrieved_count}</strong> historical example${data.retrieved_count !== 1 ? 's' : ''} used`
    : 'Not used';

  // Escalation reason (only for ESCALATE)
  const reasonHtml = isEscalate && data.escalation_reason ? `
    <div class="dc-row">
      <span class="dc-label">Reason</span>
      <span class="dc-value mono">${esc(data.escalation_reason)}</span>
    </div>` : '';

  // Error
  const errorHtml = data.error ? `
    <div class="dc-row">
      <span class="dc-label">Error</span>
      <span class="dc-error">${esc(data.error)}</span>
    </div>` : '';

  const cardHtml = `
    <div class="decision-card">
      <div class="decision-card-header">
        <span class="decision-card-title">Pipeline Decision</span>
        <span class="decision-badge ${badgeClass}">${badgeIcon} ${esc(decision)}</span>
      </div>
      <div class="decision-card-body">
        <div class="dc-row">
          <span class="dc-label">Intent</span>
          <span class="dc-value"><strong>${esc(data.intent || '—')}</strong></span>
        </div>
        ${confRowHtml}
        <div class="dc-row">
          <span class="dc-label">Policy</span>
          <span class="dc-value mono">${esc(data.policy_action || '—')}</span>
        </div>
        ${flagsHtml}
        <div class="dc-row">
          <span class="dc-label">Retrieval</span>
          <span class="dc-value">${retText}</span>
        </div>
        ${reasonHtml}
        ${errorHtml}
      </div>
    </div>`;

  group.innerHTML = customerHtml + responseSectionHtml + cardHtml;
  return group;
}

// ── Loading group ────────────────────────────────────────────────────────────
function buildLoadingGroup(customerText, attachment) {
  const group = document.createElement('div');
  group.className = 'loading-group';
  const attHtml = attachment ? `<div class="bubble-attachment">📎 ${esc(attachment.name)} <span style="opacity:0.75">(${esc(attachment.size)})</span></div>` : '';
  group.innerHTML = `
    <div class="customer-label-row"><span class="msg-label">Customer</span></div>
    <div class="customer-row">
      <div class="msg-bubble user-bubble">
        <div class="bubble-text">${esc(customerText)}</div>
        ${attHtml}
      </div>
      <div class="customer-avatar" title="You (Customer)">👤</div>
    </div>
    <div class="agent-chat-row" style="margin-top: 8px;">
      <div class="agent-avatar-wrap">
        <img src="/static/delta_agent.jpg" alt="David - Delta Specialist" class="agent-avatar-img">
        <span class="online-badge"></span>
      </div>
      <div class="agent-content-area">
        <div class="agent-meta-header">
          <span class="agent-name">David</span>
          <span class="agent-brand-pill">Delta Airlines</span>
          <span class="agent-tag tag-running">Analyzing…</span>
        </div>
        <div class="loading-bubble"><div class="spinner"></div>Consulting Delta policy & drafting response…</div>
      </div>
    </div>`;
  return group;
}

// ── Send ─────────────────────────────────────────────────────────────────────
async function sendMessage(overrideText) {
  let text = (overrideText ?? msgInput.value).trim();
  const currentAttachment = attachedFile;

  // If text is empty but a file is attached, provide a default caption
  if (!text && currentAttachment) {
    text = `[Attached file: ${currentAttachment.name}]`;
  }

  if (!text || isLoading) return;

  isLoading = true;
  sendBtn.disabled = true;
  hideWelcome();
  resetPipeline();

  // Clear input & preview
  if (!overrideText) {
    msgInput.value = '';
    autoResizeInput();
    charCount.textContent = '0 / 2000';
  }
  attachedFile = null;
  if (fileInput) fileInput.value = '';
  renderAttachmentPreview();

  // Append loading group and scroll to it
  const loadingGroup = buildLoadingGroup(text, currentAttachment);
  chatWindow.appendChild(loadingGroup);
  scrollToGroup(loadingGroup);

  try {
    const [resp] = await Promise.all([
      fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: conversationHistory,
          attachment: currentAttachment ? { name: currentAttachment.name, size: currentAttachment.size } : null
        }),
      }),
      animatePipeline(),
    ]);

    loadingGroup.remove();

    let data;
    if (!resp.ok) {
      let errMsg = `Server error ${resp.status}`;
      try { const j = await resp.json(); errMsg = j.error || errMsg; } catch {}
      data = {
        reply: 'Something went wrong — please try again.',
        final_decision: 'ESCALATE',
        error: errMsg,
        escalation_reason: 'SERVER_ERROR',
        safety_flags: [],
        retrieval_used: false,
        retrieved_count: 0,
      };
    } else {
      data = await resp.json();
    }

    if (data.reply) {
      conversationHistory.push({ role: 'customer', text: text });
      conversationHistory.push({ role: 'assistant', text: data.reply });
      if (conversationHistory.length > 8) {
        conversationHistory = conversationHistory.slice(-8);
      }
    }

    const group = buildInteractionGroup(text, data, currentAttachment);
    chatWindow.appendChild(group);
    scrollToGroup(group);

  } catch (err) {
    loadingGroup.remove();
    resetPipeline();
    const data = {
      reply: 'Could not reach the backend. Is the server running?',
      final_decision: 'ESCALATE',
      error: err.message,
      escalation_reason: 'CONNECTION_ERROR',
      safety_flags: [],
      retrieval_used: false,
      retrieved_count: 0,
    };
    const group = buildInteractionGroup(text, data, currentAttachment);
    chatWindow.appendChild(group);
    scrollToGroup(group);
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    msgInput.focus();
  }
}

// ── Clear ────────────────────────────────────────────────────────────────────
function insertWelcome() {
  const w = document.createElement('div');
  w.id = 'welcomeState';
  w.className = 'welcome';
  w.innerHTML = `
    <div class="welcome-avatar-wrap">
      <img src="/static/delta_agent.jpg" alt="David - Delta Customer Service Specialist" class="welcome-avatar-img">
      <span class="welcome-online-pulse"></span>
    </div>
    <h1>Delta Customer Support</h1>
    <p>Chat with <strong>David</strong>, Delta Support Specialist. Watch the pipeline verify safety, classify your intent, retrieve past resolutions, and route responses live.</p>
    <div class="welcome-chips">
      <span class="wchip">🛡 Deterministic Safety</span>
      <span class="wchip">🎯 12-Intent Taxonomy</span>
      <span class="wchip">🔍 Historical Retrieval</span>
      <span class="wchip">🤖 Sarvam-105B</span>
    </div>
    <p class="welcome-note">⚠ Research prototype built for Delta Airlines automated support.</p>`;
  chatWindow.appendChild(w);
}

clearBtn.addEventListener('click', () => {
  Array.from(chatWindow.children).forEach(c => c.remove());
  insertWelcome();
  resetPipeline();
  conversationHistory = [];
  attachedFile = null;
  if (fileInput) fileInput.value = '';
  renderAttachmentPreview();
});

// ── Events ───────────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', () => sendMessage());

msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

msgInput.addEventListener('input', () => {
  autoResizeInput();
  charCount.textContent = `${msgInput.value.length} / 2000`;
});

quickBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const msg = btn.dataset.msg;
    if (msg) sendMessage(msg);
  });
});

// ── Init ─────────────────────────────────────────────────────────────────────
msgInput.focus();
