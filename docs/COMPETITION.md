# Competition mapping - checked 5 November 2026

Primary source: [Official Vultr Agent Rush brief](https://lablab.build/ai-hackathons/vultr-hackathon).

## Selected submission track

**Challenge 2: Powering the Future of Work.** The brief explicitly accepts multi-step agentic or rule-based enterprise workflows and lists procurement, vendor comparison and following up on delays as use cases. Supply Dispatcher implements supplier recovery with deterministic comparison, independent verification, AI explanation, buyer approval and a saved order update.

This is the prepared submission choice. The authenticated lablab form has not yet been updated or submitted; that platform state must be confirmed separately.

## Requirement mapping

| Requirement | Implementation / evidence |
| --- | --- |
| Public web application | HTTPS interface with order entry, supplier offers, analytics, approval and Evidence |
| Vultr VM backend | Existing Vultr VM runs Python orchestration, SQLite and Docker |
| Realistic multi-step workflow | Analyze disruption, compare eligible suppliers, verify choice, explain, approve, commit and read back |
| Vultr central orchestration | Backend controls solver dispatch, inference, decision state and persistence |
| Public repository and setup | CAPEXNULL/Vultr-Dispatcher, README and deploy/DEPLOYMENT.md |
| Public application URL | https://supply-dispatcher.80.240.28.98.sslip.io |
| Recorded video | Public /media/Supply-Dispatcher-Demo-FullHD.mp4; 177.40 seconds, visible real actions |
| Architecture and use case | README, docs/ARCHITECTURE.md and SUBMISSION.md |
| Cover and slide presentation | Approved cover and redesigned 12-slide photo-backed PDF, both published |
| Official platform submission | Pending authenticated lablab form access and final submission confirmation |

Vultr Serverless Inference is optional for Challenge 2; this project already uses it. Docker containment and recorded timeout/cleanup/recovery remain implemented features. They do not change the selected business-workflow track.

The event brief does not prescribe a minimum number of test runs, load tests or paid model calls. Saved acceptance evidence includes 333 local tests and 299 independently generated workflow scenarios. Separate cloud evidence verifies live inference, public UI approval, durable readback, service restart, VM reboot and real Docker containment. Historical local reports retain their original context; reports/final-readiness.json is the current pre-submission check.

No new terms or eligibility declarations were accepted during this track/documentation update. Event dates are 3-8 November 2026; verify the actual deadline in the authenticated form before submission.
