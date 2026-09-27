# Local deployment

The supported deployment is a single-user, loopback-only demo with one FastAPI worker and the Vite frontend proxy. See the root README for executable commands and limits.

No authentication, tenant separation, durable job queue, automatic artifact expiry, or cloud deployment is implemented. CORS does not replace authentication. Multiple API workers would each own a separate GPU lock and are unsupported. A serialized request can still exhaust memory; use cropped or tiled images within the configured pixel limit.

## Public deployment protection

The repository now includes a guarded single-worker public mode. Enable it only behind HTTPS and a reverse proxy:

```powershell
$env:PUBLIC_DEPLOYMENT="true"
$env:SATQUERY_API_KEY="generate-a-random-secret-at-least-32-characters"
$env:RATE_LIMIT_PER_MINUTE="12"
$env:ARTIFACT_RETENTION_HOURS="72"
$env:CORS_ORIGINS="https://your-frontend.example"
```

Build the frontend with the same key available as `VITE_API_KEY`, then serve `frontend/dist` and proxy `/api` to the one FastAPI worker. Public mode provides API-key authentication, per-key rate limiting, bounded request admission, request ownership metadata, protected artifact access, and startup artifact retention cleanup. Keep `--workers 1`; a process-independent GPU queue is still required before horizontal scaling.

For production, add an authenticated gateway, ownership checks on inputs and artifacts, a process-independent worker queue, job cancellation/timeouts, encrypted storage, and observability. These are deployment prerequisites, not existing features. No public deployment was performed.

The existing local Python environment was verified as Python 3.12.10 with PyTorch 2.14.0+cu130 and Transformers 5.17.0. The earlier sandbox launcher error did not establish that the environment was broken. Use requirements-lock.txt to identify the verified versions; CUDA wheel installation may require the corresponding PyTorch package index. Use npm ci for the frontend.

Artifacts are retained for reproducibility. The maintenance command previews files older than 30 days by default; only --apply deletes eligible generated files. This is an explicit local retention operation, not a background service.
