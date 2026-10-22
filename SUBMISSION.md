# lablab submission fields

Prepared in English. Do not submit until the pending infrastructure and video fields are complete. Actual form length limits may require shortening these drafts.

## Project Title

Supply Dispatcher

## Short Description

A procurement recovery agent that compares alternative suppliers with deterministic constraints, requires buyer approval and verifies the saved order update.

## Long Description

Supply Dispatcher helps a buyer recover an order after a confirmed supplier delay. The buyer enters the current order, required quantity, budget, deadline and alternative supplier offers. The application prepares a decision plan and dispatches a reviewed solver into a disposable execution environment. The solver excludes offers that fail product, quantity, price or delivery requirements, then selects the lowest-cost eligible supplier with deterministic delivery-time and supplier-ID tie-breaks.

A separate oracle checks the selected optimum. Vultr Serverless Inference provides a concise explanation of the verified recommendation without choosing the supplier. The buyer reviews offer tables, metrics and charts, then explicitly approves the replacement. Only approval updates the application's SQLite order ledger. A fresh database connection reads back the committed supplier, cost and ETA before the result is marked verified. Repeated approval does not apply the same update twice.

Verified experience can avoid a redundant explanation only when its applicability conditions and the current optimum agree. It never bypasses current constraints or approval. The sandbox policy disables network access, excludes app secrets, caps CPU/RAM/processes and task duration, and destroys the environment after each run. The containment demonstration stops an intentional infinite loop and verifies that a subsequent task still succeeds.

This release is a synthetic procurement demonstration. It does not contact suppliers, place real purchase orders or claim measured customer savings. Local tests and containment evidence are available in the repository. Vultr deployment, live model calls and the public HTTPS demo remain pending until account and inference access are configured and verified.

## Technology Tags

Vultr, Vultr Serverless Inference, Python, Docker, SQLite, JavaScript, HTML, CSS, AI Agents, Procurement, Workflow Automation, Verification

## Category / Track

Challenge 1: Blast Radius Zero. Pattern A: sandboxed code execution with a fixed reviewed solver. Procurement is the business use case. The code does not claim autonomous generation of arbitrary programs.

## GitHub URL

https://github.com/CAPEXNULL/Vultr-Dispatcher

## Demo URL

PENDING: public HTTPS endpoint on an identified Vultr VM. Do not use localhost as a submitted demo URL.

## Video URL

PENDING: record and upload the demonstration using VIDEO_SCRIPT.md after cloud verification.

## Pitch Deck

`output/pdf/Supply-Dispatcher-Pitch.pdf` (12 slides).

## Cover Image

Use `docs/screenshots/current-order.png` or the approved release banner `static/v3-banner.jpg`. The banner comes from the selected existing interface. No new third-party image was added.

## Architecture explanation

A Vultr VM is the deployment target for the Python orchestration backend. Each confirmed disruption dispatches the fixed supplier solver into a network-disabled disposable Docker container. The host independently checks the optimum, requests its English explanation through Vultr's OpenAI-compatible inference endpoint, and persists a proposal. A separate human approval action updates the local order ledger. A fresh connection verifies the durable result. Caddy terminates public HTTPS. Deployment is prepared but not yet attested by cloud evidence.

## Use case

Autonomous alternative supplier selection and verified order recovery after a supply disruption.

## Business value

The buyer receives an explicit comparison under the same constraints, avoids approving an infeasible supplier and can inspect whether the intended update actually persisted. The synthetic sample selects an eligible offer 5,000 below its 120,000 budget. Customer time savings, production ROI and reductions in real supply delays have not been measured.

## Participant actions

Log into or register on lablab.ai, enroll in the event and required Discord, complete any identity/eligibility declarations and accept applicable terms personally. Verify final event rules and timing, add actual demo and video URLs, upload the PDF/cover image, review all claims and submit. An uploaded video file alone is not a public video URL. The agent has not enrolled, accepted terms or filed a final competition submission.
