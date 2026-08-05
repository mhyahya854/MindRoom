"""Transcribe detector-listed audio/video assets into Graphify evidence files."""

from __future__ import annotations

import json
import os
from pathlib import Path

from graphify.transcribe import transcribe_all

OUT = Path(__file__).parent / "graphify-out"
detection = json.loads((OUT / ".graphify_detect.json").read_text(encoding="utf-8"))
media = detection.get("files", {}).get("video", [])
os.environ.setdefault("GRAPHIFY_WHISPER_MODEL", "base")
prompt = (
    "AFFiNE and BlockSuite local-first desktop application source assets, fixtures, "
    "and AI onboarding media. Use proper punctuation and paragraph breaks."
)
paths = transcribe_all(media, output_dir=OUT / "transcripts", initial_prompt=prompt)
(OUT / ".graphify_transcripts.json").write_text(
    json.dumps(paths, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"Transcribed {len(paths)} of {len(media)} audio/video files")
