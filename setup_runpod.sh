#!/bin/bash
# =============================================================================
# RunPod Setup Script — HunyuanVideo 1.5  (I2V best quality)
# =============================================================================
# Run once after attaching the Network Volume to your pod.
# Usage:
#   bash setup_runpod.sh
#
# What it does:
#   1. Clones the repo (fork with all patches)
#   2. Creates a Python venv and installs dependencies
#   3. Downloads model weights: base + i2v-720p + vision-encoder + sr-1080p
#
# Requirements:
#   - Network Volume mounted at /workspace  (200 GB recommended)
#   - HuggingFace token in HF_TOKEN env var (Classic token, gated model access)
#     export HF_TOKEN="hf_..."
#   - HF access accepted for: black-forest-labs/FLUX.1-Redux-dev
#     (required for vision_encoder)
# =============================================================================

set -e  # Exit on error

WORKSPACE="/workspace"
REPO_DIR="$WORKSPACE/HunyuanVideo-1.5"
CKPTS_DIR="$REPO_DIR/ckpts"

echo "============================================================"
echo " HunyuanVideo 1.5 — RunPod Setup (I2V best quality)"
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

if ! command -v python3.11 &>/dev/null; then
    apt-get install -y python3.11 python3.11-venv
fi

PYTHON=python3.11

if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt

echo "    Dependencies installed."

# ── 3. Download model weights ─────────────────────────────────────
echo ""
echo "[3/4] Downloading model weights (~118 GB total)..."
echo "      base (~26 GB) + i2v-720p (~59 GB) + vision-encoder (~1 GB) + sr-1080p (~32 GB)"
echo "      This will take 15-30 minutes depending on your connection."

mkdir -p "$CKPTS_DIR"

# download.py gestisce ogni modello in modo modulare e salta quelli già presenti.
# vision-encoder richiede accesso HF a black-forest-labs/FLUX.1-Redux-dev.
"$REPO_DIR/.venv/bin/python" download.py base i2v-720p vision-encoder sr-1080p

# ── 4. Verify structure ───────────────────────────────────────────
echo ""
echo "[4/4] Verifying checkpoint structure..."

"$REPO_DIR/.venv/bin/python" - <<'PYEOF'
import os

base = "/workspace/HunyuanVideo-1.5/ckpts"
required = [
    "text_encoder",
    "vae",
    "scheduler",
    "transformer/720p_i2v_distilled",
    "vision_encoder/siglip/image_encoder",
    "transformer/1080p_sr_distilled",
]

all_ok = True
for path in required:
    full = os.path.join(base, path)
    status = "OK" if os.path.exists(full) else "MISSING"
    if status == "MISSING":
        all_ok = False
    print(f"  [{status}] {path}")

if all_ok:
    print("\nAll required files found. Ready for best-quality I2V!")
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
echo "  1. Carica appia_strada.png nella root del repo:"
echo "     /workspace/HunyuanVideo-1.5/appia_strada.png"
echo ""
echo "  2. Imposta la tua Anthropic API key:"
echo "     export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo ""
echo "  3. Lancia la generazione massima qualità:"
echo "     cd $REPO_DIR && bash run_via_appia.sh"
echo ""
echo "  Output: ./outputs/via_appia_1080p.mp4  (1080p con SR)"
echo "          ./outputs/via_appia_1080p_pre_sr.mp4  (720p originale)"
echo ""
echo "  Per altri task usa gli script run_t2v_*.sh / run_i2v_*.sh"
echo "  oppure scarica altri transformer con download.py"
echo "============================================================"
