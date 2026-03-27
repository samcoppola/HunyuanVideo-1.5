"""Download i2v models (transformer + vision_encoder) from HuggingFace."""
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"  # disable Xet storage (avoids reconstruction errors)
from huggingface_hub import snapshot_download

token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("Set HF_TOKEN before running this script.")

print("Downloading transformer/480p_i2v_distilled and vision_encoder/siglip ...")
print("This will take several minutes (~33 GB total).")
print()

snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir="./ckpts",
    allow_patterns=[
        "transformer/480p_i2v_distilled/**",
        "vision_encoder/**",
    ],
    token=token,
    local_dir_use_symlinks=False,
)

print()
print("Done! Files saved to ./ckpts/")
print("  - transformer/480p_i2v_distilled/")
print("  - vision_encoder/siglip/")
