#!/bin/bash
# TEST B — Generazione con rewrite del prompt via Claude API
# Il prompt viene prima riscritto da Claude (stesso system prompt di Tencent),
# poi passato al text encoder (Qwen2.5-VL-7B)
#
# CAMBIA IL PROMPT QUI (usa un prompt corto/semplice, ci pensa Claude a espanderlo):
PROMPT="A breathtaking sunset over the ocean, golden and crimson light reflecting on calm water"

# Imposta la tua API key Anthropic PRIMA di lanciare lo script:
#   export ANTHROPIC_API_KEY="sk-ant-..."
# Opzionale: cambia modello Claude (default: claude-sonnet-4-6)
# export ANTHROPIC_MODEL="claude-opus-4-6"

source .venv/bin/activate

python generate.py \
    --model_path ./ckpts \
    --resolution 480p \
    --prompt "$PROMPT" \
    --cfg_distilled \
    --rewrite true \
    --sr false \
    --video_length 121 \
    --overlap_group_offloading false \
    --output_path ./outputs/test_with_rewrite.mp4
