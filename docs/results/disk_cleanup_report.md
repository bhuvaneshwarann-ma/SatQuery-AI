# SatQuery AI — Disk Space Cleanup & Reclamation Report

**Cleanup Date**: 2026-09-20  
**Host System**: Windows 11  
**Target Drive**: `C:\`  
**Execution Objective**: Reclaim disk space from unused external software (Ollama, Android SDK/Studio) and temporary build/package caches without altering or modifying the SatQuery AI application, models, dependencies, or datasets.

---

## 1. Storage Before vs. After Cleanup

| Metric | Before Cleanup | After Complete Cleanup | Total Net Space Recovered |
| :--- | :---: | :---: | :---: |
| **Free Disk Space (`C:\`)** | **`290.28 GB`**<br>(311,683,407,872 bytes) | **`298.98 GB`**<br>(321,029,918,720 bytes) | **`+8.70 GB`**<br>(9,346,510,848 bytes) |

*(Note: Prior to cleanup, free space was ~290.28 GB; after safely purging Ollama, Android SDK, pip cache, npm cache, unlocked Windows Temp files, and browser cache data, free space reached **298.98 GB**).*

---

## 2. Granular Space Recovery by Category

| # | Cleanup Category | Path / Component | Space Recovered (MB) | Space Recovered (GB) | Cleanup Method / Status |
| :-: | :--- | :--- | :---: | :---: | :--- |
| 1 | **Ollama Installation & Models** | `%LOCALAPPDATA%\Programs\Ollama`<br>`%USERPROFILE%\.ollama` | **2,825.6 MB** | **`2.76 GB`** | Official InnoSetup uninstaller (`unins000.exe /VERYSILENT /NORESTART`) + config purge |
| 2 | **Android SDK** | `%LOCALAPPDATA%\Android\Sdk` | **1,720.3 MB** | **`1.68 GB`** | Purged emulator images, build-tools, platform-tools, sources, and download intermediates |
| 3 | **Android Studio Caches** | `%LOCALAPPDATA%\Google\AndroidStudio2026.1.4`<br>`%USERPROFILE%\.android`<br>`Start Menu\Android Studio` | **623.5 MB** | **`0.61 GB`** | Removed IDE caches, AVD configs, and orphaned Start Menu shortcuts |
| 4 | **Pip Installation Cache** | `%LOCALAPPDATA%\pip\cache` | **2,332.4 MB** | **`2.28 GB`** | Official `pip cache purge` (purged 1,335 wheels including 1.85 GB PyTorch CUDA wheel) |
| 5 | **NPM Package Cache** | `%LOCALAPPDATA%\npm-cache` | **1,006.9 MB** | **`0.98 GB`** | Official `npm cache clean --force` + cache directory cleanup |
| 6 | **Windows Temp Files** | `%LOCALAPPDATA%\Temp` | **1,497.7 MB** | **`1.46 GB`** | Safely unlinked 1,555 unlocked temporary files without force-deleting locked ones |
| 7 | **Browser Cache (Edge & Brave)** | `%LOCALAPPDATA%\Microsoft\Edge\...\Cache`<br>`%LOCALAPPDATA%\BraveSoftware\...\Cache` | **852.7 MB** | **`0.83 GB`** | Safely cleaned 3,460 cached web assets; strictly preserved bookmarks, passwords, and profiles |
| **Total** | **All Categories** | | **10,859.1 MB** | **`~10.60 GB` gross**<br>(**`+8.70 GB` net on C:)** | **100% SUCCESS** |

---

## 3. Detailed Actions & Execution Log

### A. Ollama Removal
- Verified SatQuery AI source code for `ollama`, `OLLAMA`, and `localhost:11434` $\rightarrow$ **0 occurrences**.
- Stopped active processes `ollama app.exe` (PID 22328) and `ollama.exe` (PID 23544).
- Executed official Windows uninstaller `unins000.exe`.
- Removed leftover directory `%USERPROFILE%\.ollama`.
- **Ollama Space Recovered**: **`2.76 GB`**.

### B. Android Studio & Android SDK Removal
- Verified SatQuery AI requirements $\rightarrow$ Web application (React 19 + TypeScript + FastAPI + PyTorch) with **zero Android dependencies**.
- Removed `%LOCALAPPDATA%\Android\Sdk` (including emulator binaries: 1,032 MB, sources: 212 MB, build-tools: 136 MB, platforms: 119 MB).
- Removed `%LOCALAPPDATA%\Google\AndroidStudio2026.1.4` (563 MB).
- Removed `%USERPROFILE%\.android` (AVD configs) and orphaned Start Menu shortcut.
- **Android Studio & SDK Space Recovered**: **`2.29 GB`** combined.

### C. Pip Cache Purge
- Executed `.venv\Scripts\pip cache purge`.
- Removed 1,335 cached wheel files and 2,204 directories.
- Did **NOT** touch `.venv` or any installed site-packages.
- **Pip Cache Space Recovered**: **`2.28 GB`**.

### D. NPM Cache Clean
- Executed `npm cache clean --force`.
- Purged downloaded tarballs in `%LOCALAPPDATA%\npm-cache`.
- Did **NOT** touch `frontend/node_modules/`, `package.json`, or `package-lock.json`.
- **NPM Cache Space Recovered**: **`0.98 GB`**.

### E. Windows Temporary Files Cleanup
- Examined **3,831** files in `%LOCALAPPDATA%\Temp`.
- Removed **1,555** unlocked, safe temporary files.
- Skipped **2,276** files actively in use or locked by active Windows background services (no force deletion).
- **Windows Temp Space Recovered**: **`1.46 GB`**.

### F. Browser Cache Cleanup
- Examined cache directories in Microsoft Edge and Brave Browser.
- Cleaned **1,369** files in Edge Cache (`416.56 MB`).
- Cleaned **2,091** files in Brave Cache (`436.16 MB`).
- Browsers were **NOT** force-closed.
- Bookmarks, passwords, history, extensions, cookies, and user profiles were strictly **preserved**.
- **Browser Cache Space Recovered**: **`0.83 GB`**.

---

## 4. SatQuery AI Application Health & Verification

Following cleanup, the SatQuery AI platform was thoroughly verified:

1. **Python Environment (`.venv`)**:
   - Python: `3.12.10`
   - PyTorch: `2.14.0+cu130` (CUDA `12.8` enabled)
   - GPU Hardware: `NVIDIA GeForce RTX 5050 Laptop GPU` active
   - Transformers: `5.17.0`
   - Torchvision: `0.29.0+cu130`
   - FastAPI: `0.141.1`
   - Status: **100% OPERATIONAL**

2. **AI Pretrained Model Weights**:
   - `remote-sensing-Qwen2.5-VL-3B-Instruct` (`~/.cache/huggingface/hub`): **7.58 GB INTACT**
   - `grounding-dino-tiny` (`~/.cache/huggingface/hub`): **658 MB INTACT**
   - `resnet18-f37072fd.pth` (`~/.cache/torch/hub/checkpoints`): **44.7 MB INTACT**

3. **FastAPI Backend Service**:
   - Endpoint `/api/health` returned `200 OK` (`{"status":"healthy","gpu_available":true}`).
   - Registered tools active: `VQA`, `GROUNDING`, `CHANGE_DETECTION`, `OPTICAL_SAR`.

4. **React Frontend Web Dashboard**:
   - `npm run build` completed in `189ms` with **0 errors**.
   - Node modules and build configuration intact.

5. **Datasets & Source Code**:
   - All sample images in `data/samples/` preserved.
   - All ground-truth evaluation pairs in `data/benchmarks/` preserved.
   - Working tree clean; zero source code files modified.

---

## 5. Files & Assets Intentionally Preserved

The following essential application assets were protected and untouched:
- `c:\Users\BHUVANESHWARAN N\Downloads\SatQuery-AI\.venv` (3.29 GB)
- `%USERPROFILE%\.cache\huggingface` (8.23 GB)
- `%USERPROFILE%\.cache\torch` (44.7 MB)
- `SatQuery-AI\data\samples` (4 demo preset assets)
- `SatQuery-AI\data\benchmarks` (LEVIR-CD and RSVQA test manifests)
- `SatQuery-AI\frontend\node_modules` (86.4 MB)
- `SatQuery-AI\ai`, `SatQuery-AI\backend`, `SatQuery-AI\frontend`, `SatQuery-AI\docs`
- `%USERPROFILE%\.gradle` (1.29 GB — preserved per safety constraint)

---

## 6. Final State Confirmation

```text
SatQuery AI source code: PRESERVED
SatQuery AI virtual environment: PRESERVED
Qwen model: PRESERVED
Grounding DINO: PRESERVED
ResNet-18 checkpoint: PRESERVED
Hugging Face models: PRESERVED
PyTorch/CUDA environment: PRESERVED
Frontend: PRESERVED
Backend: PRESERVED
```
