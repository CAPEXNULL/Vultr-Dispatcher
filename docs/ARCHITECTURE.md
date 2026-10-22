# Architecture and trust boundaries

The browser sends a structured disruption event. The backend validates finite values, integral quantities/dates and unique supplier identifiers, invalidates old pending recommendations when order conditions change, and prepares a fixed task plan.

The runner copies the standalone solver and order JSON into a disposable directory. Docker sees only that directory. It has no network, application environment, database, app source tree or Docker socket. A container produces `output.json`. The backend hashes the artifact and a separately implemented oracle checks its optimum and feasibility.

Vultr Serverless Inference receives the order data and verified selection to write a short English explanation. All calls use the fixed Vultr endpoint. Inference cannot modify the optimizer result. Applicable experience can reuse a deterministic explanation only after a new current comparison agrees.

A proposal enters SQLite. Human approval is a separate API action. It revalidates the selected offer, commits the local order update, opens a new connection to read back supplier/cost/ETA, records verification and saves successful experience. A process lock serializes transitions within this single backend process. Run one backend process per database. Multi-host orchestration and real supplier transactions are outside this release.

The UI shows business decisions, analytics, approval and evidence. Operator-only documentation explains sandbox policy and hashes. The API trace exists to audit decisions but contains synthetic order data, never API keys.

Security boundaries are intentionally explicit: local development subprocesses are not secure sandboxes, Docker shares the VM kernel, the backend Docker group is privileged, and a public synthetic demo is not an authenticated enterprise service. The competition VM deployment and HTTPS reverse proxy are described in `deploy/` and remain unverified until executed on an identified Vultr VM.
