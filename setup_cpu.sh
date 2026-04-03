#!/bin/bash
# =============================================================================
# RunPod CPU Setup — clone + download  (NO GPU needed)
# =============================================================================
# Esegui su un pod CPU economico (~$0.02-0.05/h) prima di avviare la A100.
# Il Network Volume viene riempito qui; la A100 troverà già tutto pronto.
#
# Usage:
#   export HF_TOKEN="hf_..."
#   bash setup_cpu.sh
#
# Prerequisito HuggingFace:
#   Devi aver accettato i termini di black-forest-labs/FLUX.1-Redux-dev
#   sul tuo account HF prima di eseguire (serve per vision-encoder).
#
# Tempo stimato: 30-60 min (dipende dalla velocità di rete RunPod)
# Costo stimato: ~$0.02-0.05 totali su CPU pod
# =============================================================================

set -e

WORKSPACE="/workspace"
REPO_DIR="$WORKSPACE/HunyuanVideo-1.5"

echo "============================================================"
echo " HunyuanVideo 1.5 — CPU Setup (clone + download)"
echo "============================================================"

if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HF_TOKEN non impostato."
    echo "  export HF_TOKEN='hf_...'   (token Classic con accesso gated)"
    exit 1
fi

# ── 1. Clone repo ─────────────────────────────────────────────────
if [ ! -d "$REPO_DIR" ]; then
    echo "[1/3] Cloning repo..."
    cd "$WORKSPACE"
    git clone https://github.com/samcoppola/HunyuanVideo-1.5.git
else
    echo "[1/3] Repo già presente, pull..."
    cd "$REPO_DIR"
    git pull
fi
cd "$REPO_DIR"

# ── 2. Installa solo huggingface_hub nel Python di sistema ─────────
# Non creiamo il venv qui: torch richiederebbe CUDA per la versione GPU.
# Il venv completo viene creato dopo su GPU con setup_runpod.sh.
echo ""
echo "[2/3] Installo huggingface_hub nel Python di sistema..."
pip install -q huggingface_hub
echo "    OK."

# ── 3. Scarica modelli (~118 GB) ───────────────────────────────────
echo ""
echo "[3/3] Download modelli (~118 GB)..."
echo "      base (~26 GB) + i2v-720p (~59 GB)"
echo "      + vision-encoder (~1 GB) + sr-1080p (~32 GB)"
echo ""

python download.py base i2v-720p vision-encoder sr-1080p

# ── Done ──────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo " Download completato!"
echo "============================================================"
echo ""
echo "Prossimi passi:"
echo ""
echo "  1. Ferma questo pod CPU."
echo ""
echo "  2. Crea un pod A100 40GB (o 80GB) attaccando lo STESSO"
echo "     Network Volume."
echo ""
echo "  3. Sul pod A100:"
echo "     cd $REPO_DIR"
echo "     bash setup_runpod.sh      # crea venv + pip install (skip download)"
echo ""
echo "  4. Carica appia_strada.png via Jupyter in:"
echo "     $REPO_DIR/appia_strada.png"
echo ""
echo "  5. Genera:"
echo "     export ANTHROPIC_API_KEY='sk-ant-...'"
echo "     bash run_via_appia.sh"
echo "============================================================"
