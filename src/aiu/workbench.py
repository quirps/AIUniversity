from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

import yaml

from aiu.checkpoint import grade, load_module, write_result
from aiu.clients.deepseek import DeepSeekClient, api_key_from_env
from aiu.config import ConfigError
from aiu.models import Message, PlannedCall

SHELL_MODEL = "deepseek-flash"
MAX_SHELL_MESSAGES = 20
MAX_MESSAGE_CHARS = 4000
MAX_CONTEXT_CHARS = 12000

CSS = """
:root {
  --bg: #10151d;
  --panel: #17202b;
  --panel-2: #1e2a38;
  --text: #e8eef6;
  --muted: #9fb0c4;
  --accent: #79c0ff;
  --ok: #7ee787;
  --warn: #f2cc60;
  --bad: #ff7b72;
  --line: #2b3a4c;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.5 "Segoe UI", system-ui, sans-serif;
}
header {
  padding: 28px clamp(16px, 4vw, 56px);
  border-bottom: 1px solid var(--line);
  background: linear-gradient(135deg, #162233, #10151d 60%);
}
h1, h2, h3 { line-height: 1.2; }
h1 { margin: 0 0 6px; font-size: clamp(24px, 3vw, 38px); }
h2 { margin: 34px 0 12px; font-size: 22px; }
h3 { margin: 0 0 8px; font-size: 18px; }
main { max-width: 1180px; margin: 0 auto; padding: 0 clamp(16px, 4vw, 56px) 80px; }
.muted { color: var(--muted); }
.pill {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--accent);
  font-size: 12px;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.card, .lab, .trust, .panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
}
.card p, .lab p { margin: 8px 0; }
details { margin-top: 10px; }
summary { cursor: pointer; color: var(--accent); }
pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #0c1118;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px;
  max-height: 420px;
  overflow: auto;
  font-size: 13px;
}
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { border-bottom: 1px solid var(--line); padding: 8px 6px; text-align: left; vertical-align: top; }
th { color: var(--muted); font-weight: 600; }
code { color: #d2a8ff; }
input, select, textarea, button {
  font: inherit;
  color: var(--text);
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 9px 11px;
}
button { cursor: pointer; color: #07111d; background: var(--accent); border: 0; font-weight: 700; }
button:disabled { opacity: .55; cursor: wait; }
.field { display: grid; gap: 6px; margin: 10px 0; }
.shell-log {
  min-height: 180px;
  max-height: 420px;
  overflow: auto;
  display: grid;
  gap: 10px;
  margin: 12px 0;
}
.msg { padding: 10px 12px; border-radius: 10px; max-width: 88%; white-space: pre-wrap; }
.msg.user { justify-self: end; background: #233b55; }
.msg.assistant { justify-self: start; background: #1b2633; border: 1px solid var(--line); }
.msg.error { justify-self: start; background: #3a1d1f; border: 1px solid var(--bad); }
.status { font-size: 13px; color: var(--muted); }
.ok { color: var(--ok); }
.bad { color: var(--bad); }
.warn { color: var(--warn); }
.split { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
"""

JS = """
const shellState = { messages: [] };

function addBubble(role, text) {
  const log = document.getElementById('shell-log');
  const el = document.createElement('div');
  el.className = 'msg ' + role;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

async function sendShell(event) {
  event.preventDefault();
  const input = document.getElementById('shell-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  shellState.messages.push({ role: 'user', content: text });
  addBubble('user', text);
  const pending = addBubble('assistant', 'Thinking...');
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: shellState.messages })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    pending.textContent = data.reply || '(empty reply)';
    shellState.messages.push({ role: 'assistant', content: data.reply || '' });
  } catch (error) {
    pending.className = 'msg error';
    pending.textContent = error.message;
  }
}

async function submitCheckpoint(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = new FormData(form);
  const answers = {};
  data.forEach((value, key) => { answers[key] = value; });
  const output = document.getElementById('checkpoint-result');
  output.textContent = 'Grading...';
  output.className = 'status';
  try {
    const response = await fetch('/api/checkpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Grading failed');
    output.className = 'status ' + (result.correct === result.total ? 'ok' : 'warn');
    output.textContent = 'Checkpoint: ' + result.correct + '/' + result.total;
    for (const [id, item] of Object.entries(result.items)) {
      const row = document.createElement('div');
      row.className = 'status ' + (item.correct ? 'ok' : 'bad');
      row.textContent = id + ': ' + (item.correct ? 'correct' : 'not yet');
      output.appendChild(row);
    }
  } catch (error) {
    output.className = 'status bad';
    output.textContent = error.message;
  }
}
"""


def _read_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"not a mapping: {path.as_posix()}")
    return data


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _card(root: Path, card_id: str) -> dict:
    path = root / "curriculum" / card_id[0] / f"{card_id}.yaml"
    if not path.is_file():
        return {"id": card_id, "title": card_id, "missing": True}
    return _read_yaml(path)


def _latest_run(root: Path, lab_id: str) -> Path | None:
    base = root / "experiments" / lab_id
    if not base.is_dir():
        return None
    runs = [
        path
        for path in base.iterdir()
        if path.is_dir() and (path / "cost.json").is_file()
    ]
    return max(runs, key=lambda path: path.name) if runs else None


def _run_view(root: Path, lab_id: str) -> dict:
    manifest_path = root / "labs" / lab_id / "manifest.yaml"
    manifest = _read_yaml(manifest_path) if manifest_path.is_file() else {}
    run = _latest_run(root, lab_id)
    view = {
        "lab_id": lab_id,
        "title": manifest.get("title", lab_id),
        "status": manifest.get("status", "unknown"),
        "hypothesis": manifest.get("hypothesis", ""),
        "run": None,
    }
    if run is None:
        return view
    view["run"] = {
        "dir": run,
        "run_id": run.name,
        "prediction": _read_text(run / "prediction.md"),
        "postmortem": _read_text(run / "postmortem.md"),
        "metrics": _read_json(run / "metrics.json") or {},
        "cost": _read_json(run / "cost.json") or {},
        "result": _read_json(run / "result.json") or {},
    }
    return view


def _trust_rows(root: Path, card_ids: set[str]) -> list[dict]:
    path = root / "learner" / "trust_table.yaml"
    if not path.is_file():
        return []
    data = _read_yaml(path)
    rows = data.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [
        row
        for row in rows
        if isinstance(row, dict) and row.get("card_id") in card_ids
    ]


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _metric_rows(metrics: dict) -> str:
    rows = []
    for name in sorted(metrics):
        value = metrics[name]
        if isinstance(value, float):
            shown = f"{value:.4f}"
        else:
            shown = str(value)
        rows.append(f"<tr><td><code>{_esc(name)}</code></td><td>{_esc(shown)}</td></tr>")
    return "".join(rows)


def _card_html(card: dict) -> str:
    if card.get("missing"):
        return f"<article class=\"card\"><h3>{_esc(card['id'])}</h3><p class=\"bad\">Card file missing.</p></article>"
    fails = "".join(f"<li>{_esc(item)}</li>" for item in card.get("when_it_fails", []))
    misconceptions = "".join(
        f"<li>{_esc(item)}</li>" for item in card.get("misconceptions", [])
    )
    questions = "".join(
        f"<li><strong>{_esc(item.get('q', ''))}</strong><br>{_esc(item.get('a', ''))}</li>"
        for item in card.get("retrieval_questions", [])
    )
    return (
        "<article class=\"card\">"
        f"<h3><span class=\"pill\">{_esc(card['id'])}</span> {_esc(card.get('title', ''))}</h3>"
        f"<p class=\"muted\">{_esc(card.get('one_liner', ''))}</p>"
        f"<p><strong>Why it matters.</strong> {_esc(card.get('why_it_matters', ''))}</p>"
        f"<p><strong>Decision rule.</strong> {_esc(card.get('decision_rule', ''))}</p>"
        f"<details><summary>When it fails</summary><ul>{fails}</ul></details>"
        f"<details><summary>Misconceptions</summary><ul>{misconceptions}</ul></details>"
        f"<details><summary>Retrieval questions</summary><ul>{questions}</ul></details>"
        "</article>"
    )


def _lab_html(view: dict) -> str:
    run = view.get("run")
    if run is None:
        return (
            "<article class=\"lab\">"
            f"<h3><span class=\"pill\">{_esc(view['lab_id'])}</span> {_esc(view['title'])}</h3>"
            f"<p class=\"muted\">Status: {_esc(view['status'])}. No live run yet.</p>"
            f"<p>{_esc(view.get('hypothesis', ''))}</p>"
            "</article>"
        )
    result = run["result"]
    cost = run["cost"]
    metrics = run["metrics"].get("metrics", {}) if isinstance(run["metrics"], dict) else {}
    status = result.get("status", "unknown")
    supported = result.get("hypothesis_supported")
    validity = result.get("validity_passed")
    evidence = result.get("evidence_class", "unknown")
    actual = cost.get("actual_usd", 0.0)
    cap = cost.get("cap_usd", 0.0)
    return (
        "<article class=\"lab\">"
        f"<h3><span class=\"pill\">{_esc(view['lab_id'])}</span> {_esc(view['title'])}</h3>"
        f"<p class=\"muted\">Status: {_esc(status)} | evidence: {_esc(evidence)} | "
        f"hypothesis supported: {_esc(supported)} | validity: {_esc(validity)}</p>"
        f"<p class=\"muted\">Run <code>{_esc(run['run_id'])}</code> | "
        f"actual ${_esc(f'{float(actual):.4f}')} of ${_esc(f'{float(cap):.2f}')} cap</p>"
        f"<p>{_esc(view.get('hypothesis', ''))}</p>"
        f"<details><summary>Metrics</summary><table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>{_metric_rows(metrics)}</tbody></table></details>"
        f"<details><summary>Prediction</summary><pre>{_esc(run['prediction'])}</pre></details>"
        f"<details><summary>Post-mortem</summary><pre>{_esc(run['postmortem'])}</pre></details>"
        "</article>"
    )


def _trust_html(rows: list[dict]) -> str:
    if not rows:
        return "<p class=\"muted\">No trust rows for this module's cards yet.</p>"
    body = "".join(
        "<tr>"
        f"<td>{_esc(row.get('rule', ''))}</td>"
        f"<td>{_esc(row.get('card_id', ''))}</td>"
        f"<td>{_esc(row.get('evidence_strength', ''))}</td>"
        f"<td>{_esc(row.get('my_replication', ''))}</td>"
        f"<td>{_esc(', '.join(row.get('run_ids', [])))}</td>"
        f"<td>{_esc(row.get('notes', ''))}</td>"
        "</tr>"
        for row in rows
    )
    return (
        "<table><thead><tr><th>Rule</th><th>Card</th><th>Evidence</th>"
        "<th>Replication</th><th>Runs</th><th>Notes</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _checkpoint_html(module: dict) -> str:
    items = module.get("checkpoint", {}).get("deterministic_items", [])
    fields = []
    for item in items:
        item_id = item["id"]
        prompt = _esc(item.get("prompt", ""))
        if item.get("type") == "mcq":
            choices = "".join(
                f"<option value=\"{_esc(choice)}\">{_esc(choice)}</option>"
                for choice in item.get("choices", [])
            )
            control = f"<select name=\"{_esc(item_id)}\">{choices}</select>"
        else:
            control = f"<input name=\"{_esc(item_id)}\" autocomplete=\"off\" />"
        fields.append(
            f"<div class=\"field\"><label for=\"{_esc(item_id)}\">{_esc(item_id)}. {prompt}</label>{control}</div>"
        )
    return (
        "<form onsubmit=\"submitCheckpoint(event)\">"
        + "".join(fields)
        + "<button type=\"submit\">Grade checkpoint</button>"
        + "</form><div id=\"checkpoint-result\" class=\"status\"></div>"
    )


def build_system_prompt(root: Path, module_id: str) -> str:
    module = load_module(root, module_id)
    cards = [_card(root, card_id) for card_id in module.get("card_ids", [])]
    lines = [
        f"You are the lesson-scoped tutor for {module.get('id')}: {module.get('title')}.",
        f"Module objective: {module.get('objective')}",
        "Stay inside this lesson. Do not claim to run labs, edit files, or access the host.",
        "If the learner asks for an action outside the lesson, say it is out of scope and point to the CLI.",
        "Use the card summaries below as the authoritative lesson context.",
        "",
        "Cards:",
    ]
    for card in cards:
        if card.get("missing"):
            continue
        lines.append(
            f"- {card.get('id')} {card.get('title')}: {card.get('one_liner')} "
            f"Decision rule: {card.get('decision_rule')}"
        )
    labs = module.get("lab_ids", [])
    if labs:
        lines.append("")
        lines.append("Labs:")
        for lab_id in labs:
            view = _run_view(root, lab_id)
            run = view.get("run")
            if run is None:
                lines.append(f"- {lab_id} {view['title']}: no live run yet.")
                continue
            result = run["result"]
            cost = run["cost"]
            metrics = run["metrics"].get("metrics", {})
            lines.append(
                f"- {lab_id} {view['title']}: run {run['run_id']}, "
                f"status {result.get('status')}, evidence {result.get('evidence_class')}, "
                f"hypothesis_supported {result.get('hypothesis_supported')}, "
                f"validity_passed {result.get('validity_passed')}, "
                f"actual ${float(cost.get('actual_usd', 0.0)):.4f}. "
                f"Selected metrics: {json.dumps(metrics, sort_keys=True)}"
            )
    rows = _trust_rows(root, set(module.get("card_ids", [])))
    if rows:
        lines.append("")
        lines.append("Trust table rows for this module:")
        for row in rows:
            lines.append(
                f"- {row.get('card_id')}: {row.get('rule')} "
                f"[{row.get('evidence_strength')}, {row.get('my_replication')}]"
            )
    prompt = "\n".join(lines)
    return prompt[:MAX_CONTEXT_CHARS]


def render_page(root: Path, module_id: str) -> str:
    module = load_module(root, module_id)
    cards = [_card(root, card_id) for card_id in module.get("card_ids", [])]
    labs = [_run_view(root, lab_id) for lab_id in module.get("lab_ids", [])]
    rows = _trust_rows(root, set(module.get("card_ids", [])))
    cards_html = "".join(_card_html(card) for card in cards)
    labs_html = "".join(_lab_html(view) for view in labs) or "<p class=\"muted\">This module has no labs; it is a reading module.</p>"
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\" />"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />"
        f"<title>{_esc(module.get('id'))} - {_esc(module.get('title'))}</title>"
        f"<style>{CSS}</style></head><body>"
        "<header>"
        f"<span class=\"pill\">{_esc(module.get('id'))}</span>"
        f"<h1>{_esc(module.get('title'))}</h1>"
        f"<p class=\"muted\">{_esc(module.get('objective'))}</p>"
        "</header><main>"
        "<h2>Lesson cards</h2><div class=\"grid\">"
        f"{cards_html}</div>"
        "<h2>Labs and latest runs</h2><div class=\"grid\">"
        f"{labs_html}</div>"
        "<h2>Trust table</h2><section class=\"trust\">"
        f"{_trust_html(rows)}</section>"
        "<h2>Checkpoint</h2><section class=\"panel\">"
        f"{_checkpoint_html(module)}</section>"
        "<h2>Lesson-scoped DeepSeek shell</h2><section class=\"panel\">"
        "<p class=\"muted\">This shell sees only the module context and your chat. "
        "It cannot run labs, read arbitrary files, or change the repository. "
        "Provider key: DEEPSEEK_API_KEY.</p>"
        "<div id=\"shell-log\" class=\"shell-log\"></div>"
        "<form onsubmit=\"sendShell(event)\" class=\"split\">"
        "<textarea id=\"shell-input\" rows=\"3\" placeholder=\"Ask about this lesson...\"></textarea>"
        "<button type=\"submit\">Send</button>"
        "</form>"
        "</section></main>"
        f"<script>{JS}</script></body></html>"
    )


def _clean_messages(messages: object) -> list[Message]:
    if not isinstance(messages, list):
        raise ConfigError("messages must be a list")
    clean: list[Message] = []
    for item in messages[-MAX_SHELL_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            raise ConfigError("messages may contain only user and assistant text")
        content = content.strip()
        if not content:
            continue
        clean.append(Message(role=role, content=content[:MAX_MESSAGE_CHARS]))
    if not clean:
        raise ConfigError("no user message")
    return clean


def answer_shell(
    root: Path,
    module_id: str,
    messages: object,
    client: object | None = None,
) -> str:
    clean = _clean_messages(messages)
    system = build_system_prompt(root, module_id)
    call = PlannedCall(
        call_key="workbench-shell",
        item_id="workbench-shell",
        condition="lesson",
        role="workbench",
        sample=0,
        messages=[Message(role="system", content=system), *clean],
        temperature=0.2,
        max_tokens=700,
        seed=None,
    )
    if client is None:
        client = DeepSeekClient(api_key_from_env())
    result = client.complete(call, SHELL_MODEL)
    return str(result.text).strip()


def checkpoint_payload(
    root: Path,
    module_id: str,
    answers: object,
    write: bool = True,
) -> dict:
    if not isinstance(answers, dict):
        raise ConfigError("answers must be a mapping")
    module = load_module(root, module_id)
    clean = {
        str(key): str(value)
        for key, value in answers.items()
        if isinstance(key, str) and isinstance(value, (str, int, float))
    }
    result = grade(module, clean)
    if write:
        write_result(root, module_id, result)
    items = {
        item_id: {"correct": item["correct"], "given": item["given"]}
        for item_id, item in result["items"].items()
    }
    return {
        "module_id": result["module_id"],
        "correct": result["correct"],
        "total": result["total"],
        "items": items,
    }


class WorkbenchServer(ThreadingHTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        root: Path,
        module_id: str,
        client_factory: Callable[[], object] | None = None,
    ):
        super().__init__(address, WorkbenchHandler)
        self.root = root
        self.module_id = module_id
        self.client_factory = client_factory


class WorkbenchHandler(BaseHTTPRequestHandler):
    server: WorkbenchServer

    def log_message(self, format: str, *args) -> None:
        return

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, status: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path in ("/", f"/{self.server.module_id}"):
            try:
                self._html(200, render_page(self.server.root, self.server.module_id))
            except (ConfigError, OSError) as exc:
                self._html(500, f"<h1>Workbench error</h1><pre>{_esc(exc)}</pre>")
            return
        if self.path == "/health":
            self._json(200, {"status": "ok", "module_id": self.server.module_id})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "invalid content length"})
            return
        if length <= 0 or length > 1_000_000:
            self._json(400, {"error": "invalid body size"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid JSON"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "JSON object required"})
            return

        if self.path == "/api/chat":
            try:
                client = (
                    self.server.client_factory()
                    if self.server.client_factory is not None
                    else None
                )
                reply = answer_shell(
                    self.server.root,
                    self.server.module_id,
                    payload.get("messages"),
                    client=client,
                )
            except ConfigError as exc:
                self._json(503, {"error": str(exc)})
            except Exception as exc:
                self._json(502, {"error": f"shell request failed: {exc}"})
            else:
                self._json(200, {"reply": reply})
            return

        if self.path == "/api/checkpoint":
            try:
                result = checkpoint_payload(
                    self.server.root,
                    self.server.module_id,
                    payload.get("answers"),
                )
            except ConfigError as exc:
                self._json(400, {"error": str(exc)})
            else:
                self._json(200, result)
            return

        self._json(404, {"error": "not found"})


def serve(
    root: Path,
    module_id: str,
    host: str = "127.0.0.1",
    port: int = 8765,
    client_factory: Callable[[], object] | None = None,
) -> int:
    render_page(root, module_id)
    server = WorkbenchServer((host, port), root, module_id, client_factory)
    print(f"workbench: http://{host}:{port}/  module={module_id}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("workbench: stopped")
    finally:
        server.server_close()
    return 0


def render_to_file(root: Path, module_id: str, out: Path) -> Path:
    page = render_page(root, module_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out
