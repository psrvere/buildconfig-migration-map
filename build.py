#!/usr/bin/env python3
"""Build index.html from data/*.tsv. Standard library only.

    python3 build.py

Edit data/stories.tsv or data/features.tsv, run this, commit index.html.
The prose sections live in this file under TEMPLATE."""
import csv, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
JIRA = "https://redhat.atlassian.net/browse/"
PLUGIN = "https://github.com/migtools/crane-plugin-buildconfig-to-shipwright"
OPERATOR = "https://github.com/redhat-openshift-builds/operator"
SNAPSHOT = "2026-09-03"


def read(name):
    with open(ROOT / "data" / name, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


features = read("features.tsv")
layers = read("layers.tsv")
stories = read("stories.tsv")
fmap = {f["id"]: f for f in features}

DESCOPED = {"Won't Do", "Obsolete", "Duplicate", "Cannot Reproduce"}


def state(s):
    if s["resolution"] in DESCOPED:
        return "descoped"
    if s["resolution"] == "Done":
        return "done"
    if s["status"] == "Review":
        return "review"
    return "open"


STATE_TAG = {"done": ("ok", "done"), "review": ("warn", "review"),
             "open": ("acc", "open"), "descoped": ("off", "descoped")}
PHASE_NAME = {"TP": "Tech Preview", "P1": "Phase 1", "P2": "Phase 2",
              "P3": "Phase 3", "P4": "Phase 4"}
PHASE_EPIC = {"TP": "BUILD-1334", "P1": "BUILD-1848", "P2": "BUILD-1655",
              "P3": "BUILD-2254", "P4": "BUILD-2394"}

# ---------------------------------------------------------------- sources
SOURCES = [
    ("src-epic-tp", "BUILD-1334, Tech Preview of migration tool (BuildConfig to Builds), Jira epic", JIRA + "BUILD-1334"),
    ("src-epic-p1", "BUILD-1848, Enhancements to Migration Tool: Phase 1, Jira epic", JIRA + "BUILD-1848"),
    ("src-epic-p2", "BUILD-1655, Enhancements to Migration Tool, Phase 2, Jira epic", JIRA + "BUILD-1655"),
    ("src-epic-p3", "BUILD-2254, Migration Tool Enhancement: Phase 3, Jira epic", JIRA + "BUILD-2254"),
    ("src-epic-p4", "BUILD-2394, Enhancement to Migration Tool, Phase 4, Jira epic", JIRA + "BUILD-2394"),
    ("src-readme", "crane-plugin-buildconfig-to-shipwright, README on main", PLUGIN + "/blob/main/README.md"),
    ("src-arch", "PR #64, docs: add the architecture page (docs/architecture.md)", PLUGIN + "/pull/64"),
    ("src-matrix", "PR #65, docs: add the BuildConfig support matrix (docs/support-matrix.md)", PLUGIN + "/pull/65"),
    ("src-converter", "buildconfig/converter.go at b05b610, lines 592 to 599, the three S2I RFE warnings", PLUGIN + "/blob/b05b610/buildconfig/converter.go#L592-L599"),
    ("src-s2i-yaml", "operator config/shipwright/build/strategy/source-to-image.yaml at ea1b42e1, params scripts-url, pull-policy, incremental", OPERATOR + "/blob/ea1b42e1/config/shipwright/build/strategy/source-to-image.yaml"),
    ("src-2323", "BUILD-2323, triage comment of 2026-08-24 on where the strategy params landed", JIRA + "BUILD-2323"),
    ("src-op1402", "operator PR #1402, catalog sync that brought the strategy params into the operator", OPERATOR + "/pull/1402"),
    ("src-2317", "BUILD-2317, validate strategy parameter names, closed Won't Do", JIRA + "BUILD-2317"),
    ("src-2328", "BUILD-2328, shared param-name constants + cross-repo golden test, closed Won't Do", JIRA + "BUILD-2328"),
    ("src-triggers-go", "buildconfig/triggers.go at b05b610, preservation annotation and the per-type warnings", PLUGIN + "/blob/b05b610/buildconfig/triggers.go"),
    ("src-2393", "BUILD-2393, runbook: how to trigger builds after migration", JIRA + "BUILD-2393"),
    ("src-prs", "crane-plugin-buildconfig-to-shipwright, all pull requests", PLUGIN + "/pulls?q=is%3Apr"),
    ("src-pr63", "PR #63, YAML-based E2E test framework (midays)", PLUGIN + "/pull/63"),
    ("src-pr60", "PR #60, basic S2I and Docker cluster E2E build test with InsecureOutputFlag (aufi)", PLUGIN + "/pull/60"),
    ("src-pr17", "PR #17, prepare E2E cluster tests infrastructure (aufi)", PLUGIN + "/pull/17"),
    ("src-pr4", "PR #4, add CI build job (aufi)", PLUGIN + "/pull/4"),
    ("src-2337", "BUILD-2337, dry-run mode, closing comment of 2026-08-17", JIRA + "BUILD-2337"),
    ("src-2038", "BUILD-2038, secret migration support, closing comment of 2026-08-14", JIRA + "BUILD-2038"),
    ("src-pr23", "PR #23, map mountTrustedCA to the trusted-ca volume override", PLUGIN + "/pull/23"),
    ("src-2402", "BUILD-2402, migrate the BuildConfig ServiceAccount and its RBAC", JIRA + "BUILD-2402"),
    ("src-2326", "BUILD-2326, preserve symbolic image refs for chained BuildConfig conversions", JIRA + "BUILD-2326"),
    ("src-2334", "BUILD-2334, crane: consume Shipwright omitempty, Waiting", JIRA + "BUILD-2334"),
    ("src-2315", "BUILD-2315, stop emitting a ServiceAccount that overwrites a migrated one, PR #55 merged", JIRA + "BUILD-2315"),
    ("src-enh", "konveyor/enhancements PR #300, the BuildConfig to Shipwright enhancement proposal", "https://github.com/konveyor/enhancements/pull/300"),
    ("src-crane", "konveyor/crane, the migration CLI the plugin runs under", "https://github.com/konveyor/crane"),
]
SRC_BY_KEY = {k: (title, url) for k, title, url in SOURCES}


def ref(*keys):
    for k in keys:
        assert k in SRC_BY_KEY, k
    return "".join(f"@REF:{k}@" for k in keys)


def number_sources(page):
    """Replace @REF:key@ tokens with numbered superscripts, first use first,
    and return the page plus the sources list in that order."""
    order = []
    for k in re.findall(r"@REF:([a-z0-9-]+)@", page):
        if k not in order:
            order.append(k)
    unused = [k for k in SRC_BY_KEY if k not in order]
    assert not unused, f"sources never cited: {unused}"
    for i, k in enumerate(order, 1):
        page = page.replace(f"@REF:{k}@", f'<a class="ref" href="#src{i}">{i}</a>')
    items = "".join(f'<li id="src{i}"><a href="{e(SRC_BY_KEY[k][1])}">{e(SRC_BY_KEY[k][0])}</a></li>'
                    for i, k in enumerate(order, 1))
    return page, items


def e(s):
    return html.escape(s, quote=True)


def jira(key):
    return f'<a href="{JIRA}{key}">{key}</a>'


def pr_links(prs):
    out = []
    for p in prs.split(","):
        p = p.strip()
        if not p:
            continue
        if p.startswith("op"):
            out.append(f'<a href="{OPERATOR}/pull/{p[2:]}">operator #{p[2:]}</a>')
        else:
            out.append(f'<a href="{PLUGIN}/pull/{p}">#{p}</a>')
    return ", ".join(out)


# ---------------------------------------------------------------- figures
def fig_pipeline():
    boxes = [
        ("BuildConfig", "on the source cluster", ""),
        ("crane export", "namespace to disk", ""),
        ("crane transform", "this plugin, once per object", "acc"),
        ("review", "outcomes and warnings", ""),
        ("crane apply", "to the target cluster", ""),
        ("Shipwright Build", "with SA, ConfigMap, template", ""),
    ]
    w, h, gap, m = 300, 84, 40, 10
    rows_y = [16, 176]
    parts = ['<defs><marker id="fig1-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="var(--muted)"/></marker></defs>']
    for i, (t, sub, cls) in enumerate(boxes):
        row, col = divmod(i, 3)
        x, y = m + col * (w + gap), rows_y[row]
        parts.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>')
        tc = " acc" if cls else ""
        parts.append(f'<text class="t{tc}" x="{x + w/2}" y="{y + 36}" text-anchor="middle" style="font-size:20px">{e(t)}</text>')
        parts.append(f'<text class="s" x="{x + w/2}" y="{y + 62}" text-anchor="middle" style="font-size:15px">{e(sub)}</text>')
        if col < 2:
            parts.append(f'<path d="M{x + w} {y + h/2} H{x + w + gap - 3}" fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#fig1-arr)"/>')
    # wrap from the end of row one to the start of row two
    x3 = m + 2 * (w + gap) + w / 2
    x4 = m + w / 2
    y_channel = rows_y[0] + h + 38
    parts.append(f'<path d="M{x3} {rows_y[0] + h} V{y_channel} H{x4} V{rows_y[1] - 3}" fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#fig1-arr)"/>')
    total_w = 2 * m + 3 * w + 2 * gap
    total_h = rows_y[1] + h + 16
    return f'''<figure>
  <div class="figwrap">
    <svg viewBox="0 0 {total_w} {total_h}" role="img" aria-label="Six stages in two rows: BuildConfig on the source cluster, crane export, crane transform running this plugin, then review, crane apply, and the Shipwright Build with its companion objects.">{"".join(parts)}</svg>
  </div>
  <figcaption><b>Figure 1. Where the plugin sits.</b> crane exports the namespace to disk, the plugin converts each object during transform, and nothing touches the target cluster until apply. The blue box is this plugin. Source: README, "What it does" and "Usage with crane".{ref("src-readme")}</figcaption>
</figure>'''


def fig_layers():
    by_layer = {}
    for f in features:
        by_layer.setdefault(f["layer"], []).append(f)
    per_line, bw, bh, gap, m = 5, 196, 56, 8, 12
    width = 2 * m + per_line * bw + (per_line - 1) * gap
    parts = []
    y = 12
    for i, L in enumerate(layers):
        fs = by_layer.get(L["id"], [])
        parts.append(f'<text class="t" x="{m + 2}" y="{y + 18}" style="font-size:19px">{e(L["id"])}. {e(L["name"])}</text>')
        if L["sub"]:
            parts.append(f'<text class="s" x="{width - m - 2}" y="{y + 18}" text-anchor="end" style="font-size:15px">{e(L["sub"])}</text>')
        by = y + 32
        for j, f in enumerate(fs):
            line, col = divmod(j, per_line)
            x = m + col * (bw + gap)
            yy = by + line * (bh + gap)
            parts.append(f'<rect class="box {f["status_class"]}" x="{x}" y="{yy}" width="{bw}" height="{bh}" rx="5"/>')
            parts.append(f'<text class="t {f["status_class"]}" x="{x + 12}" y="{yy + 24}" style="font-size:18px">{e(f["id"])}</text>')
            parts.append(f'<text class="s" x="{x + 12}" y="{yy + 45}" style="font-size:15px">{e(f["short"])}</text>')
        lines = (len(fs) + per_line - 1) // per_line
        y = by + lines * (bh + gap) - gap + 18
        if i < len(layers) - 1:
            parts.append(f'<line x1="{m}" y1="{y}" x2="{width - m}" y2="{y}" stroke="var(--line)" stroke-width="1"/>')
            y += 18
    height = y + 4
    return f'''<figure>
  <div class="figwrap">
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="Seven layers, each holding its features as boxes coloured by status. Convert holds six features, five shipped and S2I parity a gap. Carry the environment holds credentials and volumes, partly done, and pre-flight checks, descoped. Tell the truth holds outcome and warnings, shipped, and triggers, partly. Safe to re-run is shipped. Prove it is partly done. Explain it is in review. Build it faster holds the engineering workflow, shipped, and upstream alignment, partly.">{"".join(parts)}</svg>
  </div>
  <figcaption><b>Figure 2. The feature map.</b> Fifteen features in seven layers. A layer is a question a reader asks in order: does it convert, does the Build have what it needs on the target, does the tool admit what it lost, can it run twice, is it proven, is it explained, can the team build it fast. Colour is the status on {SNAPSHOT}. I set it from the story map in section 4 and the code on main.{ref("src-epic-p4", "src-readme")}</figcaption>
  <div class="legend">
    <span class="l-ok">shipped on main</span>
    <span class="l-warn">partly shipped or in review</span>
    <span class="l-bad">gap the epics hide</span>
    <span class="l-off">descoped</span>
  </div>
</figure>'''


# ---------------------------------------------------------------- tables
def features_table():
    rows = []
    for f in features:
        items = "".join(f"<li>{e(t.strip())}</li>" for t in f["outcome"].split("|") if t.strip())
        rows.append(f'<tr><td class="k">{e(f["id"])} {e(f["name"])}</td><td><ul class="cell">{items}</ul></td>'
                    f'<td><span class="tag {f["status_class"]}">{e(f["status_text"])}</span></td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>Feature</th><th>What the user gets</th><th>Status</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def phase_table():
    counts = {}
    for s in stories:
        c = counts.setdefault(s["phase"], {"n": 0, "done": 0, "descoped": 0, "review": 0, "open": 0})
        c["n"] += 1
        c[state(s)] += 1
    meta = {
        "TP": ("Closed 2026-03-21", "crane convert proof of concept: Docker and S2I strategies, BuildSource types, a trigger spike, a demo", "src-epic-tp"),
        "P1": ("Closed 2026-07-21", "Buildah params in the operator, no-cache and runtime-stage-from, plus the S2I registry pull secret and output to the internal registry. It targeted builds-1.8 and the team pulled it out of the 1.9.0 release in May 2026", "src-epic-p1"),
        "P2": ("Closed 2026-09-02", "The RFE catch-all: buildah and S2I flags, secrets, ConfigMaps and volumes, source examples, idempotency, naming, the upstream omitempty change", "src-epic-p2"),
        "P3": ("Closed 2026-09-02", "Production readiness from the gap analysis: full field coverage, five code bugs, the outcome model, per-field warnings", "src-epic-p3"),
        "P4": ("Open", "Documentation and runbooks, the engineering skills, and the engineering that is left: SA and RBAC, trusted CA, chained builds, omitempty", "src-epic-p4"),
    }
    rows = []
    for p in ["TP", "P1", "P2", "P3", "P4"]:
        c = counts[p]
        st, what, src = meta[p]
        detail = f'{c["n"]} stories: {c["done"]} done'
        if c["descoped"]:
            detail += f', {c["descoped"]} descoped'
        if c["review"]:
            detail += f', {c["review"]} in review'
        if c["open"]:
            detail += f', {c["open"]} not started'
        rows.append(f'<tr><td class="k">{PHASE_NAME[p]}</td><td>{jira(PHASE_EPIC[p])}</td><td>{st}</td><td>{detail}</td><td>{e(what)}{ref(src)}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>Phase</th><th>Epic</th><th>State</th><th>Stories</th><th>What it delivered</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def story_table():
    rows = []
    for s in stories:
        st = state(s)
        cls, label = STATE_TAG[st]
        if s["gap"] == "1":
            cls, label = "bad", "done in Jira, gap in plugin"
        detail = []
        if s["resolution"] and s["resolution"] != "Done":
            detail.append(e(s["resolution"]))
        if st == "open":
            detail.append(e(s["status"]))
        if s["prs"]:
            detail.append(pr_links(s["prs"]))
        line = f'<span class="tag {cls}">{label}</span>'
        if detail:
            line += " " + " · ".join(detail)
        if s["note"]:
            line += f'<div class="src">{e(s["note"])}</div>'
        f = fmap[s["feature"]]
        rows.append(
            f'<tr data-phase="{s["phase"]}" data-feature="{s["feature"]}" data-type="{s["type"]}" data-state="{st}">'
            f'<td class="k">{e(f["id"])} {e(f["short"])}</td><td>{PHASE_NAME[s["phase"]][0] + PHASE_NAME[s["phase"]].split()[-1] if s["phase"] != "TP" else "TP"}</td>'
            f'<td class="k">{jira(s["key"])}</td><td>{e(s["title"])}</td><td>{e(s["type"])}</td><td>{line}</td></tr>')
    return ('<div class="tablewrap compact" id="stories"><table><thead><tr><th>Feature</th><th>Phase</th><th>Story</th><th>Title</th><th>Type</th><th>Status</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def filter_bar():
    def opts(values, labels=None):
        return "".join(f'<option value="{e(v)}">{e(labels[v] if labels else v)}</option>' for v in values)
    phases = ["TP", "P1", "P2", "P3", "P4"]
    types = sorted({s["type"] for s in stories})
    states = ["done", "review", "open", "descoped"]
    return f'''<div class="filters" role="group" aria-label="Filter the story map">
  <label>Phase <select id="f-phase" data-key="phase"><option value="">all</option>{opts(phases, PHASE_NAME)}</select></label>
  <label>Feature <select id="f-feature" data-key="feature"><option value="">all</option>{opts([f["id"] for f in features], {f["id"]: f["id"] + " " + f["short"] for f in features})}</select></label>
  <label>Type <select id="f-type" data-key="type"><option value="">all</option>{opts(types)}</select></label>
  <label>State <select id="f-state" data-key="state"><option value="">all</option>{opts(states)}</select></label>
  <button type="button" id="f-reset">reset</button>
  <span id="f-count" class="muted"></span>
</div>'''


def tally_table():
    rows = []
    for f in features:
        ss = [s for s in stories if s["feature"] == f["id"] and s["phase"] != "TP"]
        c = {"done": 0, "descoped": 0, "review": 0, "open": 0}
        for s in ss:
            c[state(s)] += 1
        rows.append(f'<tr><td class="k">{e(f["id"])} {e(f["short"])}</td><td class="num">{len(ss)}</td><td class="num">{c["done"]}</td>'
                    f'<td class="num">{c["descoped"]}</td><td class="num">{c["review"]}</td><td class="num">{c["open"]}</td></tr>')
    return ('<div class="tablewrap compact"><table><thead><tr><th>Feature</th><th class="num">Stories</th><th class="num">Done</th><th class="num">Descoped</th><th class="num">In review</th><th class="num">Not started</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


# ---------------------------------------------------------------- numbers
n_all = len(stories)
n_done = sum(1 for s in stories if state(s) == "done")
n_desc = sum(1 for s in stories if state(s) == "descoped")
n_rev = sum(1 for s in stories if state(s) == "review")
n_open = sum(1 for s in stories if state(s) == "open")
n_enh = sum(1 for s in stories if s["phase"] != "TP")

EXTRA_CSS = """
/* page-local additions, tokens only */
.filters { display: flex; flex-wrap: wrap; gap: 0.6rem 1rem; align-items: center; margin: 1rem 0 0.4rem; font-size: 0.86rem; color: var(--muted); }
.filters select, .filters button { font: inherit; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 3px; padding: 0.25rem 0.5rem; margin-left: 0.3rem; }
.filters button { cursor: pointer; }
.filters button:hover { border-color: var(--accent); }
#stories table td:nth-child(4) { min-width: 26ch; }
tr[hidden] { display: none; }
ul.cell { margin: 0; padding-left: 1.1rem; max-width: none; }
ul.cell li { margin: 0.15rem 0; }
.hero .note { margin-top: 1rem; }
"""

JS = """
(function () {
  var sel = ['phase', 'feature', 'type', 'state'].map(function (k) { return document.getElementById('f-' + k); });
  var rows = Array.prototype.slice.call(document.querySelectorAll('#stories tbody tr'));
  var count = document.getElementById('f-count');
  function apply() {
    var n = 0;
    rows.forEach(function (r) {
      var show = sel.every(function (s) { return !s.value || r.getAttribute('data-' + s.getAttribute('data-key')) === s.value; });
      r.hidden = !show;
      if (show) n += 1;
    });
    count.textContent = n + ' of ' + rows.length + ' stories';
  }
  sel.forEach(function (s) { s.addEventListener('change', apply); });
  document.getElementById('f-reset').addEventListener('click', function () { sel.forEach(function (s) { s.value = ''; }); apply(); });
  apply();
})();
"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BuildConfig to Shipwright migration map</title>
<meta name="description" content="What the BuildConfig to Shipwright migration plugin does today, which features each phase delivered, what is open, and the gaps the Jira epics hide.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>@@BASE_CSS@@@@EXTRA_CSS@@</style>
</head>
<body>
<div class="layout">
<nav class="toc" aria-label="Contents">
  <div class="eyebrow">Contents</div>
  <ol>
    <li><a href="#goal"><span class="n">-</span>Goal</a></li>
    <li><a href="#summary"><span class="n">-</span>In short</a></li>
    <li><a href="#s1"><span class="n">1</span>What the tool does</a></li>
    <li><a href="#s2"><span class="n">2</span>The feature map</a></li>
    <li><a href="#s3"><span class="n">3</span>Phases</a></li>
    <li><a href="#s4"><span class="n">4</span>Story map</a></li>
    <li><a href="#s5"><span class="n">5</span>Work outside Jira</a></li>
    <li><a href="#s6"><span class="n">6</span>Gaps the epic view hides</a></li>
    <li><a href="#s7"><span class="n">7</span>What is open</a></li>
    <li><a href="#sources"><span class="n">S</span>Sources</a></li>
  </ol>
</nav>

<main>
<header class="hero">
  <div class="eyebrow">BuildConfig to Shipwright migration . status page . @@SNAPSHOT@@</div>
  <h1>BuildConfig to Shipwright migration map</h1>
  <p class="lede">What the crane migration plugin does today, which features each phase delivered, what is still open, and the gaps the Jira epics hide.</p>
  <div class="facts">
    <div class="fact"><div class="v">15</div><div class="k">features in 7 layers</div></div>
    <div class="fact"><div class="v">@@N_ALL@@</div><div class="k">stories in 5 epics</div></div>
    <div class="fact"><div class="v">@@N_DONE@@</div><div class="k">done</div></div>
    <div class="fact"><div class="v">@@N_OPENALL@@</div><div class="k">open, @@N_REV@@ of them in review</div></div>
  </div>
  <p class="note">Jira and GitHub as of @@SNAPSHOT@@. The feature ids, the layers and the story types are mine, not Jira fields. <code>build.py</code> generates this page from <code>data/*.tsv</code>.</p>
</header>

<section id="goal">
  <div class="answer">
    <div class="eyebrow">Goal</div>
    <p>Two readers. A product manager or teammate who wants to know what the BuildConfig to Shipwright migration tool can do today and what it still cannot, without opening Jira. And me, planning Phase 4 from the same list, so the two views cannot drift apart.</p>
  </div>
</section>

<section id="summary">
  <h2>In short</h2>
  <p>The tool is a crane transform plugin. It reads a namespace export from disk and turns every BuildConfig into a Shipwright Build, offline, with each dropped field recorded on the object.@@R_README@@ Four of its seven layers are shipped in full: convert, tell the truth, safe to re-run, and build it faster. Carry the environment and prove it are partly done. Explain it is seven open pull requests plus four stories nobody has started.@@R_PRS@@</p>
  <p>The five epics hold @@N_ALL@@ stories. @@N_DONE@@ are done. We closed @@N_DESC@@ without building them, and @@N_OPENALL@@ are open, @@N_REV@@ of those in review.@@R_EPICS@@</p>
  <div class="callout">
    <p>Four things the epic view hides. Three S2I options are Done in Jira, and the plugin still drops them. That one bites a customer with custom S2I scripts on day one. Nothing guards the parameter contract between the plugin and the operator. The plugin preserves triggers but cannot migrate them. And the test infrastructure has no Jira footprint at all.</p>
  </div>
  <p>What is left to build sits in one layer. The ServiceAccount and its RBAC, the trusted CA volume, and chained builds are the engineering stories left. Everything else open is documentation.@@R_P4@@</p>
</section>

<section id="s1">
  <h2>1. What the tool does</h2>
  <p>crane exports a namespace from the source cluster to disk.@@R_CRANE@@ The plugin runs once per exported object. For each BuildConfig it marks the original for deletion and emits a Shipwright Build, plus a ServiceAccount, a ConfigMap or a BuildRun template when the BuildConfig needs one.@@R_README@@ It never contacts a cluster. ImageStream references resolve through two mapping flags. When no flag matches, the plugin falls back to the internal registry URL and says so in a warning.@@R_README@@</p>
  @@FIG1@@
  <p>Every field the plugin drops or changes lands as a warning in an annotation on the Build. Each BuildConfig ends in one of four recorded outcomes: converted, converted with warnings, skipped, or failed. The plugin skips Custom and JenkinsPipeline strategies and records why. One BuildConfig that cannot convert never aborts the run.@@R_ARCH@@ The enhancement proposal that started this work described a different shape, a live <code>crane convert</code> against the cluster. The offline plugin replaced it.@@R_ENH@@</p>
</section>

<section id="s2">
  <h2>2. The feature map</h2>
  <p>Fifteen features, grouped into seven layers. The layers are the questions a reader asks in order, and the colour is where each feature stands today.</p>
  @@FIG2@@
  @@FEATURES@@
</section>

<section id="s3">
  <h2>3. Phases</h2>
  <p>Phases 1 to 3 are closed. Phase 4 holds the documentation series, the engineering skills, and the engineering that is left.@@R_P4@@ The Tech Preview epic predates the phases and built the proof of concept inside crane-lib.@@R_TP@@</p>
  @@PHASES@@
</section>

<section id="s4">
  <h2>4. Story map</h2>
  <p>Every story in the five epics, with the feature it serves. Type is my classification. Status is the Jira status on @@SNAPSHOT@@, the resolution for a closed story, and the pull request where one exists.@@R_EPICS@@</p>
  @@FILTERS@@
  @@STORIES@@
  <h3>Stories per feature</h3>
  <p>The four enhancement epics only, @@N_ENH@@ stories. I left the Tech Preview stories out because they predate the feature split.</p>
  @@TALLY@@
</section>

<section id="s5">
  <h2>5. Work outside Jira</h2>
  <p>Some of the work that matters most for a merge decision has no story. It arrived as pull requests from the crane maintainers and a contributor.@@R_PRS@@</p>
  <div class="tablewrap">
    <table>
      <thead><tr><th>Feature</th><th>Pull requests</th><th>Author</th><th>State</th></tr></thead>
      <tbody>
        <tr><td class="k">F1 Conversion engine</td><td><a href="@@PLUGIN@@/pull/1">#1</a> import the converted conversion from crane</td><td>aufi</td><td><span class="tag ok">merged</span> the seed of the plugin repo</td></tr>
        <tr><td class="k">F10 Tests and CI</td><td><a href="@@PLUGIN@@/pull/4">#4</a> CI build job, <a href="@@PLUGIN@@/pull/17">#17</a> cluster E2E infrastructure, <a href="@@PLUGIN@@/pull/60">#60</a> S2I and Docker cluster E2E with insecure output</td><td>aufi</td><td><span class="tag ok">merged</span>@@R_PR4@@@@R_PR17@@@@R_PR60@@</td></tr>
        <tr><td class="k">F10 Tests and CI</td><td><a href="@@PLUGIN@@/pull/63">#63</a> YAML-based E2E test framework, 18 real-world BuildConfigs, 7 of 18 passing</td><td>midays</td><td><span class="tag warn">open</span>@@R_PR63@@</td></tr>
        <tr><td class="k">F14 Upstream alignment</td><td><a href="@@PLUGIN@@/pull/5">#5</a> x/net bump, <a href="@@PLUGIN@@/pull/62">#62</a> downgrade Go to 1.25</td><td>dependabot, aufi</td><td><span class="tag ok">merged</span></td></tr>
        <tr><td class="k">F12 Engineering workflow</td><td><a href="@@PLUGIN@@/pull/34">#34</a> skills README, <a href="@@PLUGIN@@/pull/71">#71</a> agent doc rules, and the skill chores #39, #40, #42 to #45, #48, #49, #52, #53</td><td>psrvere</td><td><span class="tag warn">#34 and #71 open</span>, the rest merged</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section id="s6">
  <h2>6. Gaps the epic view hides</h2>
  <ol>
    <li><b>Three S2I options are Done in Jira and dropped by the plugin.</b> BUILD-1606, 1607 and 1641 shipped their params, <code>pull-policy</code>, <code>incremental</code> and <code>scripts-url</code>, through strategy-catalog and the operator sync.@@R_2323@@@@R_OP1402@@@@R_S2I@@ The plugin repo started from a snapshot taken before the matching converter change, so it still drops all three with an RFE warning.@@R_CONV@@ Nobody has filed the re-port story under F4.</li>
    <li><b>The parameter contract has no automated guard.</b> The plugin emits param names the shipped strategies must declare. We closed both the validation story and the cross-repo golden test as Won't Do, so cluster E2E and review are the only check.@@R_2317@@@@R_2328@@</li>
    <li><b>Triggers are preserved, never migrated.</b> The plugin keeps the original triggers in an annotation and warns per type, and no trigger type fires after migration because nothing on a Builds for Red Hat OpenShift cluster reads them.@@R_TRIG@@ Nobody has written the runbook that tells a user how to fire builds again.@@R_2393@@</li>
    <li><b>Test infrastructure has no Jira footprint.</b> CI, the transform E2E and the Minikube cluster E2E came through pull requests. The one Jira story in this area, the CI merge gate, we closed as Won't Do.@@R_PR4@@@@R_PR63@@</li>
    <li><b>Three stories closed without code, on purpose.</b> We dropped dry-run because the transform step never touches a cluster.@@R_2337@@ We dropped secret migration because crane export already carries user secrets.@@R_2038@@ The destination pre-flight check went out with the offline design.</li>
  </ol>
</section>

<section id="s7">
  <h2>7. What is open</h2>
  <h3>Engineering</h3>
  <ul>
    <li>@@J2402@@ migrate the ServiceAccount and its RBAC, not just warn. Not started.@@R_2402@@</li>
    <li>@@J2265@@ mountTrustedCA to the trusted-ca volume override, PR #23 in review, paired with @@J2342@@ for the operator and strategy-catalog side.@@R_PR23@@</li>
    <li>@@J2326@@ symbolic image references and run ordering for chained BuildConfigs. Not started.@@R_2326@@</li>
    <li>@@J2334@@ crane consumes the Shipwright omitempty change. Waiting on Shipwright v0.21.0.@@R_2334@@</li>
    <li>The S2I re-port from gap 1 above. No story yet.</li>
    <li>@@J2438@@ and @@J2439@@, two small cleanups in the warnings.</li>
  </ul>
  <h3>Documentation</h3>
  <ul>
    <li>Seven pull requests in review: the architecture page in #64, the support matrix in #65, three worked examples in #66 to #68, the README rewrite in #69, the decision records in #70.@@R_ARCH@@@@R_MATRIX@@</li>
    <li>@@J2341@@ docs pack, @@J2393@@ trigger runbook, @@J1764@@ crane help text. Not started.</li>
    <li>@@J1950@@ blog post on RHEL entitled builds. Backlog.</li>
  </ul>
  <h3>Housekeeping</h3>
  <ul>
    <li>@@J2315@@ shows Review in Jira, but PR #55 merged on 2026-08-25. Close it.@@R_2315@@</li>
    <li>PR #63 needs a decision on whether the YAML framework replaces or sits beside the shell E2E scripts.@@R_PR63@@</li>
  </ul>
</section>

<section id="sources">
  <h2>Sources</h2>
  <ol class="sources">@@SOURCES@@</ol>
</section>
</main>
</div>
<script>@@JS@@</script>
</body>
</html>
"""

base_css = (ROOT / "assets" / "base.css").read_text()
page = (TEMPLATE
        .replace("@@BASE_CSS@@", base_css).replace("@@EXTRA_CSS@@", EXTRA_CSS)
        .replace("@@JS@@", JS)
        .replace("@@SNAPSHOT@@", SNAPSHOT).replace("@@PLUGIN@@", PLUGIN)
        .replace("@@N_ALL@@", str(n_all)).replace("@@N_DONE@@", str(n_done))
        .replace("@@N_DESC@@", str(n_desc)).replace("@@N_REV@@", str(n_rev))
        .replace("@@N_OPENALL@@", str(n_rev + n_open)).replace("@@N_ENH@@", str(n_enh))
        .replace("@@FIG1@@", fig_pipeline()).replace("@@FIG2@@", fig_layers())
        .replace("@@FEATURES@@", features_table()).replace("@@PHASES@@", phase_table())
        .replace("@@FILTERS@@", filter_bar()).replace("@@STORIES@@", story_table())
        .replace("@@TALLY@@", tally_table())
        .replace("@@R_README@@", ref("src-readme")).replace("@@R_PRS@@", ref("src-prs"))
        .replace("@@R_EPICS@@", ref("src-epic-tp", "src-epic-p1", "src-epic-p2", "src-epic-p3", "src-epic-p4"))
        .replace("@@R_P4@@", ref("src-epic-p4")).replace("@@R_TP@@", ref("src-epic-tp"))
        .replace("@@R_CRANE@@", ref("src-crane")).replace("@@R_ARCH@@", ref("src-arch"))
        .replace("@@R_MATRIX@@", ref("src-matrix")).replace("@@R_ENH@@", ref("src-enh"))
        .replace("@@R_2323@@", ref("src-2323")).replace("@@R_OP1402@@", ref("src-op1402"))
        .replace("@@R_S2I@@", ref("src-s2i-yaml")).replace("@@R_CONV@@", ref("src-converter"))
        .replace("@@R_2317@@", ref("src-2317")).replace("@@R_2328@@", ref("src-2328"))
        .replace("@@R_TRIG@@", ref("src-triggers-go")).replace("@@R_2393@@", ref("src-2393"))
        .replace("@@R_PR4@@", ref("src-pr4")).replace("@@R_PR17@@", ref("src-pr17"))
        .replace("@@R_PR60@@", ref("src-pr60")).replace("@@R_PR63@@", ref("src-pr63"))
        .replace("@@R_2337@@", ref("src-2337")).replace("@@R_2038@@", ref("src-2038"))
        .replace("@@R_PR23@@", ref("src-pr23")).replace("@@R_2402@@", ref("src-2402"))
        .replace("@@R_2326@@", ref("src-2326")).replace("@@R_2334@@", ref("src-2334"))
        .replace("@@R_2315@@", ref("src-2315")))
for key in ["2402", "2265", "2342", "2326", "2334", "2438", "2439", "2341", "2393", "1764", "1950", "2315"]:
    page = page.replace(f"@@J{key}@@", jira(f"BUILD-{key}"))

page, items = number_sources(page)
page = page.replace("@@SOURCES@@", items)
leftover = [l for l in page.split("\n") if "@@" in l or "@REF:" in l]
assert not leftover, leftover[:3]
(ROOT / "index.html").write_text(page)
print(f"index.html {len(page):,} bytes; stories={n_all} done={n_done} descoped={n_desc} review={n_rev} open={n_open}")
