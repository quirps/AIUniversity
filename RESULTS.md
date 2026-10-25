# RESULTS.md - Live run index

Cumulative spend: 0.1058 USD.

Every committed run in `experiments/<lab_id>/<run_id>/` gets exactly one row, including aborted and failed runs. Fixture runs (`.runs/`) are never listed here.

| run_id | lab | date | model (pinned ID @ date) | n items | status | headline metric (measured) | prediction held? | cost_usd | ledger rows | run dir |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261024T234653Z-live-4bc59b | L-003 | 2026-10-24 | none (0 calls) | 220 | completed | kappa=0.6466 | no (smoke) | 0.0000 | P-082 | experiments/L-003/20261024T234653Z-live-4bc59b |
| 20261024T234653Z-live-12e760 | E9 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | accuracy:oracle=0.00 (degenerate) | no (smoke) | 0.0239 | P-082, P-083 | experiments/E9/20261024T234653Z-live-12e760 |
| 20261024T234855Z-live-2669c1 | E2 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | accuracy:evidence_first=1.00 | no (smoke) | 0.0114 | P-082 | experiments/E2/20261024T234855Z-live-2669c1 |
| 20261024T235033Z-live-55f1d8 | E4 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | oot_error_drop=0.00 (degenerate) | no (smoke) | 0.0013 | P-082, P-083 | experiments/E4/20261024T235033Z-live-55f1d8 |
| 20261024T235228Z-live-142089 | L-003 | 2026-10-24 | none (0 calls) | 220 | completed | kappa=0.6466 | no (smoke) | 0.0000 | P-082 | experiments/L-003/20261024T235228Z-live-142089 |
| 20261024T235228Z-live-c603ef | E9 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | accuracy:oracle=0.00 (degenerate) | no (smoke) | 0.0239 | P-082, P-083 | experiments/E9/20261024T235228Z-live-c603ef |
| 20261024T235427Z-live-7c4fb9 | E2 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | accuracy:evidence_first=1.00 | no (smoke) | 0.0115 | P-082 | experiments/E2/20261024T235427Z-live-7c4fb9 |
| 20261024T235600Z-live-ff37c2 | E4 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | oot_error_drop=0.00 (degenerate) | no (smoke) | 0.0013 | P-082, P-083 | experiments/E4/20261024T235600Z-live-ff37c2 |
| 20261024T235642Z-live-abfd79 | E5 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | flip_rate=0.00 (degenerate) | no (smoke) | 0.0025 | P-082, P-083 | experiments/E5/20261024T235642Z-live-abfd79 |
| 20261024T235846Z-live-bcf012 | L-003 | 2026-10-24 | none (0 calls) | 220 | completed | kappa=0.6466 | no (smoke) | 0.0000 | P-082 | experiments/L-003/20261024T235846Z-live-bcf012 |
| 20261024T235846Z-live-6551ed | E9 | 2026-10-24 | deepseek-flash@2026-10-24 | 20 | completed | max_drop=0.20 | no (smoke) | 0.0216 | P-082, P-084 | experiments/E9/20261024T235846Z-live-6551ed |
| 20261025T000032Z-live-d7e9ff | E2 | 2026-10-25 | deepseek-flash@2026-10-24 | 20 | completed | accuracy:evidence_first=1.00 | no (smoke) | 0.0064 | P-082, P-084 | experiments/E2/20261025T000032Z-live-d7e9ff |
| 20261025T000147Z-live-c8fcce | E4 | 2026-10-25 | deepseek-flash@2026-10-24 | 20 | completed | oot_error_drop=1.00 | no (smoke) | 0.0007 | P-082, P-084 | experiments/E4/20261025T000147Z-live-c8fcce |
| 20261025T000229Z-live-70b504 | E5 | 2026-10-25 | deepseek-flash@2026-10-24 | 20 | completed | flip_rate=0.50 | no (smoke) | 0.0016 | P-082, P-084 | experiments/E5/20261025T000229Z-live-70b504 |

The first two smoke attempts ran with DeepSeek thinking mode enabled. The
max_tokens-limited labs returned empty content, so their `accuracy` and
`oot_error_drop` values are degenerate and are marked as such. The third attempt
(`20261024T235846Z` through `20261025T000229Z`) disabled thinking mode and is the
usable smoke set. One earlier E5 attempt (`20261024T235117Z-live-1b0f23`) was
interrupted by a shell timeout and removed before commit; its cost was not
recorded. The committed cumulative cost above includes every remaining run
directory.
