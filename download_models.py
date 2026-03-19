import os
import subprocess

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import snapshot_download

HF_TOKEN = os.environ.get("HF_TOKEN", "")
CKPTS = "/workspace/HunyuanVideo-1.5/ckpts"

# ── 1. Download vae, scheduler, config from HunyuanVideo-1.5 ──────
print("Scarico vae, scheduler, config...")
snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir=CKPTS,
    allow_patterns=[
        "config.json",
        "LICENSE",
        "NOTICE",
        "README*.md",
        "scheduler/**",
        "vae/**",
        "transformer/480p_t2v_distilled/config.json",
    ],
)
print("Fatto.")

# ── 2. Download byt5-small (~1.2 GB) ──────────────────────────────
byt5_marker = f"{CKPTS}/text_encoder/byt5-small/config.json"
if os.path.exists(byt5_marker):
    print("byt5-small gia' presente, salto.")
else:
    print("Scarico byt5-small (~1.2 GB)...")
    snapshot_download(
        repo_id="google/byt5-small",
        local_dir=f"{CKPTS}/text_encoder/byt5-small",
    )
    print("byt5-small scaricato.")

# ── 3. Download Qwen2.5-VL-7B-Instruct (text encoder LLM, ~21 GB) ─
llm_marker = f"{CKPTS}/text_encoder/llm/config.json"
if os.path.exists(llm_marker):
    print("text_encoder/llm gia' presente, salto.")
else:
    print("Scarico Qwen2.5-VL-7B-Instruct (~21 GB)...")
    snapshot_download(
        repo_id="Qwen/Qwen2.5-VL-7B-Instruct",
        local_dir=f"{CKPTS}/text_encoder/llm",
    )
    print("LLM scaricato.")

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
    print("Transformer scaricato.")
else:
    print(f"wget uscito con codice {result.returncode} — rilanciare lo script per riprendere.")
    exit(1)

# ── 3. Download Glyph-SDXL-v2 (byT5 glyph model) from ModelScope ──
glyph_dir = f"{CKPTS}/text_encoder/Glyph-SDXL-v2"
glyph_marker = f"{glyph_dir}/checkpoints/byt5_model.pt"

if os.path.exists(glyph_marker):
    print("Glyph-SDXL-v2 gia' presente, salto.")
else:
    print("Scarico Glyph-SDXL-v2 da ModelScope...")
    from modelscope import snapshot_download as ms_download
    ms_download("AI-ModelScope/Glyph-SDXL-v2", local_dir=glyph_dir)
    print("Glyph-SDXL-v2 scaricato.")

print("Download completo.")
