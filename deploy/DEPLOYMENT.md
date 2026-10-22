# Vultr VM deployment

Status: prepared, not yet deployed. A Vultr API credential or an identified Vultr VM with SSH access, an inference key/model and a DNS name are required. Never infer a provider from an unrelated SSH entry.

Use a clean Ubuntu VM on Vultr with Docker, Python 3.11+ and Caddy from their official repositories. Open ports 80/443, restrict SSH to the operator, and keep 8003 bound to loopback. Point the demo domain's DNS A record to this VM.

1. Clone the public release to `/opt/supply-dispatcher` and check out its reviewed commit.
2. Create system user `supply-dispatcher` and add it to the Docker group. The Docker group grants host-level control. Only the trusted backend may access that socket, and it must never be mounted into a task container. Use a dedicated demo VM with synthetic data.
3. Pull `python:3.13-slim`, record the digest and set `SANDBOX_IMAGE` to the digest for repeatability. No Python runtime dependencies are needed by the backend.
4. Copy `.env.example` to `/etc/supply-dispatcher.env` owned by root, mode 0600. Set the real inference key/model. EnvironmentFile is loaded by systemd, not by the application. Do not commit this file.
5. Copy `deploy/supply-dispatcher.service` to `/etc/systemd/system/`. Create `/var/lib/supply-dispatcher` owned by the service user. Run `systemctl daemon-reload` and `systemctl enable --now supply-dispatcher`.
6. Set `DEMO_DOMAIN` in Caddy's systemd environment, install `deploy/Caddyfile` as `/etc/caddy/Caddyfile`, validate it with `caddy validate`, then restart Caddy. Caddy obtains a publicly trusted certificate when DNS and ports are correct.
7. Access the HTTPS URL. Run analysis, approve, read back `/api/order/PO-1042`, and save the trace. Confirm the response reports `inference_source=vultr-serverless-inference` for a new order without applicable experience.
8. Run `python3 containment_demo.py` on the VM with Docker access. Save the observed cgroup limits and cleanup evidence. This CLI is intentionally not an unauthenticated HTTP endpoint.
9. Restart the service. Confirm `/health` and that the approved order survives. Reboot the VM and repeat. Record URL, VM identifier/provider evidence, commit, image digest, time and outcomes in the deployment report.
10. Repeat UI checks through HTTPS and ensure no keys appear in page source, network responses, logs, trace records or artifacts. Keep the real key only in the protected service environment.

The app updates its own durable SQLite order ledger. It does not contact a supplier, issue a purchase order in an ERP or spend money. The public demo has shared synthetic state and is not a multi-tenant production procurement service. A production integration requires authentication, authorization, event revisions and an ERP adapter.

Docker provides process isolation, not a VM-grade defense against kernel exploits. Task code is the fixed, reviewed solver and cannot be supplied by HTTP clients. The timeout cleanup uses the Docker daemon and removes the named container even if the Docker client times out.
