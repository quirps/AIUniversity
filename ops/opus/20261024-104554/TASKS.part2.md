### T-007: Implement status.json generation, README block, and consistency check

**Goal:** `aiu status --write` regenerates `status.json` and the README STATUS block from repo state, and `aiu status --check` exits 1 on any drift.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/status.py`, `tests/test_status.py`, `tests/fixtures/status_repo/` (minimal fake repo tree used by tests)
- modify: `src/aiu/cli.py`, `status.json`, `README.md` (only the text between the markers)

**Interfaces / schemas:** Output must validate against `schemas/status.schema.json` (handoff file).
```python
STATUS_BEGIN = "<!-- STATUS:BEGIN -->"
STATUS_END = "<!-- STATUS:END -->"
IGNORED_KEYS = ("generated_at", "tests")

def compute_status(root: Path, previous: dict | None) -> dict
  # cards: count files matching curriculum/[A-F]/[A-F]-[0-9][0-9][0-9].yaml, grouped by level and by `status` field
  # modules: count curriculum/modules/M-*.yaml
  # labs: count labs/*/manifest.yaml grouped by `status`
  # provenance: count PROVENANCE.md rows starting "| P-", grouped by status column
  # live_runs: every dir experiments/<lab_id>/<run_id>/ containing cost.json, excluding experiments/_template
  # cumulative_cost_usd: round(sum(cost.json.actual_usd over live_runs), 4)
  # last_live_run: run_id with the greatest lexical value, or null
  # tests: copied from previous["tests"] (written only by `aiu check-all`, T-035); null if previous is None
  # known_gaps: copied from previous["known_gaps"]; [] if previous is None
  # generated_at: UTC ISO-8601 "YYYY-MM-DDTHH:MM:SSZ"
def render_readme_block(status: dict) -> str
  # Markdown table. Rows, in order: Cards written, Modules, Labs runnable, Labs specified,
  # Claims verified/unverified/disputed, Live runs, Cumulative spend (USD, measured), Last live run,
  # Tests (passed/failed/at), Known gaps (bullet list).
  # Every number is labeled "measured" (from runs or tests) or "counted" (file counts).
def write_status(root: Path) -> None
  # write status.json with indent=2, sort_keys=True, trailing "\n"; replace README text between markers
def check_status(root: Path) -> list[str]
  # returns human-readable mismatch strings; empty list means OK. Checks:
  # 1. compute_status(root, committed) equals committed status.json, ignoring IGNORED_KEYS
  # 2. README text between markers equals render_readme_block(committed)
  # 3. every live run_id appears as a substring of RESULTS.md
  # 4. committed cumulative_cost_usd equals recomputed sum
  # 5. status.json validates against schemas/status.schema.json
```
CLI: `aiu status --write | --check` (mutually exclusive, one required). `--write` prints `status: written`, exit 0. `--check` prints each mismatch on its own line, then `status: OK` (exit 0) or `status: <n> mismatches` (exit 1). If either marker is missing from README, `--write` and `--check` both exit 6 and print `status: README markers missing`.

**Steps:**
1. Implement `status.py` and wire the CLI.
2. Build `tests/fixtures/status_repo/` containing 1 card, 1 lab manifest, a 2-row PROVENANCE.md, a README with markers, a RESULTS.md, and one live run dir with `cost.json` (`actual_usd: 0.1234`).
3. Tests (each copies the fixture repo into `tmp_path`): (a) write then check ? `[]`; (b) delete the run_id from RESULTS.md ? 1 mismatch; (c) edit README block ? 1 mismatch; (d) edit `cumulative_cost_usd` ? mismatch; (e) `tests` key change alone ? no mismatch; (f) missing markers ? exit 6 via `main()`.
4. Run `uv run aiu status --write` on the real repo and commit.

**Acceptance tests:**
- `uv run pytest tests/test_status.py` ? exit 0.
- `uv run aiu status --write` ? `status: written`, exit 0.
- `uv run aiu status --check` ? last line `status: OK`, exit 0.
- `uv run python -c "import json,jsonschema;jsonschema.validate(json.load(open('status.json')),json.load(open('schemas/status.schema.json')))"` ? exit 0.

**Commands:** `uv run pytest tests/test_status.py; uv run aiu status --write; uv run aiu status --check`

**Definition of done:**
- [ ] `status.json` and the README block are regenerated and committed.
- [ ] A JOURNAL entry has been appended.
- [ ] From this ticket onward, every ticket's DoD runs `uv run aiu status --write` followed by `uv run aiu status --check`.

**Out of scope:** Populating the `tests` key (T-035); editing README outside the markers.

**Open decisions:** none.

---

### T-008: Implement config loading and core pydantic models

**Goal:** `config/models.yaml`, `config/pricing.yaml`, and `config/caps.yaml` exist and load into validated pydantic models.

**Depends on:** T-007.

**Files:**
- create: `config/models.yaml`, `config/pricing.yaml`, `config/caps.yaml`, `src/aiu/config.py`, `src/aiu/models.py`, `tests/test_config.py`

**Interfaces / schemas:**

`config/models.yaml` (exact contents):
```yaml
roles:
  cheap_a:  {model_id: UNPINNED, family: unknown}
  cheap_b:  {model_id: UNPINNED, family: unknown}
  cheap_c:  {model_id: UNPINNED, family: unknown}
  strong:   {model_id: UNPINNED, family: unknown}
  judge_a:  {model_id: UNPINNED, family: unknown}
  judge_b:  {model_id: UNPINNED, family: unknown}
```

`config/pricing.yaml` (exact contents; these numbers are **assumed**, per ADR-022):
```yaml
retrieved_at: null
fixture_defaults: {input_per_mtok: 0.50, output_per_mtok: 1.50}
models: {}
```

`config/caps.yaml` (exact contents):
```yaml
per_lab_usd: 2.00
smoke_total_usd: 5.00
```

```python
class RoleConfig(BaseModel): model_id: str; family: str
class ModelsConfig(BaseModel): roles: dict[Literal["cheap_a","cheap_b","cheap_c","strong","judge_a","judge_b"], RoleConfig]
class Price(BaseModel): input_per_mtok: float = Field(ge=0); output_per_mtok: float = Field(ge=0)
class PricingConfig(BaseModel): retrieved_at: date | None; fixture_defaults: Price; models: dict[str, Price]
class CapsConfig(BaseModel): per_lab_usd: float = Field(gt=0, le=2.0); smoke_total_usd: float = Field(gt=0, le=5.0)
class Config(BaseModel): models: ModelsConfig; pricing: PricingConfig; caps: CapsConfig
class ConfigError(Exception): ...   # the CLI maps this to exit 6
def load_config(root: Path) -> Config
def resolve_role(cfg: Config, role: str, mode: Literal["fixture","live"]) -> RoleConfig
  # live mode raises ConfigError if model_id == "UNPINNED" or model_id is missing from pricing.models
class Message(BaseModel): role: Literal["system","user","assistant"]; content: str
class PlannedCall(BaseModel):
  call_key: str; item_id: str; condition: str; role: str; sample: int
  messages: list[Message]; temperature: float; max_tokens: int; seed: int | None
  response_format: dict | None = None; logprobs: bool = False
  def request_sha256(self) -> str  # sha256 of json.dumps(model_dump(exclude={"call_key"}), sort_keys=True, separators=(",",":"))
class CallResult(BaseModel):
  call_key: str; model_id: str; text: str; prompt_tokens: int; completion_tokens: int
  provider_reported_usd: float | None; latency_ms: int; source: Literal["fixture_synthetic","fixture_recorded","live"]
  request_sha256: str; timestamp: str; logprobs: list | None = None
class Item(BaseModel): id: str; input: dict; expected: dict; meta: dict
```

**Steps:**
1. Write the three config files and both modules.
2. Tests: (a) the real configs load; (b) `resolve_role(..., "live")` on UNPINNED raises ConfigError; (c) fixture mode returns the RoleConfig; (d) `per_lab_usd: 3.0` fails validation; (e) `request_sha256` is stable across two identical PlannedCall instances and changes when the temperature changes.

**Acceptance tests:**
- `uv run pytest tests/test_config.py` ? exit 0.
- `uv run python -c "from aiu.config import load_config; from pathlib import Path; print(load_config(Path('.')).caps.per_lab_usd)"` ? `2.0`, exit 0.

**Commands:** `uv run pytest tests/test_config.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `aiu status --write` and `aiu status --check` both exit 0.
- [ ] `known_gaps` includes `models UNPINNED (OD-01)`.

**Out of scope:** Choosing model IDs or prices (OD-01, T-036).

**Open decisions:** OD-01.

---

### T-009: Implement hardware check

**Goal:** `aiu hwcheck --tier <T> --json` reports measured RAM, disk, and GPU and applies the ADR-014 thresholds.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/hardware.py`, `tests/test_hardware.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class GpuInfo: name: str; vram_total_gb: float; vram_free_gb: float
@dataclass(frozen=True)
class Probe: ram_total_gb: float; ram_available_gb: float; disk_free_gb: float; gpu: GpuInfo | None
def probe(root: Path, run_cmd: Callable[[list[str]], str | None] = default_run) -> Probe
  # psutil.virtual_memory(); psutil.disk_usage(str(root)); GPU via
  # nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits (MiB/1024).
  # FileNotFoundError or nonzero exit -> gpu=None. GB = bytes / 1024**3, rounded to 2 decimals.
def check(tier: str, p: Probe, local_requirements: dict | None = None) -> dict
  # returns the LAB_SPEC �4 JSON object
```
Thresholds (ADR-014):
- `API_ONLY`: always passes; adds the warning `disk_free_gb < 10` when that condition holds.
- `LOCAL_SMALL_GPU_6GB`: requires `gpu` not null, `vram_free_gb >= weights_gb + 1.0`, `disk_free_gb >= 10 + weights_gb`, and `ram_total_gb >= 15.5`.
- `LOCAL_CPU_TINY`: requires `params_b <= 1.0` and `ram_available_gb >= 4`.

A local tier with `local_requirements=None` fails with `missing local_requirements`.

CLI: `aiu hwcheck [--tier T] [--json]`, default tier `API_ONLY`. Without `--json`, prints `hwcheck: <tier> PASS|FAIL` followed by the failures. Exit 0 on pass, 5 on fail.

**Steps:**
1. Implement with an injectable `run_cmd`.
2. Tests use fake probes. The dev-machine profile (measured): ram_total 16, avail 8, disk 41.6, GPU GTX 1060 vram_total 6.0, free 4.0. Expected results:
   - API_ONLY passes.
   - LOCAL_SMALL_GPU_6GB with weights 2.0 passes.
   - LOCAL_SMALL_GPU_6GB with weights 3.5 fails, because 4.0 < 4.5.
   - gpu=None plus a GPU tier fails.
   - LOCAL_CPU_TINY with params 1.5 fails.
   - Disk 8 on API_ONLY passes with a warning.
   - A nonexistent nvidia-smi binary gives gpu None.

**Acceptance tests:**
- `uv run pytest tests/test_hardware.py` ? exit 0.
- `uv run aiu hwcheck --json` ? valid JSON with `"passed": true`, exit 0.
- `uv run aiu hwcheck --tier LOCAL_SMALL_GPU_6GB` ? exit 5. No local_requirements are given, so the output contains `missing local_requirements`.

**Commands:** `uv run pytest tests/test_hardware.py; uv run aiu hwcheck --json`

**Definition of done:**
- [ ] The actual `hwcheck --json` output from the dev machine is pasted into the JOURNAL entry, labeled measured.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Downloading weights; benchmarking tokens/sec.

**Open decisions:** none.

---

### T-010: Implement metrics library

**Goal:** Every ADR-011 metric is implemented in `src/aiu/metrics.py` and verified against hand-computed values.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/metrics.py`, `tests/test_metrics.py`

**Interfaces / schemas:**
```python
def accuracy(pred: Sequence[object|None], gold: Sequence[object]) -> float
def parse_rate(pred: Sequence[object|None]) -> float
def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float | None
def tpr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None
def tnr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]   # n==0 -> (0.0, 1.0)
def flip_rate(ab: Sequence[str], ba: Sequence[str]) -> float            # inputs are chosen answer identities
def first_slot_rate(choices: Sequence[str]) -> float                    # choices in {"A","B"}
def rogan_gladen(p_obs: float, tpr_: float, tnr_: float) -> float | None
def pass_at_k(n: int, c: int, k: int) -> float
def pass_hat_k(n: int, c: int, k: int) -> float
def ece(conf: Sequence[float], correct: Sequence[bool], bins: int = 10) -> float
def compound(p: float, steps: int) -> float
def normalize_answer(s: str) -> str
def exact_match(pred: str | None, gold: str) -> bool                   # None -> False
def proportion(k: int, n: int) -> dict  # {"value": k/n or None, "n": n, "k": k, "ci95": [lo, hi]}
```

**Steps:**
1. Implement the formulas exactly as written in ADR-011.
2. Tests, all with exact or 1e-9 tolerance unless stated:
   - `cohen_kappa(["p","p","f","f"],["p","f","f","f"]) == 0.5`
   - kappa returns None when p_e == 1
   - `wilson_ci(24,30)` lo ? 0.6269, hi ? 0.9049 (tolerance 1e-3)
   - `rogan_gladen(0.19, 0.8, 0.92) ? 0.15`
   - rogan_gladen returns None when tpr+tnr ? 1
   - `pass_at_k(5,3,3) == 1.0`
   - `pass_hat_k(5,3,3) == 0.1`
   - `compound(0.95,5) ? 0.7738` (tolerance 1e-4)
   - ece is 0 for perfectly calibrated bins
   - a confidence of exactly 1.0 lands in the last bin
   - `normalize_answer("  The, River! ") == "the river"`
   - `flip_rate(["c","c"],["c","w"]) == 0.5`

**Acceptance tests:**
- `uv run pytest tests/test_metrics.py` ? exit 0.

**Commands:** `uv run pytest tests/test_metrics.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Plotting; macro_f1 and confusion matrices (needed only by specified lab E3, v2).

**Open decisions:** none.

---

### T-011: Implement cost estimator and CostGuard

**Goal:** Pre-run and mid-run cost guards behave as ADR-008 specifies and are proven by tests.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/cost.py`, `tests/test_cost.py`

**Interfaces / schemas:**
```python
def estimate_call(call: PlannedCall, price: Price) -> float
  # est_in = ceil(total utf-8 bytes of all message contents / 3); est_out = max_tokens
def actual_cost(prompt_tokens: int, completion_tokens: int, price: Price) -> float
def price_for(cfg: Config, role: str, mode: str) -> Price
  # fixture -> pricing.fixture_defaults; live -> pricing.models[model_id] (ConfigError if missing)
def effective_cap(cfg: Config, requested: float | None, kind: Literal["lab","smoke"]) -> float
  # None -> config default; requested > default -> ConfigError (exit 6)
class CostCapExceeded(Exception): ...   # the CLI maps this to exit 4
class CostGuard:
  def __init__(self, cap_usd: float): ...
  def preflight(self, estimates: list[float]) -> None   # raises CostCapExceeded if sum > cap
  def before_call(self, est_next: float) -> None        # raises if actual_so_far + est_next > cap
  def record(self, usd: float) -> None
  actual_so_far: float; calls: int
def cost_record(...) -> dict   # the exact LAB_SPEC �5 cost.json keys
```

**Steps:**
1. Implement the module.
2. Tests:
   - A message of 300 ASCII bytes with max_tokens 16 at 0.5/1.5 gives `(100*0.5 + 16*1.5)/1e6`.
   - A preflight sum of 2.01 against cap 2.00 raises.
   - A mid-run actual of 1.99 plus an estimate of 0.02 raises.
   - `effective_cap(cfg, 3.0, "lab")` raises ConfigError.
   - `effective_cap(cfg, 0.5, "lab") == 0.5`.

**Acceptance tests:**
- `uv run pytest tests/test_cost.py` ? exit 0.

**Commands:** `uv run pytest tests/test_cost.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Fetching live prices.

**Open decisions:** none.

---

### T-012: Implement client interface and FixtureClient

**Goal:** Planned calls resolve to fixture records deterministically, with exit 3 on a missing or mismatched fixture.

**Depends on:** T-011.

**Files:**
- create: `src/aiu/clients/__init__.py`, `src/aiu/clients/base.py`, `src/aiu/clients/fixture.py`, `tests/test_fixture_client.py`

**Interfaces / schemas:**
```python
class LLMClient(Protocol):
  def complete(self, call: PlannedCall, model_id: str) -> CallResult: ...
class MissingFixture(Exception): ...   # the CLI maps this to exit 3
class FixtureClient:
  def __init__(self, path: Path): ...   # loads JSONL keyed by call_key; duplicate key -> ValueError
  def complete(self, call, model_id) -> CallResult
    # absent key -> MissingFixture
    # record.source == "fixture_recorded" and request_sha256 != call.request_sha256() -> MissingFixture
    # returns the stored CallResult with latency_ms=0
```
Fixture JSONL line = `CallResult.model_dump()` as JSON.

**Steps:**
1. Implement.
2. Tests:
   - A hit returns the stored text.
   - A miss raises.
   - A recorded record with a hash mismatch raises.
   - A synthetic record with a hash mismatch returns.
   - Duplicate keys raise ValueError.

**Acceptance tests:**
- `uv run pytest tests/test_fixture_client.py` ? exit 0.

**Commands:** `uv run pytest tests/test_fixture_client.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** HTTP.

**Open decisions:** none.

---

### T-013: Implement OpenRouterClient with retries and mock-transport tests

**Goal:** A live HTTP client implements ADR-005 exactly and is tested with zero sockets.

**Depends on:** T-012.

**Files:**
- create: `src/aiu/clients/openrouter.py`, `tests/test_openrouter_client.py`

**Interfaces / schemas:**
```python
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
RETRY_STATUS = {408, 429, 500, 502, 503, 504}
class AuthError(Exception): ...        # HTTP 401 -> the CLI exits 6
class ProviderError(Exception): ...    # retries exhausted or non-retryable 4xx
class OpenRouterClient:
  def __init__(self, api_key: str, transport: httpx.BaseTransport | None = None,
               sleep: Callable[[float], None] = time.sleep, timeout: float = 60.0): ...
  def complete(self, call: PlannedCall, model_id: str) -> CallResult
    # body keys per ADR-005; omit seed if None, response_format if None, logprobs if False
    # text = choices[0].message.content (None -> "")
    # tokens from usage.prompt_tokens / completion_tokens (missing -> 0, record warning)
    # provider_reported_usd = usage.cost if present else None
    # source="live"; timestamp = UTC ISO-8601
def api_key_from_env() -> str   # ConfigError if OPENROUTER_API_KEY is unset or empty
```
Retry rule: at most 3 retries, sleeping `2**attempt` for attempt 0, 1, 2. The key never appears in logs, exceptions, or artifacts.

**Steps:**
1. Implement.
2. Tests use `httpx.MockTransport`:
   - (a) The request body and headers match the spec, `Authorization` included, and `X-Title: AI University` is present.
   - (b) 429, 429, then 200 succeeds, with sleep called with [1, 2].
   - (c) Four consecutive 503s raise ProviderError after 3 retries.
   - (d) 401 raises AuthError without retrying.
   - (e) 400 raises ProviderError without retrying.
   - (f) A missing usage block gives tokens 0.
   - (g) `repr` and `str` of exceptions do not contain the key.

**Acceptance tests:**
- `uv run pytest tests/test_openrouter_client.py` ? exit 0, with zero socket errors (pytest-socket is active).

**Commands:** `uv run pytest tests/test_openrouter_client.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Streaming, async, provider fallback routing.

**Open decisions:** none.

---

### T-014: Implement run IDs, `lab new-run`, and the prediction gate

**Goal:** A run directory with a prediction template can be created, and `check_prediction` enforces ADR-016.

**Depends on:** T-007.

**Files:**
- create: `src/aiu/runs.py`, `tests/test_runs.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z-(fixture|live)-[0-9a-f]{6}$")
def new_run_id(mode: str, now: datetime | None = None, rand_hex: str | None = None) -> str
def default_out_dir(mode: str) -> Path        # fixture -> ".runs", live -> "experiments"
def run_dir(out: Path, lab_id: str, run_id: str) -> Path
def create_run(root: Path, lab_id: str, mode: str, out: Path | None) -> tuple[str, Path]
  # copies experiments/_template/prediction.md and fills front matter lab_id, run_id, mode;
  # leaves written_at empty and predicted_metrics as {}
class PredictionGateError(Exception): ...     # the CLI maps this to exit 7
def check_prediction(path: Path, metric_names: set[str], now: datetime) -> dict
  # YAML front matter between the first two '---' lines; requires written_at (ISO-8601 UTC) < now;
  # predicted_metrics is a non-empty mapping with keys ? metric_names
def freeze_prediction(rdir: Path) -> str      # writes prediction.sha256 (hex of file bytes) and returns it
def prediction_unchanged(rdir: Path) -> bool
```
CLI: `aiu lab new-run LAB_ID --mode fixture|live [--out-dir PATH]` prints `run_id=<id> dir=<path>`, exit 0. It exits 6 if `labs/<LAB_ID>/manifest.yaml` is absent; until T-017 lands, tests use a tmp manifest.

**Steps:**
1. Implement.
2. Tests:
   - The regex matches the generated ID.
   - An empty predicted_metrics raises.
   - An unknown metric key raises.
   - A future written_at raises.
   - A valid prediction passes.
   - The hash changes after an edit.

**Acceptance tests:**
- `uv run pytest tests/test_runs.py` ? exit 0.

**Commands:** `uv run pytest tests/test_runs.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Executing labs.

**Open decisions:** none.

---

### T-015: Implement the lab registry, runner engine, and `lab run` / `lab estimate`

**Goal:** `aiu.runner.run_lab` executes the LAB_SPEC �3 algorithm for any registered lab, with exact exit codes.

**Depends on:** T-009, T-010, T-012, T-013, T-014.

**Files:**
- create: `src/aiu/runner.py`, `src/aiu/labs/__init__.py`, `src/aiu/labs/base.py`, `tests/test_runner.py`, `tests/fixtures/toy_lab/` (manifest.yaml, data/items.jsonl with 4 items, fixtures/responses.jsonl)
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
class LabImpl(Protocol):
  lab_id: str
  def plan(self, items: list[Item], manifest: dict, cfg: Config) -> list[PlannedCall]
  def score(self, items: list[Item], results: list[CallResult], manifest: dict) -> dict[str, float | None]
REGISTRY: dict[str, type[LabImpl]]  # filled by T-019..T-023
def register(cls): ...               # decorator
def load_manifest(root: Path, lab_id: str) -> dict
def load_items(path: Path, limit: int | None) -> list[Item]   # sorted by id; first N
def evaluate(conds: list[dict], metrics: dict, rule: str) -> bool | None  # None if any referenced metric is None or missing
def run_lab(root: Path, lab_id: str, run_id: str, mode: str, cap: float | None,
            limit: int | None, record: bool, out: Path | None,
            client_factory: Callable[[str], LLMClient] | None = None, now: datetime | None = None) -> int
def estimate_lab(root: Path, lab_id: str, limit: int | None, mode: str = "live") -> float
```
Artifact contents:
- `config.json`: `{lab_id, run_id, mode, manifest_sha256, roles: {role: {model_id, family}}, temperature, seed, max_tokens, samples_per_call, limit, started_at, aiu_version, hw: <hwcheck dict>}`
- `result.json`: `{status: "completed"|"aborted_cost"|"failed", hypothesis_supported: bool|null, validity_passed: bool|null, evidence_class: "measured"|"assumed", finished_at, n_calls, error: str|null}`
- `evidence_class` is `measured` only if `mode == live` and every CallResult.source is `live`.
- `metrics.json`: `{metrics: {...flat...}, proportions: {name: proportion dict}, evidence_class}`
- `responses.jsonl`: one CallResult per line.

`--record` (live only) overwrites `labs/<id>/fixtures/responses.jsonl` with `fixture_recorded` copies. It is an error in fixture mode (exit 6).

Exit mapping:
- `ConfigError` ? 6
- `PredictionGateError` ? 7
- hardware fail ? 5
- `CostCapExceeded` ? 4, after writing `result.json` with `aborted_cost` plus partial `responses.jsonl` and `cost.json`
- `MissingFixture` ? 3
- `AuthError` ? 6
- `ProviderError` ? 1, after writing `result.json` with `failed`

stdout is exactly one line, `run_id=<id> status=<s> cost_usd=<x.xxxx>`. No metric is printed.

CLI:
- `aiu lab run LAB_ID --run-id RUN_ID --mode M [--cap USD] [--limit N] [--record] [--out-dir PATH]`
- `aiu lab estimate LAB_ID [--limit N]` prints `estimate_usd=<x.xxxx> calls=<n> cap_usd=<y>`. It uses live pricing if every role is pinned, otherwise fixture_defaults with the suffix ` basis=assumed`. Exit 0.

**Steps:**
1. Implement the runner and a toy LabImpl registered only in tests (a `conftest.py` registers `toy`). The toy lab uses ID `L-999` under `tmp_path`.
2. Tests:
   - Fixture run ? exit 0 with all 8 artifacts present, `evidence_class == "assumed"`, and stdout matching the regex.
   - Missing prediction ? 7.
   - Cap 0.0000001 ? 4 with `result.json.status == "aborted_cost"`.
   - A removed fixture line ? 3.
   - Live mode with UNPINNED roles ? 6.
   - The prediction edited after the run ? `prediction_unchanged` is False.

**Acceptance tests:**
- `uv run pytest tests/test_runner.py` ? exit 0.

**Commands:** `uv run pytest tests/test_runner.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Real lab implementations; postmortem validation.

**Open decisions:** none.

---

### T-016: Implement post-mortem check

**Goal:** `aiu lab postmortem-check` exits 0 only for a complete post-mortem whose prediction is unchanged.

**Depends on:** T-015.

**Files:**
- create: `src/aiu/postmortem.py`, `tests/test_postmortem.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Required headings in `postmortem.md` are those of `experiments/_template/postmortem.md`:
- `## Prediction vs outcome`
- `## What surprised me`
- `## Confounds observed`
- `## Rule-of-thumb update`
- `## Next experiment`

```python
REQUIRED_HEADINGS: tuple[str, ...]  # exactly the five above
def check_postmortem(rdir: Path) -> list[str]
  # problems: missing file; missing heading; a section body shorter than 20 non-whitespace chars
  # or still containing the template placeholder "TODO";
  # front matter `trust_table_row` absent or not a rule text present in learner/trust_table.yaml;
  # prediction.sha256 missing or mismatched
```
CLI: `aiu lab postmortem-check LAB_ID --run-id RUN_ID [--out-dir PATH]` prints each problem, then `postmortem: OK` (exit 0) or `postmortem: <n> problems` (exit 1). The out-dir default follows the mode encoded in run_id.

**Steps:**
1. Implement.
2. Tests:
   - The untouched template ? ?5 problems.
   - A complete post-mortem with a matching trust row ? OK.
   - An edited prediction ? problem `prediction modified after run`.

**Acceptance tests:**
- `uv run pytest tests/test_postmortem.py` ? exit 0.

**Commands:** `uv run pytest tests/test_postmortem.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Judging post-mortem quality (human rubric, GOVERNANCE).

**Open decisions:** none.

---

### T-017: Author all 17 lab manifests and implement `labs list` / `labs check-tiers`

**Goal:** Every lab in LAB_SPEC �6 has a schema-valid manifest, and the tier policy is mechanically checked.

**Depends on:** T-006, T-015.

**Files:**
- create: `labs/<ID>/manifest.yaml` for E1-E13 and L-001-L-004 (17 files), `src/aiu/labs/tiers.py`, `tests/test_tiers.py`, `tests/fixtures/invalid_lab_local_bad_fallback.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Each manifest follows the `lab` schema with these values:
- **From LAB_SPEC �6:** `id`, `title`, `status`, `hardware_tier: API_ONLY`, `concept_ids`, `cost_cap_usd: 2.00`, `cost_basis: assumed`, `expected_cost_usd`, and `post_mortem_template`.
- **From �8/�9:** dataset, conditions, metrics, pass_fail, validity_checks, and confounds.

Metric `name`s with `<cond>` are expanded to one entry per condition. Example: E9 has `accuracy:oracle` . `accuracy:d20_middle`, then `accuracy_drop:d5_start` . `accuracy_drop:d20_middle`, then `max_drop` and `unknown_rate:<cond>`. Every `impl` names a function path such as `aiu.labs.e9.score`.

Field values by lab group:
- **Runnable labs:** `fixtures.path = labs/<ID>/fixtures/responses.jsonl`, `provenance: synthetic`, and `n_calls` equal to the �6 call count (0 for L-003).
- **Specified labs:** `fixtures: {path: null, provenance: none, n_calls: 0}`; `dataset.n_items` as given in �9; `generator: null` where human labels are needed.
- **Lab roles:** `model_roles` copied from �6, with `[]` for "none".
- **`expected_runtime_minutes` (assumed):** runnable labs use `ceil(calls * 1.5 s / 60)`; L-003 uses 1.

```python
def check_tiers(root: Path) -> list[str]
  # each manifest: tier in enum; local tier => api_fallback.lab_id exists, its manifest
  # hardware_tier == API_ONLY, and its fixtures.provenance != "none"; local_requirements present
def list_labs(root: Path) -> list[tuple[str, str, str, str]]   # id, status, tier, title
```
CLI:
- `aiu labs list` prints `<id>\t<status>\t<tier>\t<title>` per lab sorted by id, exit 0.
- `aiu labs check-tiers` prints problems, then `tiers: OK (<n> labs)`; exit 0 or 1. With an explicit file argument (`aiu labs check-tiers PATH`) it checks only that manifest.

**Steps:**
1. Write the 17 manifests.
2. Implement tiers.py and the CLI.
3. Tests:
   - The real repo has 0 problems.
   - A tmp LOCAL_SMALL_GPU_6GB manifest with a fallback to a `specified` lab without fixtures ? problem.
   - A local manifest with weights_gb 4.0 fails schema validation.

**Acceptance tests:**
- `uv run aiu validate labs` ? `validate: 17 files, 0 errors`, exit 0.
- `uv run aiu labs list` ? 17 lines, exit 0.
- `uv run aiu labs check-tiers` ? `tiers: OK (17 labs)`, exit 0.
- `uv run aiu labs check-tiers tests/fixtures/invalid_lab_local_bad_fallback.yaml` ? exit 1.
- `uv run pytest tests/test_tiers.py` ? exit 0.

**Commands:** `uv run aiu validate labs; uv run aiu labs check-tiers; uv run pytest tests/test_tiers.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` shows labs runnable 5 and specified 12.
- [ ] `status --check` passes.

**Out of scope:** Implementing any lab; local-tier labs.

**Open decisions:** none.

---

### T-018: Implement dataset build and synthetic fixture framework

**Goal:** `aiu dataset build` and `aiu fixtures synth` are deterministic and byte-checkable for any lab with a generator.

**Depends on:** T-017.

**Files:**
- create: `src/aiu/generators/__init__.py`, `src/aiu/generators/base.py`, `src/aiu/fixtures_synth.py`, `tests/test_generators_base.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SEED = 1337
GENERATORS: dict[str, Callable[[random.Random], list[Item]]]   # filled by T-019..T-023
def serialize(items: list[Item]) -> bytes
  # sorted by id; json.dumps(sort_keys=True, ensure_ascii=False, separators=(",",":")); "\n" line endings; trailing "\n"
def build(root: Path, lab_id: str, check: bool) -> int
  # check=True -> compare bytes, exit 1 on diff; else write labs/<id>/data/items.jsonl
SYNTH: dict[str, Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]]]
def synth(root: Path, lab_id: str, check: bool) -> int
  # plans with fixture mode, no limit; rng = random.Random(SEED); source="fixture_synthetic";
  # model_id="fixture"; prompt_tokens=ceil(bytes/3); completion_tokens=len(text)//4+1;
  # timestamp="1970-01-01T00:00:00Z"
```
CLI: `aiu dataset build LAB_ID [--check]` and `aiu fixtures synth LAB_ID [--check]`. Both print `<cmd>: <lab_id> OK|DIFF|WRITTEN`. Exit codes: 0, 1 on DIFF, 6 if no generator is registered.

**Steps:**
1. Implement.
2. Tests use a toy generator: two builds produce identical bytes; `--check` after a manual edit ? 1; an unknown lab ? 6.

**Acceptance tests:**
- `uv run pytest tests/test_generators_base.py` ? exit 0.
- `uv run aiu dataset build E1` ? exit 6. E1 has no generator, which is expected.

**Commands:** `uv run pytest tests/test_generators_base.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Lab-specific generators.

**Open decisions:** none.

---

### T-019: Implement lab L-003 (eval statistics workbench)

**Goal:** L-003 runs in fixture mode with zero model calls and reproduces exact, hand-checkable statistics.

**Depends on:** T-018.

**Files:**
- create: `src/aiu/generators/l003.py`, `src/aiu/labs/l003.py`, `labs/L-003/data/items.jsonl`, `labs/L-003/data/DATASET_CARD.md`, `labs/L-003/fixtures/responses.jsonl` (empty file), `tests/test_lab_l003.py`

**Interfaces / schemas:** The generator produces 200 label items (IDs `j000`.`j199`) with exact counts from LAB_SPEC �8: 24 TP, 6 FN, 14 FP, 156 TN. The positive label is `fail`. It also produces 20 agent items (`t00`.`t19`) with `expected = {successes: c, trials: 5}`, where c comes from the listed counts. Item order is shuffled by `random.Random(1337)` before ID assignment; ids are then sorted.

`plan()` returns `[]`. `score()` computes the metrics below:

| Metric | Expected value | Tolerance |
|---|---|---|
| `raw_agreement` | 0.90 | exact |
| `tpr` | 0.80 | exact |
| `tnr` | 156/170 | 1e-9 |
| `observed_fail_rate` | 0.19 | exact |
| `true_fail_rate` | 0.15 | exact |
| `corrected_fail_rate` | `rogan_gladen(0.19, 0.8, 156/170)` | 1e-9 |
| `kappa` | 0.6732 | 1e-3 |
| `agreement_minus_kappa` | 0.90 ? kappa | 1e-9 |
| `compound_0.95_5` | 0.7738 | 1e-4 |

`corrected_fail_rate` is approximately 0.1504. Both `kappa` and `corrected_fail_rate` are recomputed in the test from the counts via `aiu.metrics`. `pass_at_3` and `pass_hat_3` are means of `pass_at_k(5,c,3)` and `pass_hat_k(5,c,3)` over the 20 tasks, also recomputed in the test.

The `pass_fail` condition `agreement_minus_kappa >= 0.15` is therefore true by construction.

**Steps:**
1. Implement the generator and lab; register both.
2. `uv run aiu dataset build L-003`; create the empty fixture file.
3. Write the DATASET_CARD.md: synthetic, seed 1337, counts, license per OD-04, and the bias note "rates chosen for teaching, not observed in any real system".
4. Tests: an end-to-end fixture run via `run_lab` into `tmp_path` with a valid prediction, asserting the values above and `hypothesis_supported is True`.

**Acceptance tests:**
- `uv run aiu dataset build L-003 --check` ? `OK`, exit 0.
- `uv run pytest tests/test_lab_l003.py` ? exit 0.
- The PowerShell sequence below ? final exit 0.
  ```
  $o=(uv run aiu lab new-run L-003 --mode fixture); $id=($o -split ' ')[0] -replace 'run_id=',''
  uv run python -c "import sys,pathlib,datetime;p=pathlib.Path('.runs/L-003/'+sys.argv[1]+'/prediction.md');t=p.read_text();t=t.replace('written_at:','written_at: '+(datetime.datetime.utcnow()-datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),1).replace('predicted_metrics: {}','predicted_metrics: {kappa: 0.8}',1);p.write_text(t)" $id
  uv run aiu lab run L-003 --run-id $id --mode fixture
  ```
  This sequence requires the prediction template to contain the literal lines `written_at:` and `predicted_metrics: {}`. If it does not, the template is a spec defect.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Live mode; L-003 has no model calls.

**Open decisions:** OD-04 (content license).

---

### T-020: Implement lab E9 (context distractors and position)

**Goal:** E9 builds its dataset, synthesizes fixtures, and runs end-to-end in fixture mode exactly per LAB_SPEC �8.

**Depends on:** T-018.

**Files:**
- create: `src/aiu/generators/e9.py`, `src/aiu/labs/e9.py`, `labs/E9/data/items.jsonl`, `labs/E9/data/DATASET_CARD.md`, `labs/E9/fixtures/responses.jsonl`, `tests/test_lab_e9.py`, `tests/helpers.py`

**Interfaces / schemas:**
- **Data and prompts:** LAB_SPEC �8 E9 (60 items, 5 conditions, prompts verbatim, role `cheap_a`, temperature 0, seed 1337, max_tokens 16).
- **Distractor order:** `meta.distractor_order` (fixed in the generator), not random at plan time.
- **call_key:** `"{item_id}|{condition}|cheap_a|0"`.
- **Synthetic fixture:** for each call, `rng.random() < error_rate[cond]` produces distractor 0's value, otherwise the expected answer. Rates are given in LAB_SPEC �8.

`tests/helpers.py`:
```python
def fill_prediction(rdir: Path, metrics: dict) -> None   # sets written_at = now-60s, predicted_metrics = metrics
def run_fixture(root: Path, lab_id: str, tmp: Path, limit: int | None = None) -> tuple[int, Path]
```
T-019's test is refactored to use these helpers.

**Steps:**
1. Implement the generator. Entities are fictional names built from syllable lists in the generator file. Each passage is 60-90 words, enforced by a generator assertion.
2. Run `aiu dataset build E9` and `aiu fixtures synth E9`.
3. Tests:
   - 60 items.
   - Every distractor name is within edit distance ?2 of the key name and not equal to it.
   - 300 planned calls.
   - A fixture run exits 0.
   - `metrics.json` contains every manifest metric name.
   - `validity_passed is True`.
   - `evidence_class == "assumed"`.
   - The planned prompt for `d20_middle` places the key passage at index 10.

**Acceptance tests:**
- `uv run aiu dataset build E9 --check` ? exit 0.
- `uv run aiu fixtures synth E9 --check` ? exit 0.
- `uv run pytest tests/test_lab_e9.py` ? exit 0.
- `uv run aiu lab estimate E9` ? line contains `calls=300` and `basis=assumed`, exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended, recording the assumed estimate.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Live runs (T-037).

**Open decisions:** none.

---

### T-021: Implement lab E2 (schema field order)

**Goal:** E2 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e2.py`, `src/aiu/labs/e2.py`, `labs/E2/data/items.jsonl`, `labs/E2/data/DATASET_CARD.md`, `labs/E2/fixtures/responses.jsonl`, `tests/test_lab_e2.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E2 (80 items, 40/40 split; conditions verdict_first, reasoning_first, evidence_first).
- **Parser:** first `{` to last `}`, then `json.loads`; `verdict` must be in the allowed set, otherwise None.
- **Synthetic fixture texts:** JSON with keys in the condition's order.
  - A wrong verdict is the flipped label, at the �8 rate.
  - At rate 0.02 the text is `not json` (a parse failure).
  - `evidence_quote` is an exact sentence from the passage.
- **`mean_rationale_chars`:** mean `len(reasoning)` over parsed items.

**Steps:**
1. Implement, build, and synth.
2. Tests:
   - Exactly one attribute differs between the passage fact and each not_entailed claim (the generator records `meta.changed_attr`).
   - The parser handles a leading prose prefix.
   - The fixture run exits 0 with all metrics present and `validity_passed is True`.

**Acceptance tests:**
- `uv run aiu dataset build E2 --check` ? exit 0.
- `uv run aiu fixtures synth E2 --check` ? exit 0.
- `uv run pytest tests/test_lab_e2.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** `response_format` structured-output variant (v2).

**Open decisions:** none.

---

### T-022: Implement lab E4 (escape hatch)

**Goal:** E4 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e4.py`, `src/aiu/labs/e4.py`, `labs/E4/data/items.jsonl`, `labs/E4/data/DATASET_CARD.md`, `labs/E4/fixtures/responses.jsonl`, `tests/test_lab_e4.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E4 (80 items with 60 in-taxonomy and 20 OOT, by the exact per-label counts in �8; 2 conditions; label-only output).
- **Parser:** `normalize_answer(text)` must equal a normalized allowed label for the condition, otherwise None.
- **Synthetic fixture rates:** per �8. Random labels are drawn with the same rng.

**Steps:**
1. Implement, build, and synth.
2. Tests:
   - Label counts match �8 exactly.
   - `other` is not allowed in `no_escape` (parses to None).
   - The fixture run exits 0 with `validity_passed is True` and all metrics present.

**Acceptance tests:**
- `uv run aiu dataset build E4 --check` ? exit 0.
- `uv run aiu fixtures synth E4 --check` ? exit 0.
- `uv run pytest tests/test_lab_e4.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Hierarchical classification.

**Open decisions:** none.

---

### T-023: Implement lab E5 (position and verbosity bias)

**Goal:** E5 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e5.py`, `src/aiu/labs/e5.py`, `labs/E5/data/items.jsonl`, `labs/E5/data/DATASET_CARD.md`, `labs/E5/fixtures/responses.jsonl`, `tests/test_lab_e5.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E5 (40 items, 4 conditions, role `judge_a`, output `A` or `B`).
- **Score mapping:** the slot letter maps to identity `correct` or `wrong` per condition.
- **Parser:** first non-space char uppercased, which must be in {A, B}, otherwise None. A None is excluded from flip pairs and counted in a `parse_rate` metric that is added to the manifest metric list in this ticket.
- **`flip_rate_padded`:** computed over the pair (cw_padwrong, wc_padwrong).
- **Synthetic fixture:** per �8.

**Steps:**
1. Implement, build, and synth.
2. Update `labs/E5/manifest.yaml` to add `parse_rate` and bump nothing else.
3. Tests:
   - Hand-built results [A,B] for cw and wc give flip_rate 0 and first_slot 0.5.
   - The fixture run exits 0 with `validity_passed is True`.

**Acceptance tests:**
- `uv run aiu dataset build E5 --check` ? exit 0.
- `uv run aiu fixtures synth E5 --check` ? exit 0.
- `uv run pytest tests/test_lab_e5.py` ? exit 0.
- `uv run aiu validate labs` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Cross-family judging (E6).

**Open decisions:** none.

---

### T-024: Implement smoke suite with total cost cap

**Goal:** `aiu smoke --mode fixture` runs every runnable lab with zero network, and `--mode live` is bounded by `smoke_total_usd`.

**Depends on:** T-019, T-020, T-021, T-022, T-023, T-016.

**Files:**
- create: `src/aiu/smoke.py`, `tests/test_smoke.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SMOKE_PLAN: list[tuple[str, int | None]] = [("L-003", None), ("E9", 20), ("E2", 20), ("E4", 20), ("E5", 20)]
def run_smoke(root: Path, mode: str, cap: float | None, now: datetime | None = None,
              client_factory=None) -> int
  # total_cap = effective_cap(cfg, cap, "smoke")
  # preflight: total estimate over all labs (estimate_lab with limits) > total_cap -> exit 4, no calls
  # per lab: create_run; write prediction with front matter smoke: true, written_at=now-60s,
  #   predicted_metrics={<first manifest metric>: null}; then run_lab with
  #   cap=min(per_lab_usd, total_cap - spent)
  # any lab exit != 0 -> stop and return that code
  # summary written to <out>/smoke-<run_stamp>.json:
  #   {mode, labs:[{lab_id, run_id, status, cost_usd}], total_cost_usd, cap_usd}
```
The prediction gate accepts `null` values when `smoke: true`. This is a `check_prediction` amendment: values may be null only if `smoke` is true. Smoke run dirs created in live mode are real live runs and must be indexed in RESULTS.md (GOVERNANCE) with lesson `smoke run; no learner prediction`.

CLI: `aiu smoke --mode fixture|live [--cap USD]`. It prints one line per lab, then `smoke: <mode> total_cost_usd=<x.xxxx> cap_usd=<y> OK|FAIL`. Exit 0, or the first failing code.

**Steps:**
1. Implement and amend `runs.check_prediction`.
2. Tests:
   - Fixture smoke into tmp ? exit 0 with 5 labs completed and `total_cost_usd == 0`.
   - `--cap 6` ? exit 6.
   - A live smoke with a mock client and a cap below the estimate ? exit 4 with zero calls made.

**Acceptance tests:**
- `uv run aiu smoke --mode fixture` ? last line ends `OK`, exit 0.
- `uv run aiu smoke --mode fixture --cap 6` ? exit 6.
- `uv run pytest tests/test_smoke.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended, with the smoke output pasted.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Running live smoke (T-036).

**Open decisions:** none.

---

### T-025: Implement module checkpoint grader

**Goal:** `aiu checkpoint grade` deterministically grades the deterministic items of a module's checkpoint.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/checkpoint.py`, `tests/test_checkpoint.py`, `learner/checkpoints/.gitkeep`, `tests/fixtures/module_test.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** The answers file is YAML of the form `{module_id: M-A1, answers: {Q01: "B", Q02: 0.77}}`.

Grading rules by item type:
- `mcq`: exact match of the trimmed string against `answer`.
- `exact`: `normalize_answer` equality.
- `numeric`: `abs(given - answer) <= tolerance`.
- A missing answer is incorrect.

```python
def grade(module: dict, answers: dict) -> dict
  # {module_id, total, correct, items: {Q01: {correct: bool, given, expected}}, graded_at}
```
CLI: `aiu checkpoint grade MODULE_ID --answers PATH`. The module is loaded from `curriculum/modules/<ID>.yaml`; a missing module ? exit 6. Writes `learner/checkpoints/<ID>.result.json` and prints `checkpoint: <correct>/<total>`. Exit 0 if every item is correct, otherwise 1.

**Steps:**
1. Implement.
2. Tests use the fixture module (3 items, one of each type): all correct ? exit 0; one wrong ? exit 1; a numeric answer within tolerance ? correct.

**Acceptance tests:**
- `uv run pytest tests/test_checkpoint.py` ? exit 0.

**Commands:** `uv run pytest tests/test_checkpoint.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Grading human-rubric items; LLM grading (forbidden, ADR-019).

**Open decisions:** none.

---

### T-026: Implement provenance ledger check

**Goal:** `aiu provenance check` exits 1 if any card cites a claim missing from `PROVENANCE.md` or disagrees with the ledger status.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/provenance.py`, `tests/test_provenance.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Ledger rows are markdown table rows beginning `| P-###`, with columns in this order: `ID | Claim | Tag | Status | Source | Date | Method | Cards`.
```python
@dataclass(frozen=True)
class Claim: id: str; claim: str; tag: str; status: str; source: str; date: str; method: str; cards: list[str]
def parse_ledger(text: str) -> dict[str, Claim]   # duplicate id or status not in enum -> ValueError
def check(root: Path) -> list[str]
  # 1. every card verify[].claim_id exists in the ledger
  # 2. card verify status == ledger status
  # 3. ledger status "verified" requires a non-empty Source, a YYYY-MM-DD Date, and a non-empty Method
  # 4. every card ID listed in a ledger row's Cards column that has a card file cites that claim
```
CLI: `aiu provenance check` prints problems, then `provenance: OK (<n> claims)`; exit 0 or 1.

**Steps:**
1. Implement.
2. Tests:
   - Synthetic ledger and card in tmp: OK.
   - Missing claim ? problem.
   - Status mismatch ? problem.
   - A verified row with an empty source ? problem.

**Acceptance tests:**
- `uv run aiu provenance check` ? exit 0 against the real repo (exemplar cards cite P-001, P-011, and P-042, which exist in the handoff ledger).
- `uv run pytest tests/test_provenance.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Fetching or checking URLs; only humans verify (ADR-018).

**Open decisions:** none.

---

### T-027: Implement traceability check

**Goal:** `aiu traceability check` enforces the TRACEABILITY.md rules against the card files.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/traceability.py`, `tests/test_traceability.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class Row: src: str; concept: str; card: str; experiment: str; tag: str; status: str
def parse_rows(text: str) -> list[Row]   # rows starting "| �" or "| none"
def check(root: Path, require_all_cards: bool) -> list[str]
  # 1. each card file appears in exactly one row (match by card id)
  # 2. card.source_section == row.src
  # 3. row.experiment == "-" <=> card.experiment_id is null; else equal
  # 4. each referenced experiment (not "-", not "E1-E13") has labs/<id>/manifest.yaml
  # 5. if require_all_cards: every row card id matching ^[A-F]-\d{3}$ has a file
```
CLI: `aiu traceability check [--require-all]` prints problems, then `traceability: OK (<rows> rows, <cards> cards)`; exit 0 or 1.

**Steps:**
1. Implement.
2. Tests:
   - A tmp repo with a matching card ? OK.
   - A source_section mismatch ? problem.
   - experiment null versus `E9` ? problem.
   - A card absent from the table ? problem.

**Acceptance tests:**
- `uv run aiu traceability check` ? exit 0 (3 exemplar cards).
- `uv run aiu traceability check --require-all` ? exit 1 before T-033. This is expected and is recorded in the JOURNAL.
- `uv run pytest tests/test_traceability.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Editing TRACEABILITY.md content.

**Open decisions:** none.

---

### T-028: Author the 13 module YAML files

**Goal:** Every module in LAB_SPEC �7 exists as a schema-valid YAML file, and M-A1's checkpoint is gradeable.

**Depends on:** T-025, T-017.

**Files:**
- create: `curriculum/modules/M-A1.yaml`, `M-A2.yaml`, `M-B1.yaml`, `M-B2.yaml`, `M-B3.yaml`, `M-C1.yaml`, `M-C2.yaml`, `M-C3.yaml`, `M-D1.yaml`, `M-D2.yaml`, `M-E1.yaml`, `M-F1.yaml`, `M-F2.yaml`, `tests/test_modules.py`, `tests/fixtures/M-A1.answers.yaml`

**Interfaces / schemas:**
- **Source fields:** `card_ids`, `lab_ids`, `conceptual`, and `level` are taken from LAB_SPEC �7.
- **`objective`:** begins `Can ` and names an observable capability.
- **Checkpoint:** ?3 deterministic items whose answers are derivable from the cards or ADR-011 formulas, and ?2 human_rubric lines.
- **`portfolio_artifact.path_pattern`:** `learner/portfolio/<MODULE_ID>/`.

M-A1 must include these items:
- `Q01` (numeric): accuracy drop when oracle=0.95 and d20_middle=0.80; answer 0.15, tolerance 0.001.
- `Q02` (mcq): which playbook step checks whether the information is in context; choices ["Step 1","Step 2","Step 5","Step 7"]; answer "Step 2".
- `Q03` (exact): the term for running the strongest model with oracle context; answer "ceiling test".

`tests/fixtures/M-A1.answers.yaml` holds the correct answers.

Test requirements:
- Every card appears in exactly one module.
- Module card IDs match TRACEABILITY card IDs (A-001.F-010 and C-019).
- Every `lab_ids` entry has a manifest.

**Steps:**
1. Author the files.
2. Write the tests.

**Acceptance tests:**
- `uv run aiu validate curriculum/modules` ? `validate: 13 files, 0 errors`, exit 0.
- `uv run aiu checkpoint grade M-A1 --answers tests/fixtures/M-A1.answers.yaml` ? `checkpoint: 3/3`, exit 0. Afterwards, delete `learner/checkpoints/M-A1.result.json`; it is not committed by this ticket.
- `uv run pytest tests/test_modules.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Card content.

**Open decisions:** none.

---

### T-029: Author level A cards A-002..A-010

**Goal:** All 10 level-A cards exist, validate, and pass provenance and traceability checks.

**Depends on:** T-026, T-027.

**Files:**
- create: `curriculum/A/A-002.yaml` . `curriculum/A/A-010.yaml` (9 files)
- modify: `PROVENANCE.md` (append rows only, for new P-### IDs if a card needs a claim not already seeded)

**Interfaces / schemas:**
- **Schema:** `card` in `schemas/curriculum.schema.json`.
- **`source_section` and `experiment_id`:** exactly as in the TRACEABILITY row.
- **Provenance:** carried from the source tag. Every S/K claim gets a `verify` item with `status: unverified`.
- **Card content:** each card has ?1 `when_it_fails` item, and any number in the card is written as "reported" or "claimed".
- **Card metadata:** `status: draft`, `version: 1.0.0`.

**Steps:**
1. Write the cards using the A-001 exemplar style.
2. Append any new ledger rows.
3. Run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/A` ? `validate: 10 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] Human content review is requested in the JOURNAL; cards stay `draft` until reviewed.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Marking claims verified.

**Open decisions:** none.

---

### T-030: Author level B cards B-002..B-014

**Goal:** All 14 level-B cards exist and pass all content checks.

**Depends on:** T-029.

**Files:**
- create: `curriculum/B/B-002.yaml` . `curriculum/B/B-014.yaml` (13 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:** The rules of T-029 apply. B-004 and B-005 have `experiment_id: null`, with `experiment_null_reason` copied from TRACEABILITY. B-006 `when_it_fails` must state that the "?7 labels" default is untested `[K]`, to be measured by E3.

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/B` ? `validate: 14 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-031: Author level C cards (18 remaining)

**Goal:** All 19 level-C cards (C-001..C-019, of which C-004 already exists) exist and pass all checks.

**Depends on:** T-030.

**Files:**
- create: `curriculum/C/C-001.yaml`, `C-002`, `C-003`, `C-005` . `C-019` (18 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- C-019 has `provenance: [ADD]`, `source_section: none`, and `add_justification` copied from TRACEABILITY.
- C-005 states the 33-41 point gap as "reported in one 2026 study (sourced, unverified)".
- C-018 lists the �7 failure catalog in `why_it_matters` or `tags`.

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/C` ? `validate: 19 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-032: Author level D and E cards

**Goal:** All 15 level-D and 7 level-E cards exist and pass all checks.

**Depends on:** T-031.

**Files:**
- create: `curriculum/D/D-001.yaml` . `D-015.yaml` (15 files), `curriculum/E/E-001.yaml` . `E-007.yaml` (7 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- D-004 states "five steps at 95% ? 77%" as arithmetic, which is computed and needs no verification. Its other claims remain unverified K.
- D-012 `experiment_null_reason` references `src/aiu/clients/openrouter.py`.
- E-006 notes "read-only in v1".

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/D curriculum/E` ? `validate: 22 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-033: Author level F cards and close traceability

**Goal:** All 75 cards exist, and `aiu traceability check --require-all` exits 0.

**Depends on:** T-032, T-028.

**Files:**
- create: `curriculum/F/F-001.yaml` . `F-010.yaml` (10 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- F-007 `when_it_fails` and `why_it_matters` reference the measured dev-machine profile: GTX 1060 6 GB, Pascal, no tensor cores, no bf16. This illustrates memory-bandwidth-bound decoding without requiring any run.
- F-010 states that local nanochat training is out of scope per the local-model policy.

**Steps:** Author the cards; run all checks.

**Acceptance tests:**
- `uv run aiu validate curriculum` ? `validate: 88 files, 0 errors`, exit 0. The count is 75 cards plus 13 modules.
- `uv run aiu traceability check --require-all` ? exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run pytest tests/test_modules.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` shows 75 cards; `status --check` passes.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-034: Write learner guide and M-A1 walkthrough

**Goal:** A learner can follow `docs/LEARNER_GUIDE.md` through module M-A1 using only repo commands.

**Depends on:** T-028, T-020, T-016.

**Files:**
- create: `docs/LEARNER_GUIDE.md`, `tests/test_learner_guide.py`

**Interfaces / schemas:** The guide has these sections, in order:
1. `## Setup`, covering `ops/bootstrap.ps1` and `.env`.
2. `## The learning loop`, covering prediction ? run ? post-mortem ? trust table.
3. `## Module M-A1 walkthrough`, with the exact LAB_SPEC �2 commands for E9, then `aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml`, then the portfolio artifact path.
4. `## Fixture mode practice`, the same loop with `--mode fixture`, clearly labeled "results are assumed, not measured".
5. `## Costs`, listing the assumed estimate and the $2 cap.
6. `## What the harness will refuse to do`, mapping exit codes 3-7.

Test requirement: every line in the guide's fenced code blocks that starts with `uv run aiu` must name a subcommand registered in `build_parser()`.

**Steps:** Write the guide and the test.

**Acceptance tests:**
- `uv run pytest tests/test_learner_guide.py` ? exit 0.

**Commands:** `uv run pytest tests/test_learner_guide.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Guides for other modules.

**Open decisions:** none.

---

### T-035: Implement repo-layout test and `aiu check-all`

**Goal:** One command runs every offline check, records test results in `status.json`, and enforces REPO_LAYOUT.md.

**Depends on:** T-024, T-026, T-027, T-033, T-034.

**Files:**
- create: `tests/test_layout.py`, `src/aiu/checkall.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**

`tests/test_layout.py` asserts four things:
1. The tracked top-level entries (`git ls-files` first path segment, plus `.runs` if present) are a subset of the REPO_LAYOUT.md tree.
2. Every directory under `labs/` matches the lab_id pattern.
3. `experiments/` contains only `_template` and lab_id dirs, and each run dir matches RUN_ID_RE with mode `live`.
4. `.runs/` is not tracked.

```python
CHECKS = [
  ["secrets-scan"], ["journal", "check"], ["validate"], ["labs", "check-tiers"],
  ["provenance", "check"], ["traceability", "check", "--require-all"],
  ["dataset", "build", "<each generator lab>", "--check"], ["fixtures", "synth", "<each runnable lab>", "--check"],
  ["smoke", "--mode", "fixture"],
]
def check_all(root: Path) -> int
  # runs CHECKS in-process via main(); then subprocess `uv run pytest` (inherits --disable-socket);
  # parses "N passed" / "M failed" from the pytest summary;
  # writes status.json.tests = {passed, failed, ran_at}; then status --write; then status --check;
  # prints "check-all: <k>/<total> checks OK"; returns 0 iff all are 0
```
CLI: `aiu check-all`.

**Steps:**
1. Implement.
2. Run it and fix any finding in the offending ticket's scope, recording each fix in the JOURNAL.

**Acceptance tests:**
- `uv run pytest tests/test_layout.py` ? exit 0.
- `uv run aiu check-all` ? last line `check-all: <n>/<n> checks OK`, exit 0.
- `uv run python -c "import json;t=json.load(open('status.json'))['tests'];assert t['failed']==0 and t['passed']>0"` ? exit 0.

**Commands:** `uv run aiu check-all`

**Definition of done:**
- [ ] JOURNAL entry appended, with the check-all output.
- [ ] `status.json.tests` is populated; README block is regenerated.

**Out of scope:** Live checks.

**Open decisions:** none.

---

### T-036: Pin models and prices, recompute expected costs, and run live smoke

**Goal:** Models and prices are pinned with dates, manifests carry pinned-pricing estimates, and one live smoke run completes under $5.00 (measured).

**Depends on:** T-035. Also blocked on human input: OD-01 and OD-02.

**Files:**
- modify: `config/models.yaml`, `config/pricing.yaml`, `labs/E2/manifest.yaml`, `labs/E4/manifest.yaml`, `labs/E5/manifest.yaml`, `labs/E9/manifest.yaml`, `labs/L-003/manifest.yaml`, `DECISIONS.md` (append ADR-024 recording the pinned IDs, prices, and date), `RESULTS.md`, `PROVENANCE.md` (append rows for pricing and OpenRouter usage, seed, and logprob behavior observed)
- create: `experiments/<lab_id>/<run_id>/.` for each smoke lab (committed, including failures)

**Interfaces / schemas:**
- **models.yaml:** the human-supplied IDs. judge_a.family must differ from judge_b.family, and cheap_a/b/c must be three distinct families. Add a test in `tests/test_config.py` asserting distinct families when nothing is UNPINNED.
- **pricing.yaml:** `retrieved_at` is the pinning date, and `models` holds one entry per pinned ID. Prices are sourced from the OpenRouter model page on that date.
- **Runnable manifests:** `expected_cost_usd` = the `aiu lab estimate` value; `cost_basis: estimated_from_pinned_pricing`.

**Steps:**
1. The human supplies IDs and prices. The implementer edits the configs and appends ADR-024.
2. `uv run aiu lab estimate <ID>` for each runnable lab; write the values into the manifests.
3. Set `$env:OPENROUTER_API_KEY` in the shell only.
4. `uv run aiu smoke --mode live`.
5. Add one RESULTS.md row per live run dir, with lesson `smoke run; no learner prediction`, and append the observed behavior to PROVENANCE as `unverified` or measured-for-our-setup rows.
6. `uv run aiu secrets-scan`, then `uv run aiu check-all`.

**Acceptance tests:**
- `uv run aiu lab estimate E9` ? no `basis=assumed`, exit 0.
- `uv run aiu smoke --mode live` ? last line ends `OK`, with `total_cost_usd` < 5.00, exit 0. If it exits 4 or 1, the run dirs are still committed and the ticket is returned as a spec defect with the JOURNAL entry.
- `uv run aiu status --check` ? exit 0. Every live run_id appears in RESULTS.md and the cumulative cost matches.
- `uv run aiu secrets-scan` ? exit 0.

**Commands:** as in Steps.

**Definition of done:**
- [ ] JOURNAL entry appended, with per-lab measured cost, total, and model IDs with date.
- [ ] README spend is updated via `status --write`.
- [ ] CHANGELOG entry added.

**Out of scope:** Learner-prediction runs (T-037); changing prompts to make tests pass.

**Open decisions:** OD-01 (model IDs), OD-02 (approval to spend up to $5.00 on live smoke).

---

### T-037: Complete module M-A1 end-to-end with a live E9 run

**Goal:** One full learning loop (prediction ? live E9 ? post-mortem ? trust-table row ? checkpoint ? portfolio ? learning write-up) exists in the repo with measured numbers.

**Depends on:** T-036, T-034.

**Files:**
- create: `experiments/E9/<run_id>/` (all 8 artifacts plus a filled `postmortem.md`), `learner/portfolio/M-A1/README.md`, `learner/checkpoints/M-A1.answers.yaml`, `learner/checkpoints/M-A1.result.json`, `docs/learnings/YYYY-MM-DD-e9-context-distractors.md`
- modify: `learner/trust_table.yaml` (one row for A-008 or A-001), `RESULTS.md`, `CHANGELOG.md`

**Interfaces / schemas:**
- **Trust row:** follows the `trust_row` schema. `my_replication` is set from `result.json.hypothesis_supported`: true ? `replicated`, false ? `failed_to_replicate`, null ? `inconclusive`. `run_ids` holds `[<run_id>]`.
- **Learning write-up:** follows `docs/learnings/_template.md`. Every number links to `experiments/E9/<run_id>/metrics.json` and `cost.json`.
- **Outcome logging:** negative or inconclusive outcomes are logged exactly as observed.

**Steps:** Follow docs/LEARNER_GUIDE.md "Module M-A1 walkthrough" verbatim. The human writes the prediction and post-mortem content, or explicitly delegates them and records the delegation in the JOURNAL.

**Acceptance tests:**
- `uv run aiu lab postmortem-check E9 --run-id <run_id>` ? `postmortem: OK`, exit 0.
- `uv run aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml` ? exit 0.
- `uv run aiu validate learner` ? exit 0.
- `uv run aiu status --check` ? exit 0.
- `uv run python -c "import json;assert json.load(open('experiments/E9/<run_id>/result.json'))['evidence_class']=='measured'"` ? exit 0.

**Commands:** LAB_SPEC �2 sequence with `E9`, then the commands above.

**Definition of done:**
- [ ] JOURNAL entry appended, with measured cost.
- [ ] RESULTS row added; CHANGELOG entry added.
- [ ] `status --write` done; `check-all` exits 0.

**Out of scope:** Other modules; editing the prediction after the run (forbidden).

**Open decisions:** OD-06 (whether the human or the implementer authors the learner prediction and post-mortem).

---

### T-038: Run final v1 acceptance

**Goal:** Every check in ACCEPTANCE.md passes from a clean checkout, and the result is recorded publicly.

**Depends on:** T-037.

**Files:**
- create: `docs/learnings/YYYY-MM-DD-v1-acceptance.md`
- modify: `README.md` (non-generated sections: the "what works / what doesn't" table must match ACCEPTANCE results), `CHANGELOG.md` (`v1.0.0`), `JOURNAL.md`, `status.json`

**Interfaces / schemas:** ACCEPTANCE.md AC-01..AC-20.

**Steps:**
1. `git clone` the repo into `C:\Users\Joe\Documents\Playground\aiu-accept`.
2. `
