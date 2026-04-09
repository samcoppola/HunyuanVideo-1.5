#!/bin/bash
# TEST A — Generazione senza rewrite del prompt
# Il prompt viene passato direttamente al text encoder (Qwen2.5-VL-7B)
#
# CAMBIA IL PROMPT QUI:
PROMPT="A breathtaking sunset over the ocean, golden and crimson light reflecting on calm water"

source .venv/bin/activate

torchrun --nproc_per_node=1 generate.py \
    --model_path ./ckpts \
    --resolution 480p \
    --prompt "$PROMPT" \
    --cfg_distilled \
    --rewrite false \
    --sr false \
    --video_length 121 \
    --overlap_group_offloading false \
    --output_path ./outputs/test_no_rewrite.mp4
