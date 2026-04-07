#!/usr/bin/env python3
"""
Fix script: scarica (o riscarica) transformer e upsampler SR 1080p.

Necessario quando:
  - transformer/1080p_sr_distilled è stato spostato per errore
  - upsampler/1080p_sr_distilled non era mai stato scaricato

Usage:
    export HF_TOKEN=hf_...
    python3 fix_sr.py
"""
import os
import sys

token = os.environ.get("HF_TOKEN")
if not token:
    print("ERROR: HF_TOKEN non impostato.")
    print("       export HF_TOKEN=hf_...")
    sys.exit(1)

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("huggingface_hub non trovato, installo...")
    os.system("pip install -q huggingface_hub")
    from huggingface_hub import snapshot_download

CKPTS = "./ckpts"
REPO = "tencent/HunyuanVideo-1.5"

print("==> Download transformer/1080p_sr_distilled ...")
snapshot_download(REPO, local_dir=CKPTS,
    allow_patterns=["transformer/1080p_sr_distilled/**"], token=token)

print("==> Download upsampler/1080p_sr_distilled ...")
snapshot_download(REPO, local_dir=CKPTS,
    allow_patterns=["upsampler/**"], token=token)

print()
print("Done! Verifica:")
for p in ["transformer/1080p_sr_distilled", "upsampler/1080p_sr_distilled"]:
    full = os.path.join(CKPTS, p)
    status = "OK" if os.path.exists(full) else "MISSING"
    print(f"  [{status}] {p}")
