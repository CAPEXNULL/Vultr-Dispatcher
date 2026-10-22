# Optional artifact and audit tools

The backend requires only Python's standard library. The core acceptance suite requires pytest from `requirements.txt` and a running Docker engine.

- `python tools/audit_ui.py` requires `playwright` and its Chromium browser. Install using `python -m pip install playwright` and `python -m playwright install chromium`. It launches only its own headless test browser and a temporary local application on port 8013. It tests desktop/mobile controls, writes screenshots and verifies state after a restart.
- `python tools/build_pitch.py` requires `reportlab`, `pymupdf` and `Pillow`. It creates the 12-slide PDF, its Markdown source and temporary PNG renders for visual QA.
- `python tools/security_audit.py` scans the release and writes an explicit publication manifest. This pattern-based check complements manual review and does not promise detection of every possible secret format.
- `python tools/reproduce.py` runs a real Docker-backed workflow from a fresh exported release using isolated Python, then reads the committed order in a second process.
- `python containment_demo.py` demonstrates actual container policy, a stopped infinite loop, destruction and a subsequent successful task.

Reports do not establish deployment on Vultr. Repeat the public checks described in `deploy/DEPLOYMENT.md` after the service is actually provisioned.
