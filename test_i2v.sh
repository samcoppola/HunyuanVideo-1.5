#!/bin/bash
# Test rapido I2V — no rewrite, no SR, 33 frame (~2s)
# Serve solo a verificare che il pipeline funzioni end-to-end.
# Se genera il video → tutto ok, poi usa run_via_appia.sh per la qualità piena.
set -e

cd /workspace/HunyuanVideo-1.5
source .venv/bin/activate

if [ ! -f "./appia_strada.png" ]; then
    echo "ERROR: appia_strada.png non trovata. Caricala nella root del repo."
    exit 1
fi

mkdir -p ./outputs

echo "Avvio test I2V 720p — 33 frame, no rewrite, no SR..."
echo "Dovresti vedere output immediato qui sotto:"
echo ""

PYTHONUNBUFFERED=1 torchrun --nproc_per_node=1 generate.py \
    --model_path ./ckpts \
    --resolution 720p \
    --prompt "Slow forward camera walk along the Via Appia Antica in ancient Rome." \
    --image_path ./appia_strada.png \
    --cfg_distilled \
    --video_length 33 \
    --sr false \
    --rewrite false \
    --overlap_group_offloading false \
    --output_path ./outputs/test_i2v.mp4

echo ""
echo "Test completato! Video: ./outputs/test_i2v.mp4"
