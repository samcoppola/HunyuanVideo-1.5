#!/bin/bash
set -e

cd /workspace/HunyuanVideo-1.5
source .venv/bin/activate

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: set ANTHROPIC_API_KEY first"
    exit 1
fi

python generate.py \
    --model_path ./ckpts \
    --resolution 480p \
    --prompt "A highly realistic cinematic video of ancient Rome, slow forward walking movement along the Via Appia Antica during the Roman Imperial period. The road is paved with large irregular basalt stones, slightly worn and uneven. On both sides monumental Roman tombs, mausoleums, funerary architectures of different shapes: cylindrical tombs, temple-like structures with columns, pyramidal roofs, statues, relief decorations. Bright daylight, warm natural sunlight, soft shadows, slightly dusty atmosphere. Camera at eye level moving slowly forward, smooth and stable with slight natural head motion, gently looking right and left at architectural details. A few distant Roman figures in tunics. Sparse vegetation, Roman umbrella pine trees in background. Ultra-realistic textures, physically accurate lighting, cinematic depth of field, first-person perspective, photorealistic, no modern elements." \
    --image_path ./ludovico.png \
    --cfg_distilled \
    --sr false \
    --rewrite true \
    --video_length 33 \
    --overlap_group_offloading false \
    --output_path ./outputs/via_appia.mp4

echo "Done! Video saved to ./outputs/via_appia.mp4"
