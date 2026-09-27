# Local deployment

The supported deployment is a single-user, loopback-only demo with one FastAPI worker and the Vite frontend proxy. See the root README for executable commands and limits.

No authentication, tenant separation, durable job queue, automatic artifact expiry, or cloud deployment is implemented. CORS does not replace authentication. Multiple API workers would each own a separate GPU lock and are unsupported. A serialized request can still exhaust memory; use cropped or tiled images within the configured pixel limit.

For production, add an authenticated gateway, ownership checks on inputs and artifacts, a process-independent worker queue, job cancellation/timeouts, encrypted storage, and observability. These are deployment prerequisites, not existing features. No public deployment was performed.

The existing local Python environment was verified as Python 3.12.10 with PyTorch 2.14.0+cu130 and Transformers 5.17.0. The earlier sandbox launcher error did not establish that the environment was broken. Use requirements-lock.txt to identify the verified versions; CUDA wheel installation may require the corresponding PyTorch package index. Use npm ci for the frontend.

Artifacts are retained for reproducibility. The maintenance command previews files older than 30 days by default; only --apply deletes eligible generated files. This is an explicit local retention operation, not a background service.
