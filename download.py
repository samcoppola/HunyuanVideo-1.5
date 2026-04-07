#!/usr/bin/env python3
"""
HunyuanVideo 1.5 — Model Download Manager

Usage:
    python download.py <model> [<model> ...]

Available models:
    base            text_encoder + vae + scheduler (~26 GB) — always required
    t2v-480p        480p text-to-video distilled transformer (~33 GB)
    t2v-720p        720p text-to-video distilled transformer (~33 GB)
    i2v-480p        480p image-to-video distilled transformer (~33 GB)
    i2v-720p        720p image-to-video distilled transformer (~59 GB)
    vision-encoder  SigLIP vision encoder for i2v (~1 GB)
                    Requires: HF access to black-forest-labs/FLUX.1-Redux-dev
    sr-1080p        1080p super-resolution upsampler (~32 GB)

Examples:
    python download.py base t2v-480p             # minimal T2V setup (~59 GB)
    python download.py base i2v-720p vision-encoder  # 720p I2V setup (~86 GB)
    python download.py sr-1080p                  # add SR upsampler later
    python download.py i2v-480p                  # swap in 480p i2v transformer
"""
import os
import sys

os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import snapshot_download

CKPTS = "./ckpts"

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("ERROR: HF_TOKEN not set.")
    print("       Run: export HF_TOKEN='hf_...'")
    sys.exit(1)


def _download_glyph(ckpts):
    """Scarica Glyph-SDXL-v2 da ModelScope (non presente su HuggingFace)."""
    dest = f"{ckpts}/text_encoder/Glyph-SDXL-v2"
    marker = f"{dest}/checkpoints/byt5_model.pt"
    if os.path.exists(marker):
        print(f"  Already present ({dest}) — skipping.")
        return
    try:
        from modelscope import snapshot_download as ms_dl
    except ImportError:
        print("  ERROR: modelscope non installato. Esegui: pip install modelscope")
        sys.exit(1)
    print("  Downloading Glyph-SDXL-v2 from ModelScope...")
    ms_dl("AI-ModelScope/Glyph-SDXL-v2", local_dir=dest)
    print("  Done.")


MODELS = {
    "base": {
        "desc": "text_encoder (LLM+byT5+Glyph) + vae + scheduler (~42 GB)",
        "downloads": [
            {
                # DiT support files: VAE, scheduler, text_encoder skeleton
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["text_encoder/**", "vae/**", "scheduler/**"],
                "check_path": f"{CKPTS}/text_encoder",
            },
            {
                # LLM text encoder (Qwen2.5-VL-7B-Instruct, ~15 GB)
                "repo": "Qwen/Qwen2.5-VL-7B-Instruct",
                "local_dir": f"{CKPTS}/text_encoder/llm",
                "patterns": ["**"],
                "check_path": f"{CKPTS}/text_encoder/llm",
            },
            {
                # byT5 small encoder (~1.2 GB)
                "repo": "google/byt5-small",
                "local_dir": f"{CKPTS}/text_encoder/byt5-small",
                "patterns": ["**"],
                "check_path": f"{CKPTS}/text_encoder/byt5-small",
            },
        ],
        "post": _download_glyph,  # Glyph-SDXL-v2 da ModelScope
    },
    "t2v-480p": {
        "desc": "480p text-to-video distilled transformer (~33 GB)",
        "downloads": [
            {
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["transformer/480p_t2v_distilled/**"],
                "check_path": f"{CKPTS}/transformer/480p_t2v_distilled",
            }
        ],
    },
    "t2v-720p": {
        "desc": "720p text-to-video distilled transformer (~33 GB)",
        "downloads": [
            {
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["transformer/720p_t2v_distilled/**"],
                "check_path": f"{CKPTS}/transformer/720p_t2v_distilled",
            }
        ],
    },
    "i2v-480p": {
        "desc": "480p image-to-video distilled transformer (~33 GB)",
        "downloads": [
            {
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["transformer/480p_i2v_distilled/**"],
                "check_path": f"{CKPTS}/transformer/480p_i2v_distilled",
            }
        ],
    },
    "i2v-720p": {
        "desc": "720p image-to-video distilled transformer (~59 GB)",
        "downloads": [
            {
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["transformer/720p_i2v_distilled/**"],
                "check_path": f"{CKPTS}/transformer/720p_i2v_distilled",
            }
        ],
    },
    "vision-encoder": {
        "desc": "SigLIP vision encoder for i2v (~1 GB) [needs FLUX.1-Redux-dev access on HF]",
        "downloads": [
            {
                "repo": "black-forest-labs/FLUX.1-Redux-dev",
                "local_dir": f"{CKPTS}/vision_encoder/siglip",
                "patterns": ["image_encoder/**", "feature_extractor/**"],
                "check_path": f"{CKPTS}/vision_encoder/siglip/image_encoder",
            }
        ],
    },
    "sr-1080p": {
        "desc": "1080p SR transformer + upsampler (~32 GB)",
        "downloads": [
            {
                # SR diffusion transformer
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["transformer/1080p_sr_distilled/**"],
                "check_path": f"{CKPTS}/transformer/1080p_sr_distilled",
            },
            {
                # SR upsampler network (separate model)
                "repo": "tencent/HunyuanVideo-1.5",
                "local_dir": CKPTS,
                "patterns": ["upsampler/1080p_sr_distilled/**"],
                "check_path": f"{CKPTS}/upsampler/1080p_sr_distilled",
            },
        ],
    },
}


def is_downloaded(path):
    return os.path.exists(path) and len(os.listdir(path)) > 1


def download_model(name):
    if name not in MODELS:
        print(f"ERROR: Unknown model '{name}'.")
        print(f"Available: {', '.join(MODELS.keys())}")
        sys.exit(1)

    model = MODELS[name]
    print(f"\n{'='*60}")
    print(f"  {name}  —  {model['desc']}")
    print(f"{'='*60}")

    for dl in model["downloads"]:
        if is_downloaded(dl["check_path"]):
            print(f"  Already present ({dl['check_path']}) — skipping.")
            continue
        print(f"  Downloading from {dl['repo']} ...")
        os.makedirs(dl["local_dir"], exist_ok=True)
        snapshot_download(
            repo_id=dl["repo"],
            local_dir=dl["local_dir"],
            allow_patterns=dl["patterns"],
            token=HF_TOKEN,
            local_dir_use_symlinks=False,
        )
        print(f"  Done.")

    if "post" in model:
        model["post"](CKPTS)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    for model_name in sys.argv[1:]:
        download_model(model_name)

    print(f"\nAll requested models downloaded to {CKPTS}/")
