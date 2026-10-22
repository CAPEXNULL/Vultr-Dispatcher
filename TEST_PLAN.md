# Frozen acceptance plan

Frozen before the final acceptance run, 22 October 2026.

1. Run original regression tests and audit all five original UI variants. Ship only the localhost:8003 variant.
2. Run the release regression, input validation, event invalidation, persistent state, repeated approval and independent verification tests.
3. Execute exactly 299 deterministic generated scenarios. Each uses a fresh database and an oracle that enumerates non-dominated feasible offers without importing production decision functions. Cover budget, quantity, deadline, product, ties, no solution, repeated events/approvals and accepted/rejected experience reuse. All scenarios run actual fresh Python subprocesses. This is functional evidence, not a claim of Docker containment for those 299 runs.
4. Exercise real Docker solver execution, a resource/time limit demonstration, secret exclusion, observed cgroup limits, container destruction and a subsequent healthy run.
5. Run HTTP API E2E including persisted order readback, invalid requests, origin rejection and traversal prevention.
6. Audit every frontend control, English copy and desktop/mobile layout. Table, Metrics and Charts must contain different representations of the same data. Save screenshots.
7. Scan the explicit release file set for credentials, local paths, databases, caches and proprietary reference documents. Audit the Git publication set.
8. Reproduce from a clean release export with documented dependencies. Restart the server and verify state persistence.
9. After the first local acceptance PASS, stop implementation changes and publish the reviewed release to the new public Vultr-Dispatcher repository. Verify the remote files and visibility.
10. Deploy that revision to a Vultr VM, configure real Serverless Inference, HTTPS and Docker. Repeat the complete public E2E, containment and cold restart checks. Do not equate local PASS with overall PASS.

Critical failure: record cause, apply a local correction, recheck. Maximum three correction cycles per cause. Then repeat the complete applicable plan. Stop improvements after the first full PASS. Missing credentials or infrastructure are BLOCKED, never PASS. GitHub/public-deployment checks necessarily follow local acceptance because the requested publication order forbids earlier publication.
