#!/bin/bash
# =============================================================================
# RunPod Setup Script — HunyuanVideo 1.5
# =============================================================================
# Run once after attaching the Network Volume to your pod.
# Usage:
#   bash setup_runpod.sh
#
# What it does:
#   1. Clones the repo (fork with all patches)
#   2. Creates a Python venv and installs dependencies
#   3. Downloads model weights from HuggingFace
#
# Requirements:
#   - Network Volume mounted at /workspace
#   - HuggingFace token in HF_TOKEN env var (for gated models)
#     export HF_TOKEN="hf_..."
# =============================================================================

set -e  # Exit on error

WORKSPACE="/workspace"
REPO_DIR="$WORKSPACE/HunyuanVideo-1.5"
CKPTS_DIR="$REPO_DIR/ckpts"
HF_REPO="tencent/HunyuanVideo-1.5"

echo "============================================================"
echo " HunyuanVideo 1.5 — RunPod Setup"
echo "============================================================"

# ── 1. Clone repo ────────────────────────────────────────────────
if [ ! -d "$REPO_DIR" ]; then
    echo "[1/4] Cloning repo..."
    cd "$WORKSPACE"
    git clone https://github.com/samcoppola/HunyuanVideo-1.5.git
else
    echo "[1/4] Repo already exists, pulling latest changes..."
    cd "$REPO_DIR"
    git pull
fi

cd "$REPO_DIR"

# ── 2. Create venv and install dependencies ───────────────────────
echo ""
echo "[2/4] Setting up Python virtual environment..."

# Ensure python3-venv is available (missing on many RunPod base images)
if ! python3 -m venv --help &>/dev/null; then
    apt-get install -y python3-venv
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "    Dependencies installed."

# ── 3. Download model weights ─────────────────────────────────────
echo ""
echo "[3/4] Downloading model weights (~58 GB for T2V 480p distilled)..."
echo "      This will take several minutes depending on your connection."

mkdir -p "$CKPTS_DIR"

# Use huggingface_hub Python API for reliable large-file downloads
python3 - <<'PYEOF'
import os
from huggingface_hub import snapshot_download

repo_id = "tencent/HunyuanVideo-1.5"
local_dir = os.environ.get("CKPTS_DIR", "/workspace/HunyuanVideo-1.5/ckpts")
token = os.environ.get("HF_TOKEN", None)

# Download everything EXCEPT transformer variants we don't need yet.
# Edit this list to add more variants later.
ignore_patterns = [
    # Skip transformer variants not needed for the first T2V test.
    # Remove lines below when you want those variants.
    "transformer/720p_t2v/*",
    "transformer/720p_t2v_distilled/*",
    "transformer/480p_i2v/*",
    "transformer/480p_i2v_distilled/*",
    "transformer/480p_i2v_step_distilled/*",
    "transformer/720p_i2v/*",
    "transformer/720p_i2v_distilled/*",
    # Skip SR upsampler for now (only needed with --sr true)
    "upsampler/*",
    # Skip vision encoder (only needed for I2V tasks)
    "vision_encoder/*",
    # Skip large binary assets folder
    "assets/*",
]

print(f"Downloading to: {local_dir}")
print("Included: text_encoder, vae, scheduler, transformer/480p_t2v_distilled")
print("Skipped:  720p variants, I2V variants, upsampler, vision_encoder")
print()

snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    ignore_patterns=ignore_patterns,
    token=token,
    local_dir_use_symlinks=False,
)

print("Download complete!")
PYEOF

# ── 4. Verify structure ───────────────────────────────────────────
echo ""
echo "[4/4] Verifying checkpoint structure..."

python3 - <<'PYEOF'
import os

base = "/workspace/HunyuanVideo-1.5/ckpts"
required = [
    "text_encoder",
    "vae",
    "scheduler",
    "transformer/480p_t2v_distilled",
]

all_ok = True
for path in required:
    full = os.path.join(base, path)
    status = "OK" if os.path.exists(full) else "MISSING"
    if status == "MISSING":
        all_ok = False
    print(f"  [{status}] {path}")

if all_ok:
    print("\nAll required files found. Ready to generate!")
else:
    print("\nSome files are missing. Check the download logs above.")
PYEOF

# ── Done ──────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo " Setup complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Set your Anthropic API key:"
echo "     export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo ""
echo "  2. Run test WITHOUT prompt rewriting:"
echo "     cd $REPO_DIR && bash test_no_rewrite.sh"
echo ""
echo "  3. Run test WITH Claude prompt rewriting:"
echo "     cd $REPO_DIR && bash test_with_rewrite.sh"
echo "     (edit the PROMPT and ANTHROPIC_API_KEY inside first)"
echo ""
echo "  4. Run the conversational Video Subagent:"
echo "     cd $REPO_DIR && source .venv/bin/activate"
echo "     python video_subagent.py"
echo "     # or: python video_subagent.py --auto \"video di un vecchio che fuma la pipa\""
echo ""
echo "  Output videos will be saved to: $REPO_DIR/outputs/"
echo ""
echo "  To download more model variants later (720p, I2V, etc.),"
echo "  edit the ignore_patterns in this script and run it again."
echo "============================================================"
