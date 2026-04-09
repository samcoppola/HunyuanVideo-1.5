#!/bin/bash
source .venv/bin/activate
torchrun --nproc_per_node=1 generate.py \
    --model_path ./ckpts \
    --resolution 480p \
    --prompt "Un paesaggio al tramonto" \
    --cfg_distilled \
    --sr false \
    --rewrite false \
    --video_length 33 \
    --output_path ./outputs/test_video.mp4 \
    --overlap_group_offloading false