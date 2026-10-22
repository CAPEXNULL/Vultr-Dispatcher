# Supply Dispatcher pitch deck

12-slide source. Local evidence and pending cloud work are stated separately.

## 1. Supply Dispatcher

Verified recovery after a supplier delay

- Deterministic supplier comparison
- Buyer approval before the order changes
- A saved result with independent verification

## 2. A delayed supplier puts the order at risk

Procurement disruption

- A buyer must compare price, quantity, product and delivery at once.
- The cheapest offer can fail a mandatory requirement.
- An explanation alone does not recover the order.

## 3. Fluent text cannot prove feasibility

The weakness of LLM-only selection

- A recommendation must satisfy every declared order constraint.
- Identical offers should produce an identical winner.
- An approved action needs a durable record and a checked outcome.

## 4. Calculation chooses. Inference explains.

Our approach

- A fixed solver compares the current offers in an isolated container.
- An independent implementation checks the optimum.
- Vultr inference explains the checked choice. The buyer approves it.

## 5. One disruption, one reviewable workflow

Product workflow

- Enter the delayed order and supplier alternatives.
- Review the plan, recommendation and three analytics views.
- Approve the replacement and inspect the verified saved result.

## 6. The selection rule is explicit

Deterministic mathematical decision layer

- Product matches. Quantity covers the order. Cost and ETA fit the limits.
- Minimize cost, then ETA, then supplier ID for an exact tie.
- No feasible offer means no replacement and no order update.

## 7. Every task has a bounded lifetime

Execution and containment

- Disposable Docker execution with no network or application secrets.
- 128 MiB RAM, 0.50 CPU, 64 processes, CPU and wall-clock limits.
- The infinite-loop demo confirms termination, cleanup and recovery.

## 8. Vultr is the planned control plane

Deployment architecture

- Vultr VM: Python backend, SQLite ledger and Docker task runner.
- Vultr Serverless Inference: OpenAI-compatible explanation calls.
- Caddy: public HTTPS. Cloud deployment and live inference are pending.

## 9. Approval leads to a checked record

Verifiable execution

- The host checks the sandbox optimum and mandatory constraints.
- Approval commits supplier, cost and ETA to the order ledger.
- A fresh connection reads back the result. Evidence records the outcome.

## 10. Evidence comes from executed checks

Reliability evidence

- 299 generated fresh-state workflow cases use an independent oracle.
- Separate HTTP, regression and real Docker tests check boundaries.
- Recorded local evidence does not establish a public cloud deployment.

## 11. The buyer can explain and verify the choice

Business value

- The sample selects SUP-A at 115,000 within a 120,000 budget.
- SUP-C fails quantity. Faster SUP-B costs more under the fixed objective.
- The sample is synthetic. Customer ROI and time savings are unmeasured.

## 12. From recommendation to verified recovery

Demo and completion

- Public source: github.com/CAPEXNULL/Vultr-Dispatcher
- Next: verify Vultr deployment, live inference and the HTTPS workflow.
- Record the containment moment, upload the video and submit on lablab.
