#!/bin/bash
# ============================================================
# TEXT-TO-VIDEO — 480p
# Required models: base + t2v-480p
#   python download.py base t2v-480p
# ============================================================
set -e

cd /workspace/HunyuanVideo-1.5
source /root/.venv/bin/activate

# ── Edit these ───────────────────────────────────────────────
PROMPT="Your prompt here"
OUTPUT="./outputs/t2v_480p.mp4"
REWRITE=true        # true = Claude rewrites the prompt (needs ANTHROPIC_API_KEY)
VIDEO_LENGTH=33     # frames: 33 ≈ 2s | 65 ≈ 4s | 97 ≈ 6s
# ─────────────────────────────────────────────────────────────

if [ "$REWRITE" = "true" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

mkdir -p ./outputs

torchrun --nproc_per_node=1 generate.py \
    --model_path ./ckpts \
    --resolution 480p \
    --prompt "$PROMPT" \
    --cfg_distilled \
    --sr false \
    --rewrite $REWRITE \
    --video_length $VIDEO_LENGTH \
    --overlap_group_offloading false \
    --output_path "$OUTPUT"

echo "Done! Video saved to $OUTPUT"
