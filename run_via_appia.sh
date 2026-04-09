#!/bin/bash
# ============================================================
# Via Appia Antica — I2V 720p → SR 1080p, massima qualità
# Modelli richiesti:
#   python download.py base i2v-720p vision-encoder sr-1080p
# GPU minima: A100 40GB  (consigliata: A100 80GB)
# Tempo stimato: ~8-12 min su A100 40GB
# ============================================================
set -e

cd /workspace/HunyuanVideo-1.5
source /root/.venv/bin/activate

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY non impostata."
    echo "       export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

IMAGE_PATH="./appia_strada.png"
if [ ! -f "$IMAGE_PATH" ]; then
    echo "ERROR: immagine non trovata in $IMAGE_PATH"
    echo "       Carica appia_strada.png nella root del repo."
    exit 1
fi

mkdir -p ./outputs

# ── Parametri per massima qualità ───────────────────────────
# - 720p: risoluzione nativa 1280x720, poi SR porta a 1920x1080
# - 97 frames: ~6 secondi a 16fps (ottimale per confronto con Kling)
# - sr true: upscala a 1080p con il modello sr-1080p
# - enable_cache false: nessuna approssimazione deepcache/teacache
# - cfg_distilled: modello stabile a 50 step (default)
# - rewrite true: Claude riscrive il prompt in cinese (come il training)
# - overlap_group_offloading false: sicuro su A100 40GB
# ─────────────────────────────────────────────────────────────

PROMPT="Slow forward camera walk along the Via Appia Antica. The camera glides smoothly forward at eye level along the ancient cobblestone road, gently tilting left and right to observe the monumental Roman tombs. Distant Roman figures in tunics walk slowly ahead. Sparse vegetation sways lightly in the breeze. Cinematic, first-person perspective, photorealistic, no modern elements."

torchrun --nproc_per_node=1 generate.py \
    --model_path ./ckpts \
    --resolution 720p \
    --prompt "$PROMPT" \
    --image_path "$IMAGE_PATH" \
    --aspect_ratio 16:9 \
    --cfg_distilled \
    --num_inference_steps 50 \
    --video_length 97 \
    --sr true \
    --save_pre_sr_video \
    --rewrite true \
    --enable_cache false \
    --overlap_group_offloading false \
    --output_path ./outputs/via_appia_1080p.mp4

echo ""
echo "Done!"
echo "  Video 1080p: ./outputs/via_appia_1080p.mp4"
echo "  Video 720p pre-SR: ./outputs/via_appia_1080p_pre_sr.mp4"
