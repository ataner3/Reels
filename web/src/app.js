/* Fabulous – Web-App. Daten: lokal (localStorage) + Sync über claude.ai (db), falls verfügbar. */
'use strict';

/* ================= Utilities ================= */
const $ = (s, r = document) => r.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
const pad = (n) => String(n).padStart(2, '0');
const dayKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const fromDayKey = (k) => { const [y, m, d] = k.split('-').map(Number); return new Date(y, m - 1, d); };
const monthKeyOf = (t) => { const d = new Date(t); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}`; };
const startOfDay = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const startOfWeek = (d) => { const x = startOfDay(d); return addDays(x, -((x.getDay() + 6) % 7)); };
const sameDay = (a, b) => dayKey(a) === dayKey(b);
const isToday = (d) => sameDay(d, new Date());
const fmt = (d, o) => new Intl.DateTimeFormat('de-DE', o).format(d);
const num = (v) => (Math.round(v * 10) / 10).toLocaleString('de-DE', { maximumFractionDigits: 1 });
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
const reduceMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
const firstGrapheme = (v) => { try { if (Intl.Segmenter) return [...new Intl.Segmenter('de', { granularity: 'grapheme' }).segment(v)][0].segment; } catch (e) { /* ignore */ } return [...v].slice(0, 2).join(''); };
const timeToMin = (t) => { const [h, m] = String(t || '0:0').split(':').map(Number); return (h || 0) * 60 + (m || 0); };

const ICON = {
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.5-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5z"/></svg>',
  pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4.5" width="4" height="15" rx="1.2"/><rect x="14" y="4.5" width="4" height="15" rx="1.2"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  back: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
  chev: '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
  left: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
  right: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
  up: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 15l6-6 6 6"/></svg>',
  down: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>',
  edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L19 9l-4-4L4 16v4z"/></svg>',
  note: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14v12l-4 4H5z"/><path d="M9 9h6M9 13h4"/></svg>',
  trash: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></svg>',
  tabToday: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>',
  tabJourney: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19c3-1 4-5 8-6s5-4 8-7"/><circle cx="4" cy="19" r="1.6"/><path d="M17 4h3v3"/></svg>',
  tabProgress: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 20V12M10 20V6M15 20v-9M20 20V9"/></svg>',
  tabMe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="8.5" r="3.8"/><path d="M4.5 20c1.2-3.6 4-5.3 7.5-5.3s6.3 1.7 7.5 5.3"/></svg>',
};

/* ================= State ================= */
const LS_KEY = 'fabulous-data-v1';
const freshState = () => ({
  v: 1, updatedAt: 0,
  profile: { name: '', onboarded: false, createdAt: Date.now() },
  goals: [], rituals: [], journeys: [],
});
let S = freshState();
let M = {}; // monthKey -> { updatedAt, entries: [{id, g, t, v, n}] }
let cacheIdx = null;
let sessionOnboarded = false;

const ui = {
  mode: 'boot', tab: 'heute', date: new Date(), stack: [], range: 7,
  sheet: null, player: null, showArchived: false,
  ob: { step: 0, name: '', journey: 'energy', wake: '07:00' },
};

function loadLocal() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    if (data && data.S && data.S.profile) { S = normalizeState(data.S); M = normalizeMonths(data.M); }
  } catch (e) { /* storage unavailable */ }
}
let saveTimer = null;
function saveLocal() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try { localStorage.setItem(LS_KEY, JSON.stringify({ S, M })); } catch (e) { /* ignore */ }
  }, 150);
}
function normalizeState(s) {
  const base = freshState();
  return {
    ...base, ...s,
    profile: { ...base.profile, ...(s.profile || {}) },
    goals: Array.isArray(s.goals) ? s.goals : [],
    rituals: Array.isArray(s.rituals) ? s.rituals : [],
    journeys: Array.isArray(s.journeys) ? s.journeys : [],
  };
}
function normalizeMonths(m) {
  const out = {};
  if (m && typeof m === 'object') {
    for (const k of Object.keys(m)) {
      if (/^\d{4}-\d{2}$/.test(k) && m[k] && Array.isArray(m[k].entries)) {
        out[k] = { updatedAt: Number(m[k].updatedAt) || 0, entries: m[k].entries.filter((e) => e && e.g && e.t) };
      }
    }
  }
  return out;
}

/** Nach jeder Änderung aufrufen. */
function commit({ app = true, months = [], render = true } = {}) {
  const now = Date.now();
  if (app) { S.updatedAt = Math.max(now, S.updatedAt + 1); Cloud.markApp(); }
  for (const mk of months) { if (M[mk]) { M[mk].updatedAt = Math.max(now, M[mk].updatedAt + 1); Cloud.markMonth(mk); } }
  cacheIdx = null;
  saveLocal();
  Cloud.schedule();
  if (render) renderApp();
}

/* ================= Entries & computations ================= */
function idx() {
  if (cacheIdx) return cacheIdx;
  const byDay = new Map(); const list = new Map();
  for (const mk of Object.keys(M)) {
    for (const e of M[mk].entries) {
      const k = dayKey(new Date(e.t));
      let m = byDay.get(e.g); if (!m) { m = new Map(); byDay.set(e.g, m); }
      m.set(k, (m.get(k) || 0) + Number(e.v || 0));
      let l = list.get(e.g); if (!l) { l = []; list.set(e.g, l); }
      l.push(e);
    }
  }
  cacheIdx = { byDay, list };
  return cacheIdx;
}
const goalEntries = (g) => idx().list.get(g.id) || [];
const dayTotal = (g, d) => idx().byDay.get(g.id)?.get(dayKey(d)) || 0;
const periodStart = (g, d) => (g.freq === 'weekly' ? startOfWeek(d) : startOfDay(d));
const prevPeriod = (g, d) => (g.freq === 'weekly' ? addDays(startOfWeek(d), -7) : addDays(startOfDay(d), -1));
function progress(g, d) {
  if (g.freq !== 'weekly') return dayTotal(g, d);
  const s = startOfWeek(d); let t = 0;
  for (let i = 0; i < 7; i++) t += dayTotal(g, addDays(s, i));
  return t;
}
const isCompleted = (g, d) => progress(g, d) >= g.target;
const isDone = (g, d) => (g.kind === 'count' && g.freq === 'daily' ? isCompleted(g, d) : dayTotal(g, d) > 0);
const fraction = (g, d) => (g.target > 0 ? Math.min(progress(g, d) / g.target, 1) : 0);
const streakUnit = (g, n) => (g.freq === 'weekly' ? (n === 1 ? 'Woche' : 'Wochen') : (n === 1 ? 'Tag' : 'Tage'));

function currentStreak(g) {
  let d = new Date();
  if (!isCompleted(g, d)) d = prevPeriod(g, d);
  let n = 0;
  while (n < 3000 && isCompleted(g, d)) { n++; d = prevPeriod(g, d); }
  return n;
}
function bestStreak(g) {
  const l = goalEntries(g);
  if (!l.length) return 0;
  let first = Infinity; for (const e of l) first = Math.min(first, e.t);
  let d = periodStart(g, new Date(first)); const now = new Date();
  let best = 0, run = 0, guard = 0;
  while (d <= now && guard++ < 4000) {
    if (isCompleted(g, d)) { run++; best = Math.max(best, run); } else run = 0;
    d = g.freq === 'weekly' ? addDays(d, 7) : addDays(d, 1);
  }
  return best;
}
function trackingStart(g) {
  let m = g.createdAt || Date.now();
  for (const e of goalEntries(g)) m = Math.min(m, e.t);
  return new Date(m);
}
function completionRate(g, days) {
  const periods = g.freq === 'weekly' ? Math.max(1, Math.ceil(days / 7)) : days;
  const limit = periodStart(g, trackingStart(g));
  let d = periodStart(g, new Date()); let counted = 0, done = 0;
  for (let i = 0; i < periods; i++) {
    if (d < limit) break;
    const r = isCompleted(g, d);
    if (!(i === 0 && !r)) { counted++; if (r) done++; }
    d = prevPeriod(g, d);
  }
  return counted ? done / counted : null;
}
const totalAmount = (g) => goalEntries(g).reduce((s, e) => s + Number(e.v || 0), 0);
function summary(g) {
  if (g.kind === 'check') return g.freq === 'weekly' ? `${g.target}× pro Woche` : 'Täglich abhaken';
  return `${num(g.target)} ${g.unit} ${g.freq === 'weekly' ? 'pro Woche' : 'pro Tag'}`.replace(/\s+/g, ' ');
}
function progressText(g, d) {
  const p = progress(g, d);
  if (g.kind === 'check') return g.freq === 'weekly' ? `${num(p)} von ${g.target}× diese Woche` : (p >= 1 ? 'Erledigt' : 'Noch offen');
  return `${num(p)} / ${num(g.target)} ${g.unit}${g.freq === 'weekly' ? ' diese Woche' : ''}`;
}
function entryTime(d) {
  if (isToday(d)) return Date.now();
  const x = startOfDay(d); x.setHours(12); return x.getTime();
}

/* ---- mutations (call commit afterwards) ---- */
function addEntry(g, d, v, note = '') {
  const t = entryTime(d); const mk = monthKeyOf(t);
  if (!M[mk]) M[mk] = { updatedAt: 0, entries: [] };
  M[mk].entries.push({ id: uid(), g: g.id, t, v: Number(v), n: note || '' });
  cacheIdx = null;
  return mk;
}
function removeEntry(e) {
  const mk = monthKeyOf(e.t);
  if (M[mk]) M[mk].entries = M[mk].entries.filter((x) => x.id !== e.id);
  cacheIdx = null;
  return mk;
}
const entriesOnDay = (g, d) => { const k = dayKey(d); return goalEntries(g).filter((e) => dayKey(new Date(e.t)) === k); };
function completeForDay(g, d) {
  if (isDone(g, d)) return [];
  if (g.kind === 'count' && g.freq === 'daily') return [addEntry(g, d, Math.max(g.target - dayTotal(g, d), g.step || 1))];
  if (g.kind === 'count') return [addEntry(g, d, g.step || 1)];
  return [addEntry(g, d, 1)];
}
function resetDay(g, d) { return entriesOnDay(g, d).map(removeEntry); }
function toggleDone(g, d) { return isDone(g, d) ? resetDay(g, d) : completeForDay(g, d); }
function primaryAction(g, d) {
  if (g.kind === 'check') return dayTotal(g, d) > 0 ? resetDay(g, d) : [addEntry(g, d, 1)];
  return [addEntry(g, d, g.step || 1)];
}
function undoLast(g, d) {
  const l = entriesOnDay(g, d).sort((a, b) => b.t - a.t);
  return l.length ? [removeEntry(l[0])] : [];
}

/* ---- goals / rituals ---- */
const goalById = (id) => S.goals.find((g) => g.id === id);
const ritualById = (id) => S.rituals.find((r) => r.id === id);
const activeGoals = () => S.goals.filter((g) => !g.archived).sort((a, b) => a.sort - b.sort);
const nextSort = () => S.goals.reduce((m, g) => Math.max(m, g.sort ?? 0), -1) + 1;
function newGoal(p = {}) {
  return {
    id: uid(), title: '', emoji: '⭐️', color: COLORS[0], kind: 'check', freq: 'daily', target: 1, unit: '', step: 1,
    notes: '', createdAt: Date.now(), archived: false, sort: nextSort(), ritualId: null, ritualOrder: 0, duration: 0, ...p,
  };
}
const ritualHabits = (r) => S.goals.filter((g) => g.ritualId === r.id && !g.archived).sort((a, b) => a.ritualOrder - b.ritualOrder);
const sortedRituals = () => [...S.rituals].sort((a, b) => timeToMin(a.time) - timeToMin(b.time));
function addToRitual(g, r) {
  g.ritualId = r.id;
  g.ritualOrder = ritualHabits(r).filter((x) => x.id !== g.id).reduce((m, x) => Math.max(m, x.ritualOrder), -1) + 1;
}
function makeRitual(slot, time) {
  const s = SLOTS[slot];
  return { id: uid(), name: s.name, emoji: s.emoji, theme: s.theme, time: time || s.time, slot, createdAt: Date.now() };
}
function ritualForSlot(slot) {
  let r = S.rituals.find((x) => x.slot === slot);
  if (!r) { r = makeRitual(slot); S.rituals.push(r); }
  return r;
}
const ritualMinutes = (r) => ritualHabits(r).reduce((s, g) => s + (Number(g.duration) || 0), 0);
const ritualDone = (r, d) => ritualHabits(r).filter((g) => isDone(g, d)).length;
function ritualCompleted(r, d) { const h = ritualHabits(r); return h.length > 0 && h.every((g) => isDone(g, d)); }
function ritualStreak(r) {
  let d = startOfDay(new Date());
  if (!ritualCompleted(r, d)) d = addDays(d, -1);
  let n = 0;
  while (n < 3000 && ritualCompleted(r, d)) { n++; d = addDays(d, -1); }
  return n;
}
function ritualInfo(r) {
  const h = ritualHabits(r).length; const m = ritualMinutes(r);
  return [r.time, plural(h, 'Gewohnheit', 'Gewohnheiten'), m ? `${m} Min.` : ''].filter(Boolean).join(' · ');
}
const themeOf = (key) => THEMES[key] || THEMES.morning;
const themeStyle = (key) => { const t = themeOf(key); return `--a:${t.a};--b:${t.b}`; };

/* ---- journeys ---- */
const journeyById = (id) => JOURNEYS.find((j) => j.id === id);
const journeyProgress = (id) => S.journeys.find((p) => p.id === id);
const activeJourney = () => S.journeys.find((p) => p.active && !p.completedAt);
function startJourney(j) {
  for (const p of S.journeys) p.active = false;
  const p = journeyProgress(j.id);
  if (p) {
    if (p.completedAt) Object.assign(p, { stepIndex: 0, stepStartedAt: Date.now(), linkedGoalId: null, completedAt: null, startedAt: Date.now() });
    p.active = true;
  } else {
    S.journeys.push({ id: j.id, startedAt: Date.now(), stepIndex: 0, stepStartedAt: Date.now(), linkedGoalId: null, active: true, completedAt: null });
  }
}
function addHabitFromBlueprint(bp) {
  const r = ritualForSlot(bp.slot);
  let g = ritualHabits(r).find((x) => x.title === bp.title) || S.goals.find((x) => x.title === bp.title && !x.archived);
  if (g) { if (!g.ritualId) addToRitual(g, r); return g; }
  g = newGoal({ title: bp.title, emoji: bp.emoji, color: bp.color, duration: bp.minutes, notes: bp.tip });
  S.goals.push(g); addToRitual(g, r);
  return g;
}
function journeyDoneDays(p) {
  const g = p.linkedGoalId && goalById(p.linkedGoalId);
  if (!g) return 0;
  const start = startOfDay(new Date(p.stepStartedAt)).getTime();
  const days = new Set();
  for (const e of goalEntries(g)) if (e.t >= start) days.add(dayKey(new Date(e.t)));
  let n = 0; for (const k of days) if (isDone(g, fromDayKey(k))) n++;
  return n;
}
function advanceJourney(p, j) {
  p.stepIndex++; p.stepStartedAt = Date.now(); p.linkedGoalId = null;
  if (p.stepIndex >= j.steps.length) { p.completedAt = Date.now(); p.active = false; }
}

/* ================= Cloud sync (claude.ai db) ================= */
const Cloud = (() => {
  let db = null, appRef = null, monthsCol = null;
  let status = 'connecting'; // connecting | local | synced | saving | offline | error
  let dirtyApp = false; const dirtyMonths = new Set();
  let timer = null, flushing = false, readyResolve, appSeen = false, monthsSeen = false;
  const ready = new Promise((r) => { readyResolve = r; });
  const setStatus = (s) => { status = s; const el = $('#sync-status'); if (el) el.outerHTML = syncHTML(); };

  async function init() {
    const c = window.claude;
    if (!c || typeof c.use !== 'function') { setStatus('local'); readyResolve(); return; }
    let dbNs = null, userNs = null;
    try { [dbNs, userNs] = await Promise.all([c.use('db'), c.use('user')]); } catch (e) { /* ignore */ }
    if (!dbNs || !userNs) { setStatus('local'); readyResolve(); return; }
    let id = null;
    try { id = await userNs.id(); } catch (e) { /* ignore */ }
    if (!id) { setStatus('local'); readyResolve(); return; }
    try {
      db = dbNs;
      appRef = db.doc(`data/users/${id}/app`);
      monthsCol = appRef.collection('months');
    } catch (e) { db = null; setStatus('local'); readyResolve(); return; }
    const t = setTimeout(() => { if (!appSeen) { setStatus('offline'); readyResolve(); } }, 9000);
    appRef.onSnapshot((snap) => {
      onApp(snap);
      if (!snap.metadata.fromCache) { appSeen = true; clearTimeout(t); maybeReady(); }
    }, () => { setStatus('error'); readyResolve(); });
    monthsCol.onSnapshot((snap) => {
      onMonths(snap);
      if (!snap.metadata.fromCache) { monthsSeen = true; maybeReady(); }
    }, () => { setStatus('error'); });
  }
  function maybeReady() {
    if (appSeen && status === 'connecting') setStatus('synced');
    if (appSeen && monthsSeen) readyResolve();
    else if (appSeen) setTimeout(readyResolve, 2500);
  }
  function onApp(snap) {
    if (snap.metadata.hasPendingWrites) return;
    const body = snap.exists ? snap.data() : null;
    const remote = body && body.state && body.state.profile ? body.state : null;
    const rT = remote ? Number(remote.updatedAt) || 0 : 0;
    // Frisch auf diesem Gerät eingerichtet, aber in der Cloud gibt es schon ein älteres Profil: Cloud gewinnt.
    const adoptOld = remote && remote.profile.onboarded && sessionOnboarded && S.goals.length <= 2 &&
      (remote.profile.createdAt || 0) < (S.profile.createdAt || 0) && rT < S.updatedAt;
    if (remote && (rT > S.updatedAt || adoptOld)) {
      const wasOnboarded = S.profile.onboarded;
      S = normalizeState(JSON.parse(JSON.stringify(remote)));
      if (adoptOld) { S.updatedAt = Date.now(); markApp(); schedule(); toast('Deine gespeicherten Daten wurden geladen.'); }
      cacheIdx = null; saveLocal();
      if (ui.mode !== 'app' && S.profile.onboarded) { ui.mode = 'app'; renderApp(); }
      else if (ui.mode === 'app' && !S.profile.onboarded && wasOnboarded) { ui.mode = 'onboarding'; ui.stack = []; closeSheet(); renderOnboarding(); }
      else if (ui.mode === 'app') renderApp();
    } else if (S.updatedAt > rT && (S.profile.onboarded || remote)) {
      markApp(); schedule();
    }
  }
  function onMonths(snap) {
    let changed = false;
    const seen = new Set();
    for (const d of snap.docs) {
      seen.add(d.id);
      const body = d.data(); if (!body) continue;
      const rT = Number(body.updatedAt) || 0; const lT = M[d.id]?.updatedAt || 0;
      if (rT > lT) { M[d.id] = { updatedAt: rT, entries: Array.isArray(body.entries) ? body.entries.map((e) => ({ ...e })) : [] }; changed = true; }
      else if (lT > rT) { dirtyMonths.add(d.id); }
    }
    if (!snap.metadata.fromCache) for (const k of Object.keys(M)) if (!seen.has(k) && M[k].entries.length) dirtyMonths.add(k);
    if (dirtyMonths.size) schedule();
    if (changed) { cacheIdx = null; saveLocal(); if (ui.mode === 'app') renderApp(); }
  }
  function markApp() { dirtyApp = true; }
  function markMonth(k) { dirtyMonths.add(k); }
  function schedule() { if (!db) return; clearTimeout(timer); timer = setTimeout(flush, 700); }
  async function write(ref, body) {
    try { await ref.set(body); }
    catch (e) {
      if (e && e.code === 'unavailable') { await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200)); await ref.set(body); }
      else throw e;
    }
  }
  async function flush() {
    if (!db || flushing) return;
    flushing = true; setStatus('saving');
    try {
      while (dirtyApp || dirtyMonths.size) {
        if (dirtyApp) { dirtyApp = false; await write(appRef, { updatedAt: S.updatedAt, state: JSON.parse(JSON.stringify(S)) }); }
        for (const k of [...dirtyMonths]) {
          dirtyMonths.delete(k);
          if (M[k]) await write(monthsCol.doc(k), { updatedAt: M[k].updatedAt, entries: M[k].entries });
        }
      }
      setStatus('synced');
    } catch (e) {
      dirtyApp = true;
      if (e && (e.code === 'invalid_argument' || e.code === 'revoked' || e.code === 'not_granted')) {
        db = null; setStatus('local');
      } else if (e && e.code === 'quota_exceeded') {
        setStatus('error'); toast('Cloud-Speicher ist voll. Deine Daten bleiben auf diesem Gerät.');
      } else {
        setStatus('offline'); setTimeout(schedule, 8000);
      }
    } finally { flushing = false; }
  }
  return { init, ready, markApp, markMonth, schedule, get status() { return status; }, get enabled() { return !!db; } };
})();

function syncHTML() {
  const s = Cloud.status;
  const map = {
    connecting: ['busy', 'Verbinde mit deinem claude.ai-Konto …'],
    synced: ['ok', 'Synchronisiert mit deinem claude.ai-Konto'],
    saving: ['busy', 'Wird gespeichert …'],
    offline: ['bad', 'Gerade nicht erreichbar. Änderungen werden später übertragen.'],
    error: ['bad', 'Synchronisierung fehlgeschlagen. Daten bleiben auf diesem Gerät.'],
    local: ['', 'Gespeichert nur auf diesem Gerät'],
  };
  const [cls, text] = map[s] || map.local;
  return `<p id="sync-status" class="sync ${cls}"><i></i><span>${text}</span></p>`;
}

/* ================= Small UI helpers ================= */
function ring(frac, size, stroke, color, track = 'currentColor', trackOpacity = 0.18) {
  const r = (size - stroke) / 2; const c = 2 * Math.PI * r; const f = clamp(frac || 0, 0, 1);
  return `<svg class="ring" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true">
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${track}" stroke-opacity="${trackOpacity}" stroke-width="${stroke}"/>
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="${stroke}" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - f)}" transform="rotate(-90 ${size / 2} ${size / 2})"
      style="transition: stroke-dashoffset .5s cubic-bezier(.3,1,.4,1)" ${f === 0 ? 'stroke-opacity="0"' : ''}/>
  </svg>`;
}
let toastTimer = null;
function toast(msg) {
  const el = $('#toast'); if (!el) return;
  el.textContent = msg; el.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
}
function greeting() {
  const h = new Date().getHours();
  const base = h >= 5 && h < 11 ? 'Guten Morgen' : h >= 11 && h < 17 ? 'Hallo' : h >= 17 && h < 22 ? 'Guten Abend' : 'Gute Nacht';
  return S.profile.name ? `${base}, ${S.profile.name}` : base;
}
const quoteFor = (d) => QUOTES[Math.floor(startOfDay(d).getTime() / 86400000) % QUOTES.length];

/* ---- sound ---- */
let audioCtx = null;
function unlockAudio() {
  try { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); if (audioCtx.state === 'suspended') audioCtx.resume(); } catch (e) { /* ignore */ }
}
function chime(notes = [660, 880]) {
  if (!audioCtx) return;
  try {
    const now = audioCtx.currentTime;
    notes.forEach((f, i) => {
      const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, now + i * 0.16);
      g.gain.exponentialRampToValueAtTime(0.25, now + i * 0.16 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.16 + 0.9);
      o.connect(g).connect(audioCtx.destination); o.start(now + i * 0.16); o.stop(now + i * 0.16 + 1);
    });
  } catch (e) { /* ignore */ }
  try { navigator.vibrate?.(120); } catch (e) { /* ignore */ }
}

/* ================= Rendering: shell ================= */
const TABS = [
  { id: 'heute', label: 'Heute', icon: ICON.tabToday },
  { id: 'reisen', label: 'Reisen', icon: ICON.tabJourney },
  { id: 'fortschritt', label: 'Fortschritt', icon: ICON.tabProgress },
  { id: 'ich', label: 'Ich', icon: ICON.tabMe },
];

function renderApp() {
  if (ui.mode !== 'app') return;
  ui.stack = ui.stack.filter((s) => (s.type === 'goal' ? goalById(s.id) : s.type === 'ritual' ? ritualById(s.id) : journeyById(s.id)));
  const root = $('#app');
  const top = ui.stack[ui.stack.length - 1];
  let body;
  try {
    if (top) body = top.type === 'goal' ? viewGoal(top.id) : top.type === 'ritual' ? viewRitual(top.id) : viewJourney(top.id);
    else body = ui.tab === 'reisen' ? viewJourneys() : ui.tab === 'fortschritt' ? viewProgress() : ui.tab === 'ich' ? viewMe() : viewToday();
  } catch (e) {
    console.error(e);
    body = `<div class="empty"><div class="emo">😵</div><p>Da ist etwas schiefgelaufen.</p><button class="btn" data-act="go-tab" data-tab="heute">Zu „Heute“</button></div>`;
  }
  const nav = `<nav class="tabbar" aria-label="Hauptnavigation"><div class="tabbar-inner">${TABS.map((t) =>
    `<button class="tab" data-act="go-tab" data-tab="${t.id}" ${ui.tab === t.id ? 'aria-current="page"' : ''}>${t.icon}<span>${t.label}</span></button>`).join('')}</div></nav>`;
  if (!root.querySelector('.view')) root.innerHTML = `<main class="view" id="view"></main>${nav}`;
  else root.querySelector('.tabbar').outerHTML = nav;
  root.querySelector('.view').innerHTML = body;
}

function backRow(extra = '') {
  return `<div class="back-row"><button class="back" data-act="back">${ICON.back}<span>Zurück</span></button>${extra}</div>`;
}

/* ================= View: Heute ================= */
function viewToday() {
  const d = ui.date; const goals = activeGoals();
  const rituals = sortedRituals();
  const standalone = goals.filter((g) => !g.ritualId || !ritualById(g.ritualId));
  const today = isToday(d);
  const title = today ? greeting() : sameDay(d, addDays(new Date(), -1)) ? 'Gestern' : fmt(d, { weekday: 'long', day: 'numeric', month: 'long' });
  const eyebrow = today ? fmt(d, { weekday: 'long', day: 'numeric', month: 'long' }) : 'Rückblick';

  // "Jetzt dran": das späteste, noch offene Ritual, dessen Zeit schon erreicht ist
  let nowId = null;
  if (today) {
    const mins = new Date().getHours() * 60 + new Date().getMinutes();
    for (const r of rituals) if (timeToMin(r.time) <= mins + 30 && !ritualCompleted(r, d) && ritualHabits(r).length) nowId = r.id;
  }

  let html = `<header class="page-head"><div><p class="eyebrow">${esc(eyebrow)}</p><h1>${esc(title)}</h1></div>
    <button class="icon-btn" data-act="add-menu" aria-label="Hinzufügen">${ICON.plus}</button></header>`;
  html += weekStrip(d, goals);
  if (!today) html += `<button class="btn small ghost" data-act="go-today" style="align-self:flex-start">Zurück zu heute</button>`;

  if (goals.length) {
    const done = goals.filter((g) => isDone(g, d)).length; const f = done / goals.length;
    html += `<section class="card summary"><div class="ring-wrap">${ring(f, 78, 9, 'var(--accent)', 'var(--accent)', 0.16)}<span class="num">${Math.round(f * 100)}%</span></div>
      <div><h2>${done === goals.length ? 'Alles geschafft! 🎉' : `${done} von ${goals.length} erledigt`}</h2><p>${esc(quoteFor(d))}</p></div></section>`;
  }

  const ap = activeJourney(); const aj = ap && journeyById(ap.id);
  if (aj) html += journeyBanner(aj, ap);

  for (const r of rituals) html += ritualCard(r, d, r.id === nowId);

  if (standalone.length) {
    html += `<h2 class="section-title">Ziele & Tracker</h2>`;
    html += standalone.map((g) => goalCard(g, d)).join('');
  }

  if (!goals.length && !rituals.length) {
    html += `<div class="card empty"><div class="emo">🌱</div><h3>Noch nichts geplant</h3><p class="muted">Leg ein Ritual oder ein erstes Ziel an.</p></div>`;
  }
  html += `<div class="btn-row"><button class="btn" data-act="new-ritual">${ICON.plus.replace('<svg', '<svg width="18" height="18"')} Ritual</button>
    <button class="btn" data-act="new-goal">${ICON.plus.replace('<svg', '<svg width="18" height="18"')} Ziel / Tracker</button></div>`;
  return html;
}

function weekStrip(sel, goals) {
  const start = startOfWeek(sel); const today = startOfDay(new Date());
  const canFwd = addDays(start, 7) <= today;
  let cells = '';
  for (let i = 0; i < 7; i++) {
    const day = addDays(start, i); const future = day > today;
    const f = goals.length && !future ? goals.filter((g) => isDone(g, day)).length / goals.length : 0;
    const label = fmt(day, { weekday: 'long', day: 'numeric', month: 'long' });
    cells += `<button class="day" data-act="pick-day" data-day="${dayKey(day)}" aria-pressed="${sameDay(day, sel)}" ${future ? 'disabled' : ''} aria-label="${esc(label)}">
      <span class="wd">${fmt(day, { weekday: 'short' }).slice(0, 2)}</span>
      <span class="ring-wrap">${ring(f, 36, 3.5, 'var(--accent)', 'var(--fg)', 0.12)}<span class="num">${day.getDate()}</span></span></button>`;
  }
  return `<div class="week" role="group" aria-label="Woche wählen"><button class="arrow" data-act="week" data-dir="-1" aria-label="Vorige Woche">${ICON.left}</button>${cells}
    <button class="arrow" data-act="week" data-dir="1" ${canFwd ? '' : 'disabled'} aria-label="Nächste Woche">${ICON.right}</button></div>`;
}

function journeyBanner(j, p) {
  const i = Math.min(p.stepIndex, j.steps.length - 1);
  return `<button class="journey-banner" style="${themeStyle(j.theme)}" data-act="open-journey" data-id="${j.id}">
    <div class="row"><span class="emo">${j.emoji}</span><div><small>Deine Reise · ${esc(j.title)}</small>
    <strong>Schritt ${i + 1} von ${j.steps.length}: ${esc(j.steps[i].title)}</strong></div>${ICON.chev.replace('class="chev"', 'class="chev" style="color:#fff;width:20px;height:20px"')}</div>
    <div class="bar"><i style="width:${(p.stepIndex / j.steps.length) * 100}%"></i></div></button>`;
}

function ritualCard(r, d, isNow) {
  const habits = ritualHabits(r); const done = ritualDone(r, d); const complete = ritualCompleted(r, d);
  const f = habits.length ? done / habits.length : 0;
  let html = `<section class="ritual" style="${themeStyle(r.theme)}" aria-label="${esc(r.name)}">
    <button class="ritual-head" data-act="open-ritual" data-id="${r.id}">
      <span class="ritual-emoji">${esc(r.emoji)}</span>
      <span class="grow"><h2>${esc(r.name)}</h2><small>${esc(ritualInfo(r))}</small>${isNow ? '<span class="chip now" style="margin-top:4px">Jetzt dran</span>' : ''}</span>
      <span class="ritual-ring">${ring(f, 44, 4, '#fff', '#fff', 0.28)}<span class="num">${complete ? ICON.check.replace('<svg', '<svg width="18" height="18"') : `${done}/${habits.length}`}</span></span>
    </button>`;
  if (!habits.length) {
    html += `<button class="add-first" data-act="new-habit" data-ritual="${r.id}">${ICON.plus.replace('<svg', '<svg width="20" height="20"')} Erste Gewohnheit hinzufügen</button>`;
  } else {
    html += `<ul class="habits">${habits.map((g) => {
      const ok = isDone(g, d);
      const sub = g.kind === 'count' ? progressText(g, d) : g.duration ? `${g.duration} Min.` : '';
      return `<li class="habit ${ok ? 'done' : ''}">
        <button class="habit-main" data-act="open-goal" data-id="${g.id}"><span class="habit-emoji">${esc(g.emoji)}</span>
          <span style="min-width:0"><span class="habit-title">${esc(g.title)}</span>${sub ? `<span class="habit-sub">${esc(sub)}</span>` : ''}</span></button>
        <button class="tick" data-act="toggle-habit" data-id="${g.id}" aria-pressed="${ok}" aria-label="${esc(g.title)} ${ok ? 'als offen markieren' : 'abhaken'}">${ICON.check}</button>
      </li>`;
    }).join('')}</ul>`;
    if (isToday(d)) {
      html += `<button class="play" data-act="play" data-id="${r.id}">${complete ? 'Noch einmal durchgehen' : `${ICON.play} Ritual starten`}</button>`;
    }
  }
  return html + '</section>';
}

function goalCard(g, d) {
  const complete = isCompleted(g, d);
  const filled = g.kind === 'check' ? dayTotal(g, d) > 0 : complete;
  const st = currentStreak(g);
  return `<section class="card goal-card ${complete ? 'complete' : ''}" style="--gc:${g.color}">
    <button class="goal-main" data-act="open-goal" data-id="${g.id}">
      <span class="badge">${esc(g.emoji)}</span>
      <span style="min-width:0"><span class="goal-title">${esc(g.title)}</span><span class="goal-sub">${esc(progressText(g, d))}</span>
      ${st ? `<span class="goal-meta"><span class="chip streak">🔥 ${st} ${streakUnit(g, st)}</span></span>` : ''}</span>
    </button>
    <span class="goal-actions">
      ${g.kind === 'count' ? `<button class="mini-btn" data-act="amount" data-id="${g.id}" aria-label="Menge eingeben">${ICON.edit}</button>` : ''}
      <button class="ring-btn ${filled ? 'filled' : ''}" data-act="primary" data-id="${g.id}" aria-label="${g.kind === 'check' ? (filled ? 'Als offen markieren' : 'Abhaken') : `${num(g.step)} ${esc(g.unit)} hinzufügen`}">
        <span class="fill"></span>${ring(fraction(g, d), 50, 5, g.color, g.color, 0.2)}<span class="glyph">${g.kind === 'check' ? ICON.check : ICON.plus}</span>
      </button>
    </span>
  </section>`;
}

/* ================= View: Ziel-Details ================= */
function viewGoal(id) {
  const g = goalById(id);
  if (!g) return '';
  const now = new Date(); const st = currentStreak(g); const best = bestStreak(g); const rate = completionRate(g, 30);
  const ritual = g.ritualId && ritualById(g.ritualId);
  const doneToday = g.kind === 'check' ? dayTotal(g, now) > 0 : false;
  let html = backRow(`<button class="btn small" data-act="edit-goal" data-id="${g.id}">Bearbeiten</button>`);
  html += `<section class="detail-hero" style="--gc:${g.color}">
    <div class="big-ring">${ring(fraction(g, now), 120, 10, g.color, g.color, 0.18)}<span>${esc(g.emoji)}</span></div>
    <h1>${esc(g.title)}</h1><p class="muted">${esc(summary(g))}${ritual ? ` · ${esc(ritual.emoji)} ${esc(ritual.name)}` : ''}</p>
    <p class="prog" style="color:${g.color}">${esc(progressText(g, now))}</p></section>`;
  html += `<div class="btn-row">
    <button class="btn primary" style="background:${g.color};color:#fff" data-act="primary-now" data-id="${g.id}">${g.kind === 'check' ? (doneToday ? 'Heute erledigt ✓' : 'Heute abhaken') : `+${num(g.step)} ${esc(g.unit)}`}</button>
    <button class="btn" data-act="amount" data-id="${g.id}">${g.kind === 'check' ? 'Mit Notiz' : 'Menge eingeben'}</button></div>`;
  html += `<div class="tiles four">
    <div class="tile"><span class="ico">🔥</span><span class="val">${st}</span><span class="lbl">Aktuelle Serie (${streakUnit(g, st)})</span></div>
    <div class="tile"><span class="ico">🏆</span><span class="val">${best}</span><span class="lbl">Beste Serie</span></div>
    <div class="tile"><span class="ico">📈</span><span class="val">${rate == null ? '–' : Math.round(rate * 100) + '%'}</span><span class="lbl">Erfolgsquote 30 Tage</span></div>
    <div class="tile"><span class="ico">∑</span><span class="val">${num(totalAmount(g))}</span><span class="lbl">${g.kind === 'check' ? 'Mal erledigt' : `Gesamt ${esc(g.unit)}`}</span></div></div>`;
  html += `<section class="card"><h3>Verlauf</h3>${historyChart(g)}</section>`;
  html += `<section class="card"><h3>Kalender</h3>${heatmap(g)}</section>`;
  if (g.notes) html += `<section class="card"><h3>Tipp / Motivation</h3><p class="letter" style="font-size:15.5px">${esc(g.notes)}</p></section>`;
  const recent = [...goalEntries(g)].sort((a, b) => b.t - a.t).slice(0, 40);
  html += `<section class="card" style="--gc:${g.color}"><h3>Letzte Einträge</h3>${recent.length ? recent.map((e) => `
    <div class="entry"><div class="grow"><span>${esc(fmt(new Date(e.t), { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }))}</span>
      ${e.n ? `<span class="note">${esc(e.n)}</span>` : ''}</div>
      <span class="val">${g.kind === 'check' ? '✓' : `+${num(e.v)} ${esc(g.unit)}`}</span>
      <button class="mini-btn" data-act="del-entry" data-id="${e.id}" data-goal="${g.id}" aria-label="Eintrag löschen">${ICON.trash}</button></div>`).join('')
    : '<p class="muted">Noch keine Einträge.</p>'}</section>`;
  html += `<div class="btn-row"><button class="btn" data-act="archive-goal" data-id="${g.id}">${g.archived ? 'Reaktivieren' : 'Archivieren'}</button>
    <button class="btn danger" data-act="delete-goal" data-id="${g.id}">Löschen</button></div>`;
  return html;
}

function historyChart(g) {
  const pts = []; let d = periodStart(g, new Date());
  const n = g.freq === 'weekly' ? 12 : 14;
  for (let i = 0; i < n; i++) { pts.unshift({ d, v: progress(g, d) }); d = prevPeriod(g, d); }
  const W = 340, H = 170, L = 28, B = 22, T = 14;
  const max = Math.max(g.target, ...pts.map((p) => p.v)) || 1;
  const bw = (W - L) / n;
  const y = (v) => T + (H - T - B) * (1 - v / max);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Verlauf der letzten ${n} ${g.freq === 'weekly' ? 'Wochen' : 'Tage'}">`;
  [0, max / 2, max].forEach((v) => { s += `<line class="grid" x1="${L}" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text x="${L - 4}" y="${y(v) + 3}" text-anchor="end">${num(v)}</text>`; });
  pts.forEach((p, i) => {
    const x = L + i * bw + bw * 0.18; const w = bw * 0.64; const top = y(p.v);
    const ok = p.v >= g.target;
    if (p.v > 0) s += `<rect x="${x}" y="${top}" width="${w}" height="${Math.max(0, H - B - top)}" rx="3" fill="${g.color}" fill-opacity="${ok ? 1 : 0.42}"/>`;
    if (i % 2 === (n - 1) % 2) s += `<text x="${x + w / 2}" y="${H - 6}" text-anchor="middle">${fmt(p.d, { day: 'numeric', month: 'numeric' })}</text>`;
  });
  s += `<line class="target" x1="${L}" x2="${W}" y1="${y(g.target)}" y2="${y(g.target)}"/><text x="${W}" y="${y(g.target) - 4}" text-anchor="end">Ziel</text></svg>`;
  return s;
}

function heatmap(g) {
  const weeks = 16; const today = startOfDay(new Date());
  const start = addDays(startOfWeek(today), -7 * (weeks - 1));
  const dayTarget = g.kind === 'count' && g.freq === 'daily' ? g.target : 1;
  let cells = '';
  for (let i = 0; i < weeks * 7; i++) {
    const day = addDays(start, i); const v = dayTotal(g, day);
    if (day > today) { cells += '<i style="background:transparent"></i>'; continue; }
    const k = Math.min(v / (dayTarget || 1), 1);
    cells += v > 0 ? `<i title="${esc(fmt(day, { day: 'numeric', month: 'short' }))}: ${num(v)}" style="background:${g.color};opacity:${0.3 + 0.7 * k}"></i>` : '<i></i>';
  }
  return `<div class="heat" style="grid-template-columns:repeat(${weeks},1fr)" aria-label="Aktivität der letzten ${weeks} Wochen">${cells}</div>
    <div class="heat-foot"><span>${esc(fmt(start, { day: 'numeric', month: 'short' }))}</span><span>Heute</span></div>`;
}

/* ================= View: Ritual-Details ================= */
function viewRitual(id) {
  const r = ritualById(id);
  if (!r) return '';
  const habits = ritualHabits(r); const now = new Date();
  const free = activeGoals().filter((g) => !g.ritualId || !ritualById(g.ritualId));
  let html = backRow(`<button class="btn small" data-act="edit-ritual" data-id="${r.id}">Bearbeiten</button>`);
  html += `<section class="ritual-hero" style="${themeStyle(r.theme)}"><div class="emo">${esc(r.emoji)}</div><h1>${esc(r.name)}</h1>
    <p style="opacity:.9">${esc(ritualInfo(r))}</p>
    <div class="stats"><div><b class="num">${ritualStreak(r)}</b><small>Tage in Folge</small></div><div><b class="num">${ritualDone(r, now)}/${habits.length}</b><small>Heute</small></div></div>
    ${habits.length ? `<button class="play" data-act="play" data-id="${r.id}">${ICON.play} Ritual starten</button>` : ''}</section>`;
  html += `<p class="list-label">Gewohnheiten</p>`;
  if (habits.length) {
    html += `<div class="list">${habits.map((g, i) => `<div class="list-item" style="--gc:${g.color}">
      <span class="badge" style="width:40px;height:40px;font-size:20px">${esc(g.emoji)}</span>
      <button class="grow" style="text-align:left" data-act="open-goal" data-id="${g.id}"><span class="title">${esc(g.title)}</span><span class="sub">${g.duration ? `${g.duration} Min.` : 'Ohne Timer'}${g.kind === 'count' ? ` · ${esc(summary(g))}` : ''}</span></button>
      <span class="order-btns">
        <button class="mini-btn" data-act="move-habit" data-id="${g.id}" data-dir="-1" ${i === 0 ? 'disabled style="opacity:.3"' : ''} aria-label="Nach oben">${ICON.up}</button>
        <button class="mini-btn" data-act="move-habit" data-id="${g.id}" data-dir="1" ${i === habits.length - 1 ? 'disabled style="opacity:.3"' : ''} aria-label="Nach unten">${ICON.down}</button>
        <button class="mini-btn" data-act="unlink-habit" data-id="${g.id}" aria-label="Aus Ritual entfernen">${ICON.close.replace('<svg', '<svg width="16" height="16"')}</button>
      </span></div>`).join('')}</div>`;
  } else {
    html += `<div class="card empty"><p class="muted">Dieses Ritual hat noch keine Gewohnheiten.</p></div>`;
  }
  html += `<div class="btn-row"><button class="btn primary" data-act="new-habit" data-ritual="${r.id}">Neue Gewohnheit</button>
    ${free.length ? `<button class="btn" data-act="link-existing" data-ritual="${r.id}">Vorhandenes Ziel hinzufügen</button>` : ''}</div>`;
  html += `<p class="fine">Mit ✕ entfernst du eine Gewohnheit aus dem Ritual. Sie bleibt als eigenes Ziel erhalten.</p>`;
  return html;
}

/* ================= View: Reisen ================= */
function viewJourneys() {
  const ap = activeJourney();
  let html = `<header class="page-head"><div><p class="eyebrow">Schritt für Schritt</p><h1>Reisen</h1></div></header>`;
  if (ap) { const j = journeyById(ap.id); if (j) html += `<h2 class="section-title" style="margin-top:0">Deine aktuelle Reise</h2>${journeyBanner(j, ap)}`; }
  html += `<h2 class="section-title">${ap ? 'Weitere Reisen' : 'Wähle eine Reise'}</h2>`;
  html += JOURNEYS.filter((j) => !ap || j.id !== ap.id).map((j) => {
    const p = journeyProgress(j.id);
    const state = p?.completedAt ? '<span class="state done">🏆 Abgeschlossen</span>' : p ? `<span class="state">Pausiert · Schritt ${p.stepIndex + 1}/${j.steps.length}</span>` : `<span class="state">${j.steps.length} Schritte</span>`;
    return `<button class="card journey-tile" style="${themeStyle(j.theme)}" data-act="open-journey" data-id="${j.id}">
      <span class="emo">${j.emoji}</span><span class="grow"><h3>${esc(j.title)}</h3><p>${esc(j.subtitle)}</p>${state}</span>${ICON.chev}</button>`;
  }).join('');
  html += `<p class="fine">Jede Reise baut dir Schritt für Schritt neue Gewohnheiten auf. Neue Gewohnheiten landen automatisch im passenden Ritual.</p>`;
  return html;
}

const stepKindLabel = (s) => (s.kind === 'letter' ? 'Brief' : s.kind === 'task' ? 'Aufgabe' : `Neue Gewohnheit · ${s.days} Tage`);

function viewJourney(id) {
  const j = journeyById(id); if (!j) return '';
  const p = journeyProgress(j.id); const running = !!(p && p.active && !p.completedAt);
  const other = S.journeys.find((x) => x.active && !x.completedAt && x.id !== j.id);
  let html = backRow();
  html += `<section class="journey-hero" style="${themeStyle(j.theme)}"><div class="emo">${j.emoji}</div><h1>${esc(j.title)}</h1><p style="opacity:.92">${esc(j.subtitle)}</p>
    ${p ? `<div class="bar"><i style="width:${(Math.min(p.stepIndex, j.steps.length) / j.steps.length) * 100}%"></i></div>` : ''}</section>`;
  if (p?.completedAt) {
    html += `<section class="card"><h3>🏆 Reise abgeschlossen</h3><p class="muted">Abgeschlossen am ${esc(fmt(new Date(p.completedAt), { day: 'numeric', month: 'long', year: 'numeric' }))}.</p>
      <button class="btn" data-act="start-journey" data-id="${j.id}">Noch einmal starten</button></section>`;
  } else if (!running) {
    html += `<button class="btn primary block" style="${themeStyle(j.theme)};background:var(--b);color:#fff" data-act="start-journey" data-id="${j.id}" ${other ? 'data-switch="1"' : ''}>${p ? 'Reise fortsetzen' : 'Reise starten'}</button>`;
  }
  html += `<div class="steps" style="${themeStyle(j.theme)}">`;
  j.steps.forEach((s, i) => {
    const state = !p ? 'locked' : (i < p.stepIndex || p.completedAt) ? 'done' : (i === p.stepIndex && running) ? 'current' : 'locked';
    if (state === 'current') html += currentStep(j, s, p, i);
    else html += `<button class="step ${state}" ${state === 'done' ? `data-act="read-step" data-j="${j.id}" data-s="${s.id}"` : 'disabled'}>
      <span class="dot">${state === 'done' ? '✓' : state === 'locked' ? '🔒' : i + 1}</span>
      <span class="grow"><span class="t">${esc(s.title)}</span><span class="k">${esc(stepKindLabel(s))}</span></span>${state === 'done' ? ICON.chev : ''}</button>`;
  });
  return html + '</div>';
}

function currentStep(j, s, p, i) {
  let html = `<section class="step-current"><span class="k">Schritt ${i + 1} · ${esc(stepKindLabel(s))}</span><h2>${esc(s.title)}</h2><p class="letter">${esc(s.text)}</p>`;
  const advanceBtn = (label) => `<button class="btn primary block" style="background:var(--b);color:#fff" data-act="advance" data-id="${j.id}">${esc(label)}</button>`;
  if (s.kind === 'letter') html += advanceBtn(i + 1 >= j.steps.length ? 'Reise abschließen' : 'Weiter');
  else if (s.kind === 'task') html += advanceBtn(s.action || 'Erledigt');
  else {
    const g = p.linkedGoalId && goalById(p.linkedGoalId);
    if (!g) {
      html += `<button class="btn primary block" style="background:var(--b);color:#fff" data-act="link-blueprint" data-id="${j.id}">${ICON.plus.replace('<svg', '<svg width="18" height="18"')} Zu meinem ${esc(SLOTS[s.habit.slot].name)} hinzufügen</button>`;
    } else {
      const done = journeyDoneDays(p); const r = g.ritualId && ritualById(g.ritualId);
      html += `<div class="list-item" style="padding:0;border:0;--gc:${g.color}"><span class="badge">${esc(g.emoji)}</span><span class="grow"><span class="title">${esc(g.title)}</span><span class="sub">${r ? `Im ${esc(r.name)}` : 'Eigenständige Gewohnheit'}</span></span></div>`;
      html += `<div class="dots">${Array.from({ length: s.days }, (_, k) => `<i class="${k < done ? 'on' : ''}">${k < done ? '✓' : ''}</i>`).join('')}</div>`;
      html += `<p class="muted">${done >= s.days ? 'Super! Die Gewohnheit sitzt.' : `Erledige sie an ${s.days} Tagen, um weiterzukommen (${Math.min(done, s.days)}/${s.days}).`}</p>`;
      if (done >= s.days) html += advanceBtn('Nächster Schritt');
      else if (!isDone(g, new Date())) html += `<button class="btn block" data-act="journey-done-today" data-id="${g.id}">${ICON.check.replace('<svg', '<svg width="18" height="18"')} Heute erledigt</button>`;
      else html += `<p style="font-weight:700;color:var(--b)">✓ Für heute erledigt. Bis morgen!</p>`;
    }
  }
  return html + '</section>';
}

/* ================= View: Fortschritt ================= */
function viewProgress() {
  const goals = activeGoals(); const range = ui.range;
  let html = `<header class="page-head"><div><p class="eyebrow">Deine Entwicklung</p><h1>Fortschritt</h1></div></header>`;
  if (!goals.length) return html + `<div class="card empty"><div class="emo">📊</div><h3>Noch keine Daten</h3><p class="muted">Sobald du Gewohnheiten abhakst, siehst du hier deinen Fortschritt.</p></div>`;
  html += `<div class="seg" role="group" aria-label="Zeitraum">${[7, 30, 90].map((n) => `<button data-act="range" data-n="${n}" aria-pressed="${range === n}">${n} Tage</button>`).join('')}</div>`;
  const now = new Date();
  const doneToday = goals.filter((g) => isDone(g, now)).length;
  const rates = goals.map((g) => completionRate(g, range)).filter((r) => r != null);
  const avg = rates.length ? rates.reduce((a, b) => a + b, 0) / rates.length : null;
  const since = addDays(startOfDay(now), -range + 1).getTime();
  let entryCount = 0; for (const g of goals) for (const e of goalEntries(g)) if (e.t >= since) entryCount++;
  const streaks = [...goals.map(currentStreak), ...S.rituals.map(ritualStreak)];
  html += `<div class="tiles four">
    <div class="tile"><span class="ico">✅</span><span class="val">${doneToday}/${goals.length}</span><span class="lbl">Heute erledigt</span></div>
    <div class="tile"><span class="ico">📈</span><span class="val">${avg == null ? '–' : Math.round(avg * 100) + '%'}</span><span class="lbl">Ø Erfolgsquote</span></div>
    <div class="tile"><span class="ico">🔥</span><span class="val">${Math.max(0, ...streaks)}</span><span class="lbl">Längste aktive Serie</span></div>
    <div class="tile"><span class="ico">📝</span><span class="val">${entryCount}</span><span class="lbl">Einträge (${range} Tage)</span></div></div>`;
  html += `<section class="card"><h3>Erledigt pro Tag</h3>${dailyChart(goals, range)}</section>`;
  if (S.rituals.length) {
    html += `<section class="card"><h3>Rituale</h3>${sortedRituals().map((r) => {
      const h = ritualHabits(r); let days = 0, full = 0;
      for (let i = 0; i < range; i++) { const d = addDays(startOfDay(now), -i); if (d < startOfDay(new Date(r.createdAt))) break; days++; if (ritualCompleted(r, d)) full++; }
      const st = ritualStreak(r);
      return `<button class="rate-row" data-act="open-ritual" data-id="${r.id}" style="${themeStyle(r.theme)};--gc:var(--b)">
        <span class="badge" style="background:linear-gradient(150deg,var(--a),var(--b))">${esc(r.emoji)}</span>
        <span class="grow"><span class="name">${esc(r.name)}</span><span class="bar dark"><i style="width:${days ? (full / days) * 100 : 0}%"></i></span></span>
        <span class="right"><b class="num">${full}/${days || 0}</b><span class="muted">${st ? `🔥 ${st}` : `${h.length} Gew.`}</span></span></button>`;
    }).join('')}</section>`;
  }
  html += `<section class="card"><h3>Alle Gewohnheiten & Ziele</h3>${[...goals].sort((a, b) => currentStreak(b) - currentStreak(a)).map((g) => {
    const r = completionRate(g, range); const st = currentStreak(g);
    return `<button class="rate-row" data-act="open-goal" data-id="${g.id}" style="--gc:${g.color}"><span class="badge">${esc(g.emoji)}</span>
      <span class="grow"><span class="name">${esc(g.title)}</span><span class="bar dark"><i style="width:${(r || 0) * 100}%"></i></span></span>
      <span class="right"><b class="num">${r == null ? '–' : Math.round(r * 100) + '%'}</b><span style="color:${st ? 'var(--streak)' : 'var(--muted)'}">🔥 ${st}</span></span></button>`;
  }).join('')}</section>`;
  return html;
}

function dailyChart(goals, range) {
  const daily = goals.filter((g) => g.freq === 'daily');
  const list = daily.length ? daily : goals;
  const today = startOfDay(new Date()); const pts = [];
  for (let i = range - 1; i >= 0; i--) {
    const d = addDays(today, -i);
    const rel = list.filter((g) => startOfDay(trackingStart(g)) <= d);
    pts.push({ d, f: rel.length ? rel.filter((g) => isDone(g, d)).length / rel.length : 0 });
  }
  const W = 340, H = 160, L = 30, B = 22, T = 10;
  const bw = (W - L) / pts.length; const y = (v) => T + (H - T - B) * (1 - v);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Anteil erledigter Gewohnheiten pro Tag">`;
  [0, 0.5, 1].forEach((v) => { s += `<line class="grid" x1="${L}" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text x="${L - 4}" y="${y(v) + 3}" text-anchor="end">${v * 100}%</text>`; });
  const every = range <= 7 ? 1 : range <= 30 ? 5 : 15;
  pts.forEach((p, i) => {
    const x = L + i * bw + bw * 0.15; const w = Math.max(1.5, bw * 0.7); const top = y(p.f);
    if (p.f > 0) s += `<rect x="${x}" y="${top}" width="${w}" height="${H - B - top}" rx="${Math.min(3, w / 2)}" fill="var(--accent)" fill-opacity="${p.f >= 1 ? 1 : 0.55}"/>`;
    if ((pts.length - 1 - i) % every === 0) s += `<text x="${x + w / 2}" y="${H - 6}" text-anchor="middle">${range <= 7 ? fmt(p.d, { weekday: 'short' }).slice(0, 2) : fmt(p.d, { day: 'numeric', month: 'numeric' })}</text>`;
  });
  return s + '</svg>';
}

/* ================= View: Ich ================= */
function viewMe() {
  const goals = activeGoals(); const archived = S.goals.filter((g) => g.archived);
  let entryCount = 0; for (const k of Object.keys(M)) entryCount += M[k].entries.length;
  const best = Math.max(0, ...S.goals.map(bestStreak), ...S.rituals.map(ritualStreak));
  const since = new Date(S.profile.createdAt || Date.now());
  const initial = (S.profile.name || '').trim().charAt(0).toUpperCase() || '🙂';
  let html = `<header class="page-head"><div><p class="eyebrow">Profil</p><h1>Ich</h1></div></header>`;
  html += `<section class="card profile"><span class="avatar">${esc(initial)}</span><div style="flex:1;min-width:0">
    <label class="sr-only" for="me-name">Dein Name</label>
    <input id="me-name" data-field="profile-name" value="${esc(S.profile.name)}" placeholder="Dein Name" autocomplete="given-name">
    <p class="muted" style="font-size:14px">Dabei seit ${esc(fmt(since, { day: 'numeric', month: 'long', year: 'numeric' }))}</p></div></section>`;
  html += `<div class="tiles four">
    <div class="tile"><span class="ico">✅</span><span class="val">${entryCount}</span><span class="lbl">Einträge insgesamt</span></div>
    <div class="tile"><span class="ico">🔥</span><span class="val">${best}</span><span class="lbl">Längste Serie</span></div>
    <div class="tile"><span class="ico">🏆</span><span class="val">${S.journeys.filter((p) => p.completedAt).length}/${JOURNEYS.length}</span><span class="lbl">Reisen abgeschlossen</span></div>
    <div class="tile"><span class="ico">🎯</span><span class="val">${goals.length}</span><span class="lbl">Aktive Gewohnheiten</span></div></div>`;

  html += `<p class="list-label">Rituale</p><div class="list">${sortedRituals().map((r) => `
    <button class="list-item" data-act="open-ritual" data-id="${r.id}"><span class="badge" style="${themeStyle(r.theme)};background:linear-gradient(150deg,var(--a),var(--b));width:40px;height:40px;font-size:20px">${esc(r.emoji)}</span>
    <span class="grow"><span class="title">${esc(r.name)}</span><span class="sub">${esc(ritualInfo(r))}</span></span>${ICON.chev}</button>`).join('')}
    <button class="list-item" data-act="new-ritual" style="color:var(--accent);font-weight:700">${ICON.plus.replace('<svg', '<svg width="20" height="20"')} Neues Ritual</button></div>`;

  html += `<p class="list-label">Gewohnheiten & Ziele</p><div class="list">${goals.map((g) => goalListItem(g)).join('')}
    <button class="list-item" data-act="new-goal" style="color:var(--accent);font-weight:700">${ICON.plus.replace('<svg', '<svg width="20" height="20"')} Neues Ziel</button></div>`;
  if (archived.length) {
    html += `<button class="btn small ghost" data-act="toggle-archived" style="align-self:flex-start">${ui.showArchived ? 'Archiv ausblenden' : `Archiv anzeigen (${archived.length})`}</button>`;
    if (ui.showArchived) html += `<div class="list">${archived.map((g) => goalListItem(g)).join('')}</div>`;
  }

  html += `<p class="list-label">Daten & Sync</p><section class="card">${syncHTML()}
    <p class="hint">${Cloud.enabled ? 'Öffne Fabulous auf iPhone und iPad mit demselben claude.ai-Konto, dann sind deine Daten überall gleich.' : 'Deine Daten liegen im Browser dieses Geräts. Sichere sie ab und zu als Backup.'}</p>
    <div class="btn-row"><button class="btn small" data-act="export">Backup sichern</button>
    <label class="btn small" for="import-file" style="cursor:pointer">Backup laden</label></div>
    <input type="file" id="import-file" accept="application/json,.json" class="sr-only" data-field="import"></section>`;

  html += `<p class="list-label">Einstellungen</p><div class="list">
    <button class="list-item" data-act="rerun-onboarding"><span class="grow"><span class="title">Einführung erneut ansehen</span></span>${ICON.chev}</button>
    <button class="list-item" data-act="install-help"><span class="grow"><span class="title">Auf den Home-Bildschirm legen</span><span class="sub">So startest du Fabulous wie eine App</span></span>${ICON.chev}</button>
    <button class="list-item" data-act="reset-all" style="color:var(--danger)"><span class="grow"><span class="title">Alle Daten löschen</span></span></button></div>`;
  html += `<p class="fine">Fabulous ist kostenlos und werbefrei. Kein Abo, keine Werbung.</p>`;
  return html;
}
function goalListItem(g) {
  const r = g.ritualId && ritualById(g.ritualId);
  return `<button class="list-item" data-act="open-goal" data-id="${g.id}" style="--gc:${g.color}"><span class="badge" style="width:40px;height:40px;font-size:20px">${esc(g.emoji)}</span>
    <span class="grow"><span class="title">${esc(g.title)}</span><span class="sub">${r ? `${esc(r.emoji)} ${esc(r.name)}` : esc(summary(g))}${g.archived ? ' · archiviert' : ''}</span></span>${ICON.chev}</button>`;
}

/* ================= Sheets ================= */
let sheetReturnFocus = null;
function openSheet(sheet) {
  sheetReturnFocus = document.activeElement;
  ui.sheet = sheet; renderSheet(true);
  document.body.classList.add('locked');
}
function closeSheet() {
  ui.sheet = null; const root = $('#sheet-root'); if (root) root.innerHTML = '';
  document.body.classList.remove('locked');
  try { sheetReturnFocus?.focus?.({ preventScroll: true }); } catch (e) { /* ignore */ }
}
function renderSheet(first = false) {
  const sh = ui.sheet; if (!sh) return;
  const root = $('#sheet-root');
  const prevScroll = root.querySelector('.sheet-body')?.scrollTop || 0;
  const content = SHEETS[sh.kind](sh);
  root.innerHTML = `<div class="backdrop" data-act="close-sheet"></div>
    <div class="sheet" role="dialog" aria-modal="true" aria-label="${esc(content.title)}">
      <div class="sheet-head"><span class="l"><button data-act="close-sheet">${esc(content.cancel || 'Abbrechen')}</button></span><h2>${esc(content.title)}</h2>
      <span class="r">${content.save ? `<button data-act="${content.save.act}" ${content.save.disabled ? 'disabled' : ''}>${esc(content.save.label)}</button>` : ''}</span></div>
      <div class="sheet-body">${content.body}</div></div>`;
  const body = root.querySelector('.sheet-body');
  if (first) { const f = root.querySelector('[data-autofocus]'); if (f && !('ontouchstart' in window)) f.focus(); else root.querySelector('.sheet-head button')?.focus({ preventScroll: true }); }
  else body.scrollTop = prevScroll;
}

const SHEETS = {
  'add-menu': () => ({
    title: 'Hinzufügen', cancel: 'Schließen',
    body: `<button class="choice" data-act="new-ritual"><span class="emo">🌅</span><span class="grow"><b>Neues Ritual</b><small>Eine Routine aus mehreren Gewohnheiten, z. B. morgens oder abends</small></span></button>
      <button class="choice" data-act="new-goal"><span class="emo">🎯</span><span class="grow"><b>Neues Ziel / Tracker</b><small>Abhaken oder Mengen zählen, täglich oder wöchentlich</small></span></button>
      <button class="choice" data-act="go-tab" data-tab="reisen"><span class="emo">🗺️</span><span class="grow"><b>Eine Reise starten</b><small>Geführte Programme mit neuen Gewohnheiten</small></span></button>`,
  }),

  'goal-editor': (sh) => {
    const d = sh.draft; const isNew = !sh.id;
    const ritualOpts = sortedRituals().map((r) => `<option value="${r.id}" ${d.ritualId === r.id ? 'selected' : ''}>${esc(r.emoji)} ${esc(r.name)}</option>`).join('');
    const valid = d.title.trim() && Number(d.target) > 0 && (d.kind === 'check' || Number(d.step) > 0);
    let body = '';
    if (isNew) body += `<div class="field"><span class="label">Vorlagen</span><div class="scroller">${TEMPLATES.map((t, i) =>
      `<button class="tpl" data-act="tpl" data-i="${i}"><span>${t.emoji}</span><span>${esc(t.title)}</span></button>`).join('')}</div></div>`;
    body += `<div class="field"><label for="g-title">Name</label><div class="title-row" style="--gc:${d.color}"><span class="preview">${esc(d.emoji)}</span>
      <input class="input big" id="g-title" data-field="title" value="${esc(d.title)}" placeholder="z. B. Wasser trinken" maxlength="60" data-autofocus></div></div>`;
    body += `<div class="field"><span class="label">Symbol</span><div class="emoji-grid">${EMOJIS.map((e) => `<button data-act="pick-emoji" data-v="${e}" aria-pressed="${d.emoji === e}" aria-label="${e}">${e}</button>`).join('')}</div>
      <input class="input" id="g-emoji" data-field="emoji" value="" placeholder="Oder eigenes Emoji eintippen" maxlength="8" inputmode="text"></div>`;
    body += `<div class="field"><span class="label">Farbe</span><div class="swatches">${COLORS.map((c) => `<button class="swatch" style="background:${c}" data-act="pick-color" data-v="${c}" aria-pressed="${d.color === c}" aria-label="Farbe ${c}"></button>`).join('')}</div></div>`;
    body += `<div class="field"><span class="label">Art</span><div class="seg">
      <button data-act="set" data-k="kind" data-v="check" aria-pressed="${d.kind === 'check'}">Abhaken</button>
      <button data-act="set" data-k="kind" data-v="count" aria-pressed="${d.kind === 'count'}">Zählen</button></div>
      <div class="seg"><button data-act="set" data-k="freq" data-v="daily" aria-pressed="${d.freq === 'daily'}">Täglich</button>
      <button data-act="set" data-k="freq" data-v="weekly" aria-pressed="${d.freq === 'weekly'}">Wöchentlich</button></div>
      <p class="hint">${d.kind === 'check' ? 'Hake das Ziel ab, sobald du es erledigt hast.' : 'Zähle Mengen wie Gläser, Seiten, Minuten oder Euro.'}</p></div>`;
    if (d.kind === 'check' && d.freq === 'weekly') {
      body += `<div class="field"><span class="label">Wie oft pro Woche?</span><div class="stepper"><button data-act="step-target" data-dir="-1" aria-label="Weniger">−</button><b class="num">${d.target}× pro Woche</b><button data-act="step-target" data-dir="1" aria-label="Mehr">+</button></div></div>`;
    }
    if (d.kind === 'count') {
      body += `<div class="row2"><div class="field"><label for="g-target">Ziel ${d.freq === 'weekly' ? 'pro Woche' : 'pro Tag'}</label><input class="input" id="g-target" data-field="target" type="number" inputmode="decimal" min="0" step="any" value="${esc(d.target)}"></div>
        <div class="field"><label for="g-unit">Einheit</label><input class="input" id="g-unit" data-field="unit" value="${esc(d.unit)}" placeholder="Gläser" maxlength="20"></div></div>
        <div class="field"><label for="g-step">Pro Tipp auf +</label><input class="input" id="g-step" data-field="step" type="number" inputmode="decimal" min="0" step="any" value="${esc(d.step)}"></div>`;
    }
    body += `<div class="field"><label for="g-ritual">Ritual</label><select class="select" id="g-ritual" data-field="ritualId"><option value="">Keins (eigenständiges Ziel)</option>${ritualOpts}</select>
      ${d.ritualId ? `<label for="g-duration" class="hint">Dauer im Ritual-Modus (Minuten, 0 = ohne Timer)</label><input class="input" id="g-duration" data-field="duration" type="number" inputmode="numeric" min="0" max="180" value="${esc(d.duration)}">` : '<p class="hint">Gewohnheiten in einem Ritual erscheinen im geführten Ritual-Modus, auf Wunsch mit Timer.</p>'}</div>`;
    body += `<div class="field"><label for="g-notes">Tipp / Motivation</label><textarea class="textarea" id="g-notes" data-field="notes" placeholder="Warum ist dir das wichtig?" maxlength="500">${esc(d.notes)}</textarea></div>`;
    return { title: isNew ? (d.ritualId ? 'Neue Gewohnheit' : 'Neues Ziel') : 'Bearbeiten', body, save: { act: 'save-goal', label: 'Sichern', disabled: !valid } };
  },

  'ritual-editor': (sh) => {
    const d = sh.draft; const isNew = !sh.id;
    let body = '';
    if (isNew) body += `<div class="field"><span class="label">Vorlagen</span><div class="scroller">${Object.entries(SLOTS).map(([k, s]) =>
      `<button class="tpl" data-act="ritual-tpl" data-k="${k}" style="width:110px"><span>${s.emoji}</span><span>${esc(s.name)}</span></button>`).join('')}</div></div>`;
    body += `<div class="field"><label for="r-name">Name</label><div class="title-row" style="${themeStyle(d.theme)}"><span class="preview" style="background:linear-gradient(150deg,var(--a),var(--b))">${esc(d.emoji)}</span>
      <input class="input big" id="r-name" data-field="name" value="${esc(d.name)}" placeholder="z. B. Morgenritual" maxlength="40" data-autofocus></div></div>`;
    body += `<div class="field"><span class="label">Symbol</span><div class="emoji-grid">${RITUAL_EMOJIS.map((e) => `<button data-act="pick-emoji" data-v="${e}" aria-pressed="${d.emoji === e}" aria-label="${e}">${e}</button>`).join('')}</div></div>`;
    body += `<div class="field"><span class="label">Farbe</span><div class="swatches">${Object.entries(THEMES).map(([k, t]) =>
      `<button class="swatch theme" style="background:linear-gradient(150deg,${t.a},${t.b})" data-act="pick-theme" data-v="${k}" aria-pressed="${d.theme === k}" aria-label="${esc(t.name)}"></button>`).join('')}</div></div>`;
    body += `<div class="field"><label for="r-time">Uhrzeit</label><input class="input" id="r-time" type="time" data-field="time" value="${esc(d.time)}"></div>`;
    if (!isNew) body += `<button class="btn danger" data-act="delete-ritual" data-id="${sh.id}">Ritual löschen</button><p class="hint">Die Gewohnheiten bleiben als eigene Ziele erhalten.</p>`;
    return { title: isNew ? 'Neues Ritual' : 'Ritual bearbeiten', body, save: { act: 'save-ritual', label: 'Sichern', disabled: !d.name.trim() } };
  },

  amount: (sh) => {
    const g = goalById(sh.goalId); if (!g) return { title: '', body: '' };
    const s = g.step > 0 ? g.step : 1;
    const quick = g.kind === 'count' ? [s, s * 2, s * 5, s * 10] : [];
    let body = `<p class="muted">${esc(fmt(sh.date, { weekday: 'long', day: 'numeric', month: 'long' }))}</p>`;
    if (g.kind === 'count') {
      body += `<div class="field"><label for="a-amount">Menge${g.unit ? ` (${esc(g.unit)})` : ''}</label><input class="input big" id="a-amount" data-field="amount" type="number" inputmode="decimal" min="0" step="any" value="${esc(sh.amount)}" data-autofocus></div>
        <div class="quick">${quick.map((v) => `<button data-act="quick" data-v="${v}">${num(v)}</button>`).join('')}</div>`;
    }
    body += `<div class="field"><label for="a-note">Notiz</label><textarea class="textarea" id="a-note" data-field="note" placeholder="Optional, z. B. wie es lief" maxlength="300" ${g.kind === 'check' ? 'data-autofocus' : ''}>${esc(sh.note)}</textarea></div>`;
    return { title: `${g.emoji} ${g.title}`, body, save: { act: 'save-amount', label: g.kind === 'check' ? 'Abhaken' : 'Hinzufügen', disabled: g.kind === 'count' && !(Number(sh.amount) > 0) } };
  },

  confirm: (sh) => ({
    title: sh.title,
    body: `<p class="confirm-text">${esc(sh.text)}</p><button class="btn ${sh.danger ? 'danger' : 'primary'} block" style="${sh.danger ? 'background:var(--danger);color:#fff' : ''}" data-act="confirm-ok">${esc(sh.ok)}</button>`,
  }),

  'read-step': (sh) => ({ title: sh.step.title, cancel: 'Schließen', body: `<p class="letter">${esc(sh.step.text)}</p>` }),

  'link-existing': (sh) => {
    const free = activeGoals().filter((g) => !g.ritualId || !ritualById(g.ritualId));
    return {
      title: 'Ziel hinzufügen',
      body: free.length ? `<div class="list">${free.map((g) => `<button class="list-item" data-act="do-link" data-id="${g.id}" data-ritual="${sh.ritualId}" style="--gc:${g.color}">
        <span class="badge" style="width:40px;height:40px;font-size:20px">${esc(g.emoji)}</span><span class="grow"><span class="title">${esc(g.title)}</span><span class="sub">${esc(summary(g))}</span></span>${ICON.plus.replace('<svg', '<svg width="20" height="20" style="color:var(--accent)"')}</button>`).join('')}</div>`
        : '<p class="muted">Alle Ziele sind schon in Ritualen.</p>',
    };
  },

  export: (sh) => ({
    title: 'Backup', cancel: 'Schließen',
    body: `<p>Kopiere diesen Text und bewahre ihn z. B. in der Notizen-App auf. Mit „Backup laden“ kannst du ihn später wieder einspielen.</p>
      <textarea class="textarea" id="export-text" readonly style="min-height:200px;font-size:12px;font-family:ui-monospace,monospace">${esc(sh.text)}</textarea>
      <button class="btn primary block" data-act="copy-export">Text kopieren</button>
      <p class="hint">Zum Laden kannst du den Text auch als .json-Datei speichern und über „Backup laden“ auswählen, oder hier einfügen:</p>
      <textarea class="textarea" id="import-text" data-field="import-text" placeholder="Backup-Text hier einfügen" style="font-size:12px;font-family:ui-monospace,monospace"></textarea>
      <button class="btn block" data-act="import-text">Eingefügten Text laden</button>`,
  }),

  install: () => ({
    title: 'Auf den Home-Bildschirm', cancel: 'Schließen',
    body: `<div class="card"><h3>iPhone & iPad (Safari)</h3><ol style="margin:0;padding-left:20px;line-height:1.7">
        <li>Öffne Fabulous in <b>Safari</b>.</li><li>Tippe auf das <b>Teilen</b>-Symbol (Quadrat mit Pfeil nach oben).</li>
        <li>Wähle <b>„Zum Home-Bildschirm“</b> und tippe auf <b>Hinzufügen</b>.</li></ol></div>
      <p class="hint">Danach startest du Fabulous mit einem Tipp vom Home-Bildschirm wie eine normale App. Deine Daten bleiben auf dem jeweiligen Gerät. Mit „Backup sichern“ und „Backup laden“ überträgst du sie auf ein anderes Gerät.</p>`,
  }),
};

/* ---- editors ---- */
function openGoalEditor(goal, preset = {}) {
  const base = goal ? { ...goal } : newGoal(preset);
  openSheet({ kind: 'goal-editor', id: goal?.id || null, draft: {
    title: base.title, emoji: base.emoji, color: base.color, kind: base.kind, freq: base.freq, target: base.target,
    unit: base.unit, step: base.step, ritualId: base.ritualId || '', duration: base.duration ?? 0, notes: base.notes,
  } });
}
function saveGoal() {
  const sh = ui.sheet; const d = sh.draft;
  if (!d.title.trim()) return;
  let target = Number(d.target);
  if (d.kind === 'check') target = d.freq === 'weekly' ? clamp(Math.round(target) || 1, 1, 7) : 1;
  if (!(target > 0)) return toast('Bitte gib ein Ziel größer als 0 ein.');
  const fields = {
    title: d.title.trim(), emoji: d.emoji || '⭐️', color: d.color, kind: d.kind, freq: d.freq, target,
    unit: d.kind === 'count' ? d.unit.trim() : '', step: d.kind === 'count' ? (Number(d.step) > 0 ? Number(d.step) : 1) : 1,
    notes: d.notes.trim(), duration: d.ritualId ? clamp(Math.round(Number(d.duration) || 0), 0, 180) : 0,
  };
  let g = sh.id && goalById(sh.id);
  if (g) Object.assign(g, fields); else { g = newGoal(fields); S.goals.push(g); }
  const newRitual = d.ritualId && ritualById(d.ritualId);
  if ((g.ritualId || '') !== (d.ritualId || '')) { if (newRitual) addToRitual(g, newRitual); else g.ritualId = null; }
  closeSheet(); commit();
  toast(sh.id ? 'Gespeichert' : `„${g.title}“ angelegt`);
}
function openRitualEditor(r) {
  const base = r ? { ...r } : { name: '', emoji: '🌤️', theme: 'afternoon', time: '13:00' };
  openSheet({ kind: 'ritual-editor', id: r?.id || null, draft: { name: base.name, emoji: base.emoji, theme: base.theme, time: base.time } });
}
function saveRitual() {
  const sh = ui.sheet; const d = sh.draft;
  if (!d.name.trim()) return;
  const fields = { name: d.name.trim(), emoji: d.emoji, theme: d.theme, time: d.time || '07:00' };
  let r = sh.id && ritualById(sh.id);
  if (r) Object.assign(r, fields); else { r = { id: uid(), slot: d.slot || '', createdAt: Date.now(), ...fields }; S.rituals.push(r); }
  closeSheet(); commit();
  toast(sh.id ? 'Gespeichert' : `„${r.name}“ angelegt`);
}
function confirmSheet(title, text, ok, onOk, danger = false) {
  openSheet({ kind: 'confirm', title, text, ok, onOk, danger });
}

/* ================= Player (geführter Ritual-Modus) ================= */
let playerTick = null; let wakeLock = null;
function startPlayer(rid) {
  const r = ritualById(rid); if (!r) return;
  unlockAudio();
  const habits = ritualHabits(r); if (!habits.length) return;
  const open = habits.filter((g) => !isDone(g, new Date()));
  ui.player = { rid, queue: (open.length ? open : habits).map((g) => g.id), i: 0, done: 0, finished: false };
  preparePlayerStep();
  document.body.classList.add('locked');
  try { navigator.wakeLock?.request('screen').then((l) => { wakeLock = l; }).catch(() => {}); } catch (e) { /* ignore */ }
  renderPlayer();
  clearInterval(playerTick); playerTick = setInterval(tickPlayer, 250);
}
function preparePlayerStep() {
  const p = ui.player; const g = goalById(p.queue[p.i]);
  const dur = g ? (Number(g.duration) || 0) * 60000 : 0;
  Object.assign(p, { duration: dur, remaining: dur, endAt: dur ? Date.now() + dur : 0, running: dur > 0, rang: false });
}
function closePlayer() {
  clearInterval(playerTick); ui.player = null;
  document.querySelectorAll('.confetti').forEach((c) => c.remove());
  $('#player-root').innerHTML = '';
  document.body.classList.remove('locked');
  try { wakeLock?.release?.(); } catch (e) { /* ignore */ } wakeLock = null;
  renderApp();
}
const mmss = (ms) => { const s = Math.ceil(ms / 1000); return `${Math.floor(s / 60)}:${pad(s % 60)}`; };
function tickPlayer() {
  const p = ui.player; if (!p || p.finished || !p.duration) return;
  if (p.running) p.remaining = Math.max(0, p.endAt - Date.now());
  if (p.remaining === 0 && !p.rang) { p.rang = true; p.running = false; chime([523, 659, 784]); renderPlayer(); return; }
  const t = $('#player-time'); if (t) t.textContent = mmss(p.remaining);
  const c = $('#player-ring circle:last-child');
  if (c) { const len = Number(c.getAttribute('stroke-dasharray')); c.setAttribute('stroke-dashoffset', String(len * (p.remaining / p.duration))); c.setAttribute('stroke-opacity', '1'); }
}
function renderPlayer() {
  const p = ui.player; if (!p) return;
  const r = ritualById(p.rid); if (!r) return closePlayer();
  const root = $('#player-root');
  let inner;
  if (p.finished) {
    const st = ritualStreak(r); const h = ritualHabits(r);
    inner = `<div class="celebrate"><div class="emo">🎉</div><h1>${esc(r.name)} geschafft!</h1>
      <p style="opacity:.9">${ritualDone(r, new Date())} von ${h.length} Gewohnheiten erledigt</p>
      ${st ? `<span class="chip">🔥 ${st} ${st === 1 ? 'Tag' : 'Tage'} in Folge</span>` : ''}
      <p style="opacity:.8;font-style:italic;max-width:30ch">${esc(quoteFor(new Date()))}</p></div>
      <div class="player-actions"><button class="main" data-act="player-close">Fertig</button></div>`;
  } else {
    const g = goalById(p.queue[p.i]);
    if (!g) { p.i++; if (p.i >= p.queue.length) p.finished = true; else preparePlayerStep(); return renderPlayer(); }
    const caps = p.queue.map((_, k) => `<i class="${k < p.i ? 'on' : k === p.i ? 'cur' : ''}"></i>`).join('');
    const frac = p.duration ? 1 - p.remaining / p.duration : 0;
    inner = `<div class="player-top"><button class="player-close" data-act="player-close" aria-label="Schließen">${ICON.close}</button>
        <span class="t">${esc(r.emoji)} ${esc(r.name)} · ${p.i + 1}/${p.queue.length}</span><span></span></div>
      <div class="progress-caps">${caps}</div>
      <div class="player-step" key="${g.id}"><div class="emo">${esc(g.emoji)}</div><h1>${esc(g.title)}</h1>${g.notes ? `<p>${esc(g.notes)}</p>` : ''}
        ${p.duration ? `<button class="timer" data-act="player-toggle" aria-label="${p.running ? 'Timer pausieren' : 'Timer fortsetzen'}">
          <span id="player-ring">${ring(frac, 190, 9, '#fff', '#fff', 0.25)}</span>
          <span class="center"><span class="time" id="player-time">${mmss(p.remaining)}</span>${p.remaining === 0 ? '<span style="font-weight:700">Zeit um!</span>' : p.running ? ICON.pause : ICON.play}</span></button>` : ''}
      </div>
      <div class="player-actions"><button class="main" data-act="player-done">${p.duration && p.remaining > 0 ? 'Schon erledigt' : 'Erledigt'}</button>
        <button class="skip" data-act="player-skip">Überspringen</button></div>`;
  }
  root.innerHTML = `<div class="player" style="${themeStyle(r.theme)}" role="dialog" aria-modal="true" aria-label="${esc(r.name)}"><div class="player-inner">${inner}</div></div>`;
  if (p.finished && !p.confettiDone) { p.confettiDone = true; confetti(); chime([523, 659, 784, 1046]); }
}
function playerNext() {
  const p = ui.player;
  if (p.i + 1 < p.queue.length) { p.i++; preparePlayerStep(); } else { p.finished = true; p.running = false; }
  renderPlayer();
}
function confetti() {
  if (reduceMotion()) return;
  const c = document.createElement('canvas'); c.className = 'confetti';
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  c.width = innerWidth * dpr; c.height = innerHeight * dpr; document.body.appendChild(c);
  const ctx = c.getContext('2d'); ctx.scale(dpr, dpr);
  const cols = ['#FFD166', '#FF6B6B', '#4ECDC4', '#FFFFFF', '#A78BFA', '#34D399'];
  const parts = Array.from({ length: 140 }, () => ({
    x: innerWidth / 2 + (Math.random() - 0.5) * 80, y: innerHeight * 0.35, vx: (Math.random() - 0.5) * 12, vy: -Math.random() * 13 - 4,
    s: Math.random() * 7 + 4, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.3, c: cols[(Math.random() * cols.length) | 0],
  }));
  const t0 = performance.now();
  (function frame(t) {
    const el = t - t0; ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (const p of parts) {
      p.vy += 0.32; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c; ctx.globalAlpha = Math.max(0, 1 - el / 2800);
      ctx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); ctx.restore();
    }
    if (el < 2800) requestAnimationFrame(frame); else c.remove();
  })(t0);
}

/* ================= Onboarding ================= */
function renderOnboarding() {
  const o = ui.ob; const root = $('#app');
  document.body.classList.remove('locked');
  const steps = 4;
  let content;
  if (o.step === 0) {
    content = `<div class="big">✨</div><h1>Willkommen bei <span class="wordmark">Fabulous</span></h1>
      <p>Baue dir Schritt für Schritt Gewohnheiten auf, die dich gesünder, glücklicher und fokussierter machen.</p>
      <p style="font-size:15px;opacity:.8">Kostenlos. Ohne Abo. Ohne Werbung.</p>`;
  } else if (o.step === 1) {
    content = `<div class="big">👋</div><h1>Wie heißt du?</h1><label class="sr-only" for="ob-name">Vorname</label>
      <input id="ob-name" data-field="ob-name" value="${esc(o.name)}" placeholder="Dein Vorname" autocomplete="given-name" maxlength="30" enterkeyhint="next">`;
  } else if (o.step === 2) {
    content = `<h1 style="font-size:clamp(28px,7vw,36px)">Was möchtest du verändern?</h1><p>Wähle deine erste Reise. Du kannst später jederzeit wechseln.</p>
      ${JOURNEYS.map((j) => `<button class="choice" data-act="ob-journey" data-id="${j.id}" aria-pressed="${o.journey === j.id}"><span class="emo">${j.emoji}</span>
        <span class="grow"><b>${esc(j.title)}</b><small>${esc(j.subtitle)}</small></span></button>`).join('')}`;
  } else {
    content = `<div class="big">⏰</div><h1>Wann stehst du auf?</h1><p>Dein Morgenritual beginnt zu dieser Zeit.</p>
      <label class="sr-only" for="ob-wake">Aufstehzeit</label><input id="ob-wake" type="time" data-field="ob-wake" value="${esc(o.wake)}">`;
  }
  root.innerHTML = `<div class="onb"><div class="onb-inner"><div class="onb-step" key="${o.step}">${content}</div>
    <div class="onb-dots" aria-hidden="true">${Array.from({ length: steps }, (_, i) => `<i class="${i === o.step ? 'on' : ''}"></i>`).join('')}</div>
    <button class="onb-next" data-act="ob-next">${o.step < steps - 1 ? 'Weiter' : 'Los geht’s'}</button>
    ${o.step > 0 ? '<button class="onb-back" data-act="ob-back">Zurück</button>' : ''}</div></div>`;
}
function finishOnboarding() {
  const o = ui.ob;
  S.profile.name = o.name.trim();
  if (!S.profile.createdAt) S.profile.createdAt = Date.now();
  if (!S.rituals.length) {
    const morning = makeRitual('morning', o.wake || '07:00'); const evening = makeRitual('evening');
    S.rituals.push(morning, evening);
    const water = newGoal({ title: 'Ein Glas Wasser trinken', emoji: '💧', color: '#3CC2E0', duration: 1, notes: 'Stell dir das Glas schon am Abend neben das Bett.' });
    S.goals.push(water); addToRitual(water, morning);
    const reflect = newGoal({ title: 'Tag reflektieren', emoji: '✍️', color: '#64708A', duration: 5, notes: 'Was lief heute gut? Drei Sätze reichen.' });
    S.goals.push(reflect); addToRitual(reflect, evening);
  } else {
    const morning = S.rituals.find((r) => r.slot === 'morning'); if (morning && o.wake) morning.time = o.wake;
  }
  const j = journeyById(o.journey);
  if (j && !activeJourney()) startJourney(j);
  S.profile.onboarded = true; sessionOnboarded = true;
  ui.mode = 'app'; ui.tab = 'heute'; ui.stack = []; ui.date = new Date();
  $('#app').innerHTML = '';
  commit();
  setHash('heute');
  toast(`Willkommen${S.profile.name ? ', ' + S.profile.name : ''}! Dein erstes Ritual wartet.`);
}

/* ================= Navigation ================= */
const HASH_TABS = ['heute', 'reisen', 'fortschritt', 'ich'];
function setHash(t) { try { if (location.hash !== '#' + t) history.replaceState(null, '', '#' + t); } catch (e) { /* ignore */ } }
function goTab(t) {
  if (!HASH_TABS.includes(t)) t = 'heute';
  ui.tab = t; ui.stack = []; if (t === 'heute') ui.date = ui.date || new Date();
  closeSheet(); setHash(t); renderApp(); window.scrollTo(0, 0);
}
function push(type, id) { ui.stack.push({ type, id, scroll: window.scrollY }); closeSheet(); renderApp(); window.scrollTo(0, 0); }
function pop() { const top = ui.stack.pop(); renderApp(); window.scrollTo(0, top ? top.scroll : 0); }

/* ================= Actions ================= */
function sheetDate() { return ui.stack.length ? new Date() : ui.date; }
const A = {
  'go-tab': (el) => goTab(el.dataset.tab),
  back: () => pop(),
  'go-today': () => { ui.date = new Date(); renderApp(); },
  'pick-day': (el) => { ui.date = fromDayKey(el.dataset.day); renderApp(); },
  week: (el) => {
    const n = addDays(ui.date, 7 * Number(el.dataset.dir)); const today = new Date();
    ui.date = n > today ? today : n; renderApp();
  },
  'add-menu': () => openSheet({ kind: 'add-menu' }),
  'new-goal': () => { closeSheet(); openGoalEditor(null); },
  'new-habit': (el) => { closeSheet(); openGoalEditor(null, { ritualId: el.dataset.ritual, duration: 2 }); },
  'new-ritual': () => { closeSheet(); openRitualEditor(null); },
  'edit-goal': (el) => openGoalEditor(goalById(el.dataset.id)),
  'edit-ritual': (el) => openRitualEditor(ritualById(el.dataset.id)),
  'open-goal': (el) => push('goal', el.dataset.id),
  'open-ritual': (el) => push('ritual', el.dataset.id),
  'open-journey': (el) => push('journey', el.dataset.id),
  'close-sheet': () => closeSheet(),

  'toggle-habit': (el) => {
    const g = goalById(el.dataset.id); if (!g) return;
    const r = g.ritualId && ritualById(g.ritualId); const before = r && ritualCompleted(r, ui.date);
    const months = toggleDone(g, ui.date); commit({ app: false, months });
    if (r && !before && ritualCompleted(r, ui.date)) { unlockAudio(); chime([523, 659, 784]); toast(`${r.emoji} ${r.name} geschafft!`); }
  },
  primary: (el) => {
    const g = goalById(el.dataset.id); if (!g) return;
    const before = isCompleted(g, ui.date);
    const months = primaryAction(g, ui.date); commit({ app: false, months });
    if (!before && isCompleted(g, ui.date)) toast(`${g.emoji} ${g.title}: Ziel erreicht!`);
  },
  'primary-now': (el) => { const g = goalById(el.dataset.id); if (!g) return; commit({ app: false, months: primaryAction(g, new Date()) }); },
  amount: (el) => { const g = goalById(el.dataset.id); if (!g) return; openSheet({ kind: 'amount', goalId: g.id, date: sheetDate(), amount: g.kind === 'count' ? (g.step || 1) : 1, note: '' }); },
  quick: (el) => { ui.sheet.amount = Number(el.dataset.v); renderSheet(); },
  'save-amount': () => {
    const sh = ui.sheet; const g = goalById(sh.goalId); if (!g) return closeSheet();
    const v = g.kind === 'count' ? Number(sh.amount) : 1; if (!(v > 0)) return;
    const note = (sh.note || '').trim();
    const existing = g.kind === 'check' ? entriesOnDay(g, sh.date)[0] : null;
    let mk;
    if (existing) { existing.n = note || existing.n; mk = monthKeyOf(existing.t); } else mk = addEntry(g, sh.date, v, note);
    closeSheet(); commit({ app: false, months: [mk] }); toast(existing ? 'Notiz gespeichert' : 'Eingetragen');
  },
  'del-entry': (el) => {
    const g = goalById(el.dataset.goal); const e = g && goalEntries(g).find((x) => x.id === el.dataset.id); if (!e) return;
    commit({ app: false, months: [removeEntry(e)] }); toast('Eintrag gelöscht');
  },
  'archive-goal': (el) => {
    const g = goalById(el.dataset.id); if (!g) return;
    g.archived = !g.archived; commit(); toast(g.archived ? 'Archiviert' : 'Reaktiviert');
  },
  'delete-goal': (el) => {
    const g = goalById(el.dataset.id); if (!g) return;
    confirmSheet('Ziel löschen?', `„${g.title}“ und alle Einträge werden gelöscht. Das lässt sich nicht rückgängig machen.`, 'Löschen', () => {
      const months = new Set(goalEntries(g).map((e) => monthKeyOf(e.t)));
      for (const mk of months) M[mk].entries = M[mk].entries.filter((e) => e.g !== g.id);
      S.goals = S.goals.filter((x) => x.id !== g.id);
      for (const p of S.journeys) if (p.linkedGoalId === g.id) p.linkedGoalId = null;
      ui.stack = ui.stack.filter((s) => !(s.type === 'goal' && s.id === g.id));
      commit({ months: [...months] }); toast('Gelöscht');
    }, true);
  },
  'confirm-ok': () => { const fn = ui.sheet?.onOk; closeSheet(); fn?.(); },

  'pick-emoji': (el) => { ui.sheet.draft.emoji = el.dataset.v; renderSheet(); },
  'pick-color': (el) => { ui.sheet.draft.color = el.dataset.v; renderSheet(); },
  'pick-theme': (el) => { ui.sheet.draft.theme = el.dataset.v; renderSheet(); },
  set: (el) => {
    const d = ui.sheet.draft; d[el.dataset.k] = el.dataset.v;
    if (d.kind === 'check' && d.freq === 'daily') d.target = 1;
    else if (d.kind === 'check' && d.freq === 'weekly') { const t = Math.round(Number(d.target)); d.target = t >= 2 && t <= 7 ? t : 3; }
    else if (d.kind === 'count' && !(Number(d.target) > 1)) { d.target = 8; d.step = d.step || 1; }
    renderSheet();
  },
  'step-target': (el) => { const d = ui.sheet.draft; d.target = clamp((Number(d.target) || 1) + Number(el.dataset.dir), 1, 7); renderSheet(); },
  tpl: (el) => {
    const t = TEMPLATES[Number(el.dataset.i)]; const d = ui.sheet.draft;
    Object.assign(d, { title: t.title, emoji: t.emoji, color: t.color, kind: t.kind, freq: t.freq, target: t.target, unit: t.unit || '', step: t.step || 1 });
    if (t.duration && d.ritualId) d.duration = t.duration;
    renderSheet();
  },
  'save-goal': () => saveGoal(),
  'ritual-tpl': (el) => { const s = SLOTS[el.dataset.k]; Object.assign(ui.sheet.draft, { name: s.name, emoji: s.emoji, theme: s.theme, time: s.time, slot: el.dataset.k }); renderSheet(); },
  'save-ritual': () => saveRitual(),
  'delete-ritual': (el) => {
    const r = ritualById(el.dataset.id); if (!r) return;
    confirmSheet('Ritual löschen?', `„${r.name}“ wird gelöscht. Die Gewohnheiten darin bleiben als eigene Ziele erhalten.`, 'Löschen', () => {
      for (const g of S.goals) if (g.ritualId === r.id) g.ritualId = null;
      S.rituals = S.rituals.filter((x) => x.id !== r.id);
      ui.stack = ui.stack.filter((s) => !(s.type === 'ritual' && s.id === r.id));
      commit(); toast('Ritual gelöscht');
    }, true);
  },
  'move-habit': (el) => {
    const g = goalById(el.dataset.id); const r = g && ritualById(g.ritualId); if (!r) return;
    const list = ritualHabits(r); const i = list.findIndex((x) => x.id === g.id); const j = i + Number(el.dataset.dir);
    if (j < 0 || j >= list.length) return;
    [list[i], list[j]] = [list[j], list[i]]; list.forEach((x, k) => { x.ritualOrder = k; }); commit();
  },
  'unlink-habit': (el) => { const g = goalById(el.dataset.id); if (!g) return; g.ritualId = null; commit(); toast('Aus dem Ritual entfernt'); },
  'link-existing': (el) => openSheet({ kind: 'link-existing', ritualId: el.dataset.ritual }),
  'do-link': (el) => { const g = goalById(el.dataset.id); const r = ritualById(el.dataset.ritual); if (!g || !r) return; addToRitual(g, r); closeSheet(); commit(); toast(`Zu „${r.name}“ hinzugefügt`); },
  play: (el) => startPlayer(el.dataset.id),
  'player-close': () => closePlayer(),
  'player-toggle': () => {
    const p = ui.player; if (!p || !p.duration || p.remaining === 0) return;
    if (p.running) { p.remaining = Math.max(0, p.endAt - Date.now()); p.running = false; } else { p.endAt = Date.now() + p.remaining; p.running = true; }
    renderPlayer();
  },
  'player-done': () => {
    const p = ui.player; const g = goalById(p.queue[p.i]);
    if (g) { const months = completeForDay(g, new Date()); commit({ app: false, months }); p.done++; }
    chime([660, 880]); playerNext();
  },
  'player-skip': () => playerNext(),

  'start-journey': (el) => {
    const j = journeyById(el.dataset.id); if (!j) return;
    const go = () => { startJourney(j); commit(); toast(`Reise „${j.title}“ gestartet`); };
    if (el.dataset.switch) confirmSheet('Reise wechseln?', 'Deine aktuelle Reise wird pausiert. Du kannst sie später an derselben Stelle fortsetzen.', 'Wechseln', go);
    else go();
  },
  advance: (el) => {
    const j = journeyById(el.dataset.id); const p = journeyProgress(j.id); if (!p) return;
    advanceJourney(p, j); commit();
    if (p.completedAt) { unlockAudio(); chime([523, 659, 784, 1046]); confetti(); toast('Reise abgeschlossen! 🏆'); } else toast('Weiter geht’s');
    window.scrollTo({ top: 0, behavior: reduceMotion() ? 'auto' : 'smooth' });
  },
  'link-blueprint': (el) => {
    const j = journeyById(el.dataset.id); const p = journeyProgress(j.id); const s = j.steps[p.stepIndex];
    const g = addHabitFromBlueprint(s.habit); p.linkedGoalId = g.id; p.stepStartedAt = Date.now(); commit();
    toast(`„${g.title}“ ist jetzt in deinem ${SLOTS[s.habit.slot].name}`);
  },
  'journey-done-today': (el) => { const g = goalById(el.dataset.id); if (!g) return; commit({ app: false, months: completeForDay(g, new Date()) }); },
  'read-step': (el) => { const j = journeyById(el.dataset.j); const s = j?.steps.find((x) => x.id === el.dataset.s); if (s) openSheet({ kind: 'read-step', step: s }); },

  range: (el) => { ui.range = Number(el.dataset.n); renderApp(); },
  'toggle-archived': () => { ui.showArchived = !ui.showArchived; renderApp(); },
  'rerun-onboarding': () => { ui.ob = { step: 0, name: S.profile.name, journey: activeJourney()?.id || 'energy', wake: S.rituals.find((r) => r.slot === 'morning')?.time || '07:00' }; ui.mode = 'onboarding'; renderOnboarding(); },
  'install-help': () => openSheet({ kind: 'install' }),
  export: async () => {
    const text = JSON.stringify({ app: 'fabulous', version: 1, exportedAt: new Date().toISOString(), S, M });
    const filename = `fabulous-backup-${dayKey(new Date())}.json`;
    let saved = false;
    try {
      const dl = window.claude?.use ? await window.claude.use('downloads') : null;
      if (dl) { await dl.save({ filename, data: text }); saved = true; toast('Backup gespeichert'); }
    } catch (e) { saved = false; }
    if (!saved && !window.claude) {
      // Eigenständige Version: Datei teilen (iPhone/iPad) oder herunterladen
      try {
        const file = new File([text], filename, { type: 'application/json' });
        if (navigator.canShare?.({ files: [file] })) { await navigator.share({ files: [file], title: 'Fabulous-Backup' }); saved = true; }
        else {
          const a = document.createElement('a'); a.href = URL.createObjectURL(file); a.download = filename;
          document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); saved = true; toast('Backup heruntergeladen');
        }
      } catch (e) { if (e && e.name === 'AbortError') saved = true; }
    }
    if (!saved) openSheet({ kind: 'export', text });
  },
  'copy-export': async () => {
    const ta = $('#export-text');
    try { await navigator.clipboard.writeText(ta.value); toast('Kopiert'); }
    catch (e) { ta.focus(); ta.select(); toast('Text markiert. Jetzt kopieren.'); }
  },
  'import-text': () => importBackup($('#import-text')?.value || ''),
  'reset-all': () => confirmSheet('Alle Daten löschen?', 'Alle Rituale, Gewohnheiten, Einträge und Reisen werden gelöscht, auch auf deinen anderen Geräten. Das lässt sich nicht rückgängig machen.', 'Alles löschen', () => {
    const months = Object.keys(M);
    for (const k of months) M[k].entries = [];
    S = freshState(); S.profile.createdAt = Date.now();
    ui.stack = []; ui.tab = 'heute'; ui.ob = { step: 0, name: '', journey: 'energy', wake: '07:00' };
    commit({ months, render: false });
    ui.mode = 'onboarding'; renderOnboarding();
  }, true),

  'ob-next': () => {
    const o = ui.ob;
    if (o.step === 1) { const v = $('#ob-name')?.value; if (v != null) o.name = v; }
    if (o.step === 3) { const v = $('#ob-wake')?.value; if (v) o.wake = v; return finishOnboarding(); }
    o.step++; renderOnboarding();
    if (o.step === 1 && !('ontouchstart' in window)) $('#ob-name')?.focus();
  },
  'ob-back': () => { ui.ob.step = Math.max(0, ui.ob.step - 1); renderOnboarding(); },
  'ob-journey': (el) => { ui.ob.journey = el.dataset.id; renderOnboarding(); },
};

function importBackup(text) {
  let data;
  try { data = JSON.parse(text); } catch (e) { return toast('Das ist kein gültiges Backup.'); }
  if (!data || !data.S || !data.S.profile || !Array.isArray(data.S.goals)) return toast('Das ist kein gültiges Fabulous-Backup.');
  confirmSheet('Backup laden?', 'Deine aktuellen Daten werden durch das Backup ersetzt.', 'Laden', () => {
    const oldMonths = Object.keys(M);
    S = normalizeState(data.S); M = normalizeMonths(data.M);
    for (const k of oldMonths) if (!M[k]) M[k] = { updatedAt: 0, entries: [] };
    S.profile.onboarded = true;
    ui.stack = []; ui.mode = 'app';
    commit({ months: Object.keys(M) }); toast('Backup geladen');
  });
}

/* ================= Events ================= */
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-act]');
  if (!el || el.disabled) return;
  const fn = A[el.dataset.act];
  if (fn) { e.preventDefault(); fn(el, e); }
});
document.addEventListener('input', (e) => {
  const el = e.target; const f = el.dataset?.field; if (!f) return;
  const sh = ui.sheet;
  if (f === 'ob-name') { ui.ob.name = el.value; return; }
  if (f === 'ob-wake') { ui.ob.wake = el.value; return; }
  if (f === 'profile-name' || f === 'import' || f === 'import-text') return;
  if (!sh) return;
  if (sh.kind === 'amount') { sh[f] = el.value; const b = $('.sheet-head .r button'); const g = goalById(sh.goalId); if (b && g?.kind === 'count') b.disabled = !(Number(sh.amount) > 0); return; }
  if (!sh.draft) return;
  if (f === 'emoji') { const v = el.value.trim(); if (v) { sh.draft.emoji = firstGrapheme(v); const pv = $('.title-row .preview'); if (pv) pv.textContent = sh.draft.emoji; } return; }
  sh.draft[f] = el.value;
  const b = $('.sheet-head .r button');
  if (b) {
    if (sh.kind === 'goal-editor') { const d = sh.draft; b.disabled = !(d.title.trim() && Number(d.target) > 0 && (d.kind === 'check' || Number(d.step) > 0)); }
    if (sh.kind === 'ritual-editor') b.disabled = !sh.draft.name.trim();
  }
  if (f === 'ritualId') renderSheet();
});
document.addEventListener('change', (e) => {
  const el = e.target; const f = el.dataset?.field;
  if (f === 'profile-name') { const v = el.value.trim().slice(0, 30); if (v !== S.profile.name) { S.profile.name = v; commit(); } }
  if (f === 'import' && el.files?.[0]) { const r = new FileReader(); r.onload = () => importBackup(String(r.result || '')); r.readAsText(el.files[0]); el.value = ''; }
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { if (ui.sheet) closeSheet(); else if (ui.player) closePlayer(); else if (ui.stack.length) pop(); }
  if (e.key === 'Enter' && e.target?.dataset?.field === 'ob-name') { e.preventDefault(); A['ob-next'](); }
  if (e.key === 'Enter' && ui.sheet && e.target?.tagName === 'INPUT') { const b = $('.sheet-head .r button'); if (b && !b.disabled) { e.preventDefault(); b.click(); } }
});
window.addEventListener('hashchange', () => {
  const t = location.hash.slice(1);
  if (ui.mode === 'app' && HASH_TABS.includes(t) && (t !== ui.tab || ui.stack.length)) goTab(t);
});
// Wenn die App lange offen ist und ein neuer Tag beginnt: "Heute" aktualisieren
let lastDay = dayKey(new Date());
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState !== 'visible') return;
  const k = dayKey(new Date());
  if (k !== lastDay) { if (dayKey(ui.date) === lastDay) ui.date = new Date(); lastDay = k; renderApp(); }
  if (ui.player && ui.player.running) tickPlayer();
});
setInterval(() => { const k = dayKey(new Date()); if (k !== lastDay && document.visibilityState === 'visible') { if (dayKey(ui.date) === lastDay) ui.date = new Date(); lastDay = k; renderApp(); } }, 60000);

/* ================= Boot ================= */
function renderBoot() {
  $('#app').innerHTML = `<div class="boot"><div><div class="wordmark">Fabulous</div><div class="spin" aria-label="Lädt"></div></div></div>`;
}
function boot() {
  loadLocal();
  const h = location.hash.slice(1); if (HASH_TABS.includes(h)) ui.tab = h;
  Cloud.init();
  if (S.profile.onboarded) { ui.mode = 'app'; renderApp(); return; }
  renderBoot();
  const decide = () => {
    if (ui.mode !== 'boot') return;
    if (S.profile.onboarded) { ui.mode = 'app'; renderApp(); }
    else { ui.mode = 'onboarding'; renderOnboarding(); }
  };
  Cloud.ready.then(decide);
  setTimeout(decide, 10000);
}
boot();
