"""Download i2v models (transformer + vision_encoder) from HuggingFace.

vision_encoder/siglip comes from black-forest-labs/FLUX.1-Redux-dev
(requires accepting terms at https://huggingface.co/black-forest-labs/FLUX.1-Redux-dev)
"""
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import snapshot_download

token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("Set HF_TOKEN before running this script.")

# 1. Download i2v transformer (already done if folder exists)
transformer_path = "./ckpts/transformer/480p_i2v_distilled"
if os.path.exists(transformer_path) and len(os.listdir(transformer_path)) > 1:
    print("transformer/480p_i2v_distilled already present, skipping.")
else:
    print("Downloading transformer/480p_i2v_distilled (~33 GB) ...")
    snapshot_download(
        repo_id="tencent/HunyuanVideo-1.5",
        local_dir="./ckpts",
        allow_patterns=["transformer/480p_i2v_distilled/**"],
        token=token,
        local_dir_use_symlinks=False,
    )
    print("Transformer done.")

print()

# 2. Download SigLIP vision encoder from FLUX.1-Redux-dev
print("Downloading vision_encoder/siglip from black-forest-labs/FLUX.1-Redux-dev ...")
print("(requires accepted terms on HuggingFace for that repo)")
snapshot_download(
    repo_id="black-forest-labs/FLUX.1-Redux-dev",
    local_dir="./ckpts/vision_encoder/siglip",
    allow_patterns=["image_encoder/**", "feature_extractor/**"],
    token=token,
    local_dir_use_symlinks=False,
)
print("Vision encoder done.")

print()
print("Done! Files saved to:")
print("  - ./ckpts/transformer/480p_i2v_distilled/")
print("  - ./ckpts/vision_encoder/siglip/image_encoder/")
print("  - ./ckpts/vision_encoder/siglip/feature_extractor/")
