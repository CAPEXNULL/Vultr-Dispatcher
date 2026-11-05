# lablab submission fields

Final English submission text and published material links. Adapt to the actual form field lengths.

## Project Title

Supply Dispatcher

## Short Description

A procurement recovery agent that compares alternative suppliers with deterministic constraints, requires buyer approval and verifies the saved order update.

## Long Description

Supply Dispatcher helps a buyer recover an order after a confirmed supplier delay. The buyer enters the current order, required quantity, budget, deadline and alternative supplier offers. The application prepares a decision plan and dispatches a reviewed solver into a disposable execution environment. The solver excludes offers that fail product, quantity, price or delivery requirements, then selects the lowest-cost eligible supplier with deterministic delivery-time and supplier-ID tie-breaks.

A separate oracle checks the selected optimum. Vultr Serverless Inference provides a concise explanation of the verified recommendation without choosing the supplier. The buyer reviews offer tables, metrics and charts, then explicitly approves the replacement. Only approval updates the application's SQLite order ledger. A fresh database connection reads back the committed supplier, cost and ETA before the result is marked verified. Repeated approval does not apply the same update twice.

Verified experience can avoid a redundant explanation only when its applicability conditions and the current optimum agree. It never bypasses current constraints or approval. The sandbox policy disables network access, excludes app secrets, caps CPU/RAM/processes and task duration, and destroys the environment after each run. The containment demonstration stops an intentional infinite loop and verifies that a subsequent task still succeeds.

Supply Dispatcher is deployed on Vultr with a public HTTPS application. Live inference, independent supplier selection, approval and readback, and automatic task cleanup and recovery were verified on 2026-11-05. The workflow gives the buyer a consistent comparison, clear reasoning and confirmation of the saved result.

## Technology Tags

Vultr, Vultr Serverless Inference, Python, Docker, SQLite, JavaScript, HTML, CSS, AI Agents, Procurement, Workflow Automation, Verification

## Category / Track

Challenge 2: Powering the Future of Work. Procurement and supplier disruption recovery. The application coordinates a multi-step workflow using deterministic supplier selection, AI explanations, buyer approval, durable updates and independent verification. Vultr Serverless Inference and Docker isolation support the deployed workflow.

## GitHub URL

https://github.com/CAPEXNULL/Vultr-Dispatcher

## Demo URL

https://supply-dispatcher.80.240.28.98.sslip.io

## Video URL

https://supply-dispatcher.80.240.28.98.sslip.io/media/Supply-Dispatcher-Demo-FullHD.mp4

Public watch page: https://supply-dispatcher.80.240.28.98.sslip.io/media/

Final narrated video: 1920x1080, 177.40 seconds, normal voice and playback speed. Actual ordered UI actions and visible clicks show the complete workflow.

## Pitch Deck

`output/pdf/Supply-Dispatcher-Pitch.pdf` (12 slides).

Public PDF: https://supply-dispatcher.80.240.28.98.sslip.io/media/Supply-Dispatcher-Pitch.pdf

## Cover Image

Use the owner-approved `output/media/Supply-Dispatcher-Cover.png`.

Public cover: https://supply-dispatcher.80.240.28.98.sslip.io/media/Supply-Dispatcher-Cover.png

## Architecture explanation

The Python orchestration backend runs on a Vultr VM. Each confirmed disruption dispatches the fixed supplier solver into a network-disabled disposable Docker container. The host independently checks the optimum, requests its English explanation through Vultr's OpenAI-compatible inference endpoint, and persists a proposal. A separate human approval action updates the local order ledger. A fresh connection verifies the durable result. Caddy terminates public HTTPS. A recorded public-browser workflow verified real inference and approval; separate recorded Docker execution verified containment and recovery.

## Use case

Autonomous alternative supplier selection and verified order recovery after a supply disruption.

## Business value

The buyer receives a consistent supplier comparison under explicit order requirements, a clear explanation of the best admissible option and control over the final approval. Independent readback confirms the saved result. Verified experience streamlines repeated cases while preserving fresh calculations. In the recorded case, the selected offer costs 1,200 within a 1,500 budget and arrives in four days against a five-day deadline.

## Submission status

Successfully submitted to the Vultr Agent Rush Hackathon. The participant supplied the platform success confirmation and the published project page on 2026-11-05. The final video and photo-backed PDF were uploaded; repository and application links were entered in the form.
