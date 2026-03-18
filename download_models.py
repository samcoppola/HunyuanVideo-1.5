import os
import subprocess

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import snapshot_download

HF_TOKEN = os.environ.get("HF_TOKEN", "")
CKPTS = "/workspace/HunyuanVideo-1.5/ckpts"

# ── 1. Download everything except the big transformer file ─────────
print("Scarico text_encoder, vae, scheduler, config...")
snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir=CKPTS,
    allow_patterns=[
        "config.json",
        "LICENSE",
        "NOTICE",
        "README*.md",
        "scheduler/**",
        "text_encoder/**",
        "vae/**",
        "transformer/480p_t2v_distilled/config.json",
    ],
)
print("Fatto.")

# ── 2. Download the big transformer with wget -c (resumable) ───────
transformer_dir = f"{CKPTS}/transformer/480p_t2v_distilled"
transformer_file = f"{transformer_dir}/diffusion_pytorch_model.safetensors"
os.makedirs(transformer_dir, exist_ok=True)

url = "https://huggingface.co/tencent/HunyuanVideo-1.5/resolve/main/transformer/480p_t2v_distilled/diffusion_pytorch_model.safetensors"

if os.path.exists(transformer_file):
    size = os.path.getsize(transformer_file)
    print(f"Transformer: {size / 1e9:.1f} GB gia' presenti, riprendo...")
else:
    print("Scarico transformer (33 GB) con resume...")

cmd = ["wget", "-c", "-O", transformer_file]
if HF_TOKEN:
    cmd += [f"--header=Authorization: Bearer {HF_TOKEN}"]
cmd.append(url)

result = subprocess.run(cmd)
if result.returncode == 0:
    print("Download completo.")
else:
    print(f"wget uscito con codice {result.returncode} — rilanciare lo script per riprendere.")
    exit(1)
