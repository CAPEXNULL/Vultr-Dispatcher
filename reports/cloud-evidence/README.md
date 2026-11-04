# Verified cloud recordings

Recorded on 2026-11-05 against the existing Vultr VM. All input data is synthetic.

- `Supply-Dispatcher-Cloud-Workflow.mp4`: actual 1920×1080 browser workflow over verified public HTTPS, including live Vultr inference and approval. No accelerated playback or narration.
- `Supply-Dispatcher-Cloud-Containment.mp4`: readable presentation of recorded remote execution, replaying the observed timing. Shows the deliberately looping task, timeout, container cleanup and next-task recovery. `containment-live.json` preserves timed raw output and full observed evidence. The original raw browser recording is also retained as `Supply-Dispatcher-Cloud-Containment.webm`.
- `public-ui-check.json`: actual browser analysis/approval response and TLS evidence.

The final narrated edited demonstration is `output/media/Supply-Dispatcher-Demo-FullHD.mp4`. It uses these original cloud sources and readable high-DPI views of the unchanged recorded response. No public video URL or final competition submission is created by these local files.

Publication note: JSON evidence is included in the repository. Original raw source recordings are retained locally for provenance; the final edited recording is publicly available at https://supply-dispatcher.80.240.28.98.sslip.io/media/Supply-Dispatcher-Demo-FullHD.mp4 .
