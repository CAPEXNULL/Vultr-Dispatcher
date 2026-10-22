# Acceptance corrections

Before final acceptance:

- Full request fingerprints replace selection-only identifiers. Changed order conditions invalidate pending approvals. Verified repeated events preserve the saved decision instead of resetting it.
- Invalid non-finite amounts, fractional integral fields and duplicate supplier identifiers are rejected without changing the declared optimization objective.
- A separate comparison implementation verifies the optimum. A fresh SQLite connection verifies committed order state.
- Docker timeout cleanup explicitly removes the named container. The development fallback uses a subprocess and makes no containment claim.
- Static file resolution rejects traversal outside the static directory.

Containment test correction cycle 1: an initial overly broad environment-name check classified the official Python image's public GPG_KEY as an application credential. Actual image inspection showed it is a public distribution verification key. The test now checks application credential namespaces and reports the observed environment names. The host application-key sentinel remains excluded. The standalone recheck passed. No sandbox policy was relaxed.

The first exploratory release run completed 299 workflow cases successfully but had this one containment-test assertion failure. That run is not the final acceptance result. The complete final plan is rerun after corrections and remaining HTTP/UI/material checks.
