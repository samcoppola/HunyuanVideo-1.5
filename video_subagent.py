"""
Video Subagent for HunyuanVideo-1.5
====================================
Conversational agent that collects generation parameters from the user
(or decides them automatically) and then runs generate.py.

Usage:
    python video_subagent.py
    python video_subagent.py --auto "video di un vecchio che fuma la pipa"

Requires:
    export ANTHROPIC_API_KEY="sk-ant-..."
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

import anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_PATH    = "./ckpts"
OUTPUT_DIR    = "./outputs"
CLAUDE_MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SYSTEM_PROMPT = """
You are the Video Subagent for a HunyuanVideo-1.5 generation system.
Your job is to help the user generate a video by collecting the necessary
parameters, then calling the generate_video tool.

## Available model capabilities

**Modes**
- t2v: text-to-video (user describes what they want in words)
- i2v: image-to-video (user provides a reference image + describes the motion)

**Resolutions**
- 480p: faster and cheaper, good for tests
- 720p: higher quality, recommended for final renders

**Video length (frames at 24fps)**
- 33  frames ≈ 1.4 seconds
- 65  frames ≈ 2.7 seconds
- 121 frames ≈ 5 seconds  ← optimal quality

**Aspect ratios**
- 16:9  landscape (default, most common)
- 9:16  portrait (vertical / social media)
- 1:1   square
- 4:3   classic
- 3:4   portrait classic

**Super Resolution (SR)**
- Upscales the output: 480p → 720p, or 720p → 1080p
- Adds quality but takes extra time and VRAM
- Default: off

**Notes**
- The distilled model (2× faster, same quality) is always used.
- Prompt rewriting is always enabled: a brief user description is
  automatically expanded into a detailed, cinematic prompt.
- The user never needs to know about "distilled", "cfg", "offloading", etc.

## How to behave

1. Read the user's request.
2. Infer as many parameters as you can from context:
   - If the user mentions or attaches an image → i2v
   - Mention of "vertical", "portrait", "stories" → 9:16
   - Mention of "short", "quick", "test" → 33 frames / 480p
   - Mention of "best quality", "final" → 720p + SR
3. Present a summary of the chosen parameters and ask for confirmation.
   Always show every parameter so the user knows what options exist.
4. If the user says "ok", "vai", "yes", "auto", or anything positive → call
   generate_video immediately.
5. If the user asks to change something → update and confirm again.
6. If the user explicitly says they want to decide everything manually →
   ask one parameter at a time.
7. Never mention technical details like "cfg_distilled", "offloading",
   "transformer", "flow_shift". Speak in plain language.
8. Always respond in the same language the user used.
""".strip()

# ---------------------------------------------------------------------------
# Tool definition
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "generate_video",
        "description": (
            "Launch the video generation once all parameters are confirmed. "
            "Call this only after the user has approved the parameters."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The user's original description (will be auto-rewritten).",
                },
                "task": {
                    "type": "string",
                    "enum": ["t2v", "i2v"],
                    "description": "t2v = text-to-video, i2v = image-to-video.",
                },
                "resolution": {
                    "type": "string",
                    "enum": ["480p", "720p"],
                    "description": "Output resolution.",
                },
                "video_length": {
                    "type": "integer",
                    "enum": [33, 65, 121],
                    "description": "Number of frames: 33≈1.4s, 65≈2.7s, 121≈5s.",
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "e.g. 16:9, 9:16, 1:1, 4:3, 3:4",
                },
                "sr": {
                    "type": "boolean",
                    "description": "Apply super-resolution upscaling after generation.",
                },
                "image_path": {
                    "type": "string",
                    "description": "Path to the reference image (required for i2v, omit for t2v).",
                },
            },
            "required": ["prompt", "task", "resolution", "video_length", "aspect_ratio", "sr"],
        },
    }
]

# ---------------------------------------------------------------------------
# Video generation
# ---------------------------------------------------------------------------

def build_generate_command(params: dict, output_path: str) -> list[str]:
    cmd = [
        sys.executable, "generate.py",
        "--model_path",   MODEL_PATH,
        "--resolution",   params["resolution"],
        "--prompt",       params["prompt"],
        "--cfg_distilled",
        "--rewrite",      "true",
        "--sr",           "true" if params["sr"] else "false",
        "--video_length", str(params["video_length"]),
        "--aspect_ratio", params["aspect_ratio"],
        "--output_path",  output_path,
        "--overlap_group_offloading", "false",
    ]
    if params["task"] == "i2v" and params.get("image_path"):
        cmd += ["--image_path", params["image_path"]]
    return cmd


def run_generation(params: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build a descriptive filename
    slug = params["prompt"][:40].replace(" ", "_").replace("/", "-")
    filename = f"{params['task']}_{params['resolution']}_{params['video_length']}f_{slug}.mp4"
    output_path = os.path.join(OUTPUT_DIR, filename)

    cmd = build_generate_command(params, output_path)

    print("\n" + "═" * 60)
    print("Avvio generazione video...")
    print(f"Output: {output_path}")
    print("═" * 60 + "\n")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        return f"✅ Video generato: {output_path}"
    else:
        return f"❌ Generazione fallita (exit code {result.returncode}). Controlla i log sopra."


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

class VideoSubagent:
    def __init__(self):
        self.client   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.history  = []

    def chat(self, user_message: str) -> str:
        """Send one user message, handle tool calls, return the final text reply."""
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.history,
            )

            # Collect any text content from this turn
            text_parts = [
                block.text for block in response.content
                if hasattr(block, "text")
            ]
            assistant_text = "\n".join(text_parts).strip()

            # Add assistant turn to history
            self.history.append({"role": "assistant", "content": response.content})

            # No tool call → return the text reply
            if response.stop_reason != "tool_use":
                return assistant_text

            # Handle tool call
            tool_use_block = next(
                b for b in response.content if b.type == "tool_use"
            )
            params   = tool_use_block.input
            tool_id  = tool_use_block.id

            # Print what Claude decided before generating
            if assistant_text:
                print(f"\nAssistente: {assistant_text}\n")

            generation_result = run_generation(params)

            # Feed tool result back to Claude
            self.history.append({
                "role": "user",
                "content": [{
                    "type":        "tool_result",
                    "tool_use_id": tool_id,
                    "content":     generation_result,
                }],
            })
            # Loop again so Claude can give a final text response


def interactive_loop():
    """Standard interactive REPL."""
    agent = VideoSubagent()
    print("Video Subagent — HunyuanVideo 1.5")
    print("Digita la tua richiesta. Ctrl+C per uscire.\n")

    try:
        while True:
            user_input = input("Tu: ").strip()
            if not user_input:
                continue
            reply = agent.chat(user_input)
            print(f"\nAssistente: {reply}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nUscita.")


def auto_mode(prompt: str):
    """Non-interactive: send prompt + 'auto' and run immediately."""
    agent = VideoSubagent()
    # First turn: send the request
    reply = agent.chat(prompt)
    print(f"Assistente: {reply}\n")
    # Second turn: confirm automatically
    reply = agent.chat("auto")
    print(f"Assistente: {reply}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Subagent for HunyuanVideo-1.5")
    parser.add_argument(
        "--auto",
        metavar="PROMPT",
        help="Non-interactive: pass a prompt and auto-confirm all parameters.",
    )
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Errore: imposta la variabile d'ambiente ANTHROPIC_API_KEY.")
        sys.exit(1)

    if args.auto:
        auto_mode(args.auto)
    else:
        interactive_loop()
