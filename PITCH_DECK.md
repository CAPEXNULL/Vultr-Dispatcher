# Supply Dispatcher pitch deck

12-slide source. Cloud deployment verified on 2026-11-05; all demo data is synthetic.

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

## 3. A consistent choice with a checked outcome

Decision quality

- Each recommendation satisfies the declared order requirements.
- Identical offers produce the same calculated winner.
- Every approved action receives a durable record and independent readback.

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
- Eligibility checks keep the recommendation aligned with the order.

## 7. Every task has a bounded lifetime

Execution and containment

- Disposable Docker execution with no network or application secrets.
- 128 MiB RAM, 0.50 CPU, 64 processes, CPU and wall-clock limits.
- The infinite-loop demo confirms termination, cleanup and recovery.

## 8. Running on Vultr

Verified deployment - 5 November 2026

- Vultr VM: Python backend, SQLite ledger and Docker task runner.
- Vultr Serverless Inference: qwen3.8-flash-next explains the checked choice.
- Caddy serves public HTTPS. The browser workflow used real inference.

## 9. Approval leads to a checked record

Verifiable execution

- The host checks the sandbox optimum and mandatory constraints.
- Approval commits supplier, cost and ETA to the order ledger.
- A fresh connection reads back the result. Evidence records the outcome.

## 10. Evidence comes from executed checks

Reliability evidence

- 299 generated fresh-state workflow cases use an independent oracle.
- Separate HTTP, regression and real Docker tests check boundaries.
- Cloud checks separately verified HTTPS, inference and Docker recovery.

## 11. The buyer can explain and verify the choice

Business value

- The cloud sample selects SYNTH-A at 1,200 within a 1,500 budget.
- The cheaper offer arrives late. The faster feasible alternative costs 150 more.
- The buyer can compare the alternatives and confirm the verified saved result.

## 12. Public demo and recorded evidence

Verified deployment

- Public source: github.com/CAPEXNULL/Vultr-Dispatcher
- Demo: supply-dispatcher.80.240.28.98.sslip.io
- Approved orders survived service restart and VM reboot. Cloud workflow and containment recorded.
