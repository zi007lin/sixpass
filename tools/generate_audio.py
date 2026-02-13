#!/usr/bin/env python3
"""Generate audiobook MP3s from a Markdown manuscript or CliffsNotes file.

Uses Microsoft Edge TTS (free, no API key required).
Output can be imported into Camtasia or any audio/video editor.

Usage:
    python tools/generate_audio.py <input.md> [--output-dir <dir>] [--voice <voice>] [--list-voices]

Examples:
    python tools/generate_audio.py docs/case-study/the-trip-cliffsnotes.md
    python tools/generate_audio.py docs/case-study/the-trip-cliffsnotes.md --voice en-GB-SoniaNeural
    python tools/generate_audio.py --list-voices
"""

import asyncio
import argparse
import re
import sys
from pathlib import Path

import edge_tts

# High-quality neural voices (free via Edge TTS)
VOICES = {
    "male-us": "en-US-GuyNeural",
    "female-us": "en-US-JennyNeural",
    "male-uk": "en-GB-RyanNeural",
    "female-uk": "en-GB-SoniaNeural",
    "male-au": "en-AU-WilliamNeural",
    "female-au": "en-AU-NatashaNeural",
}

DEFAULT_VOICE = "en-US-GuyNeural"


def strip_markdown(text: str) -> str:
    """Convert markdown to plain text suitable for TTS."""
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Remove markdown tables — extract cell content
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Skip table separator lines
        if re.match(r"^\|[-:|  ]+\|$", stripped):
            continue
        # Convert table rows to readable text
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            cells = [c for c in cells if c and not re.match(r"^[-:]+$", c)]
            if cells:
                lines.append(". ".join(cells) + ".")
            continue
        lines.append(line)
    text = "\n".join(lines)
    # Remove headers markers but keep text
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Remove inline code
    text = re.sub(r"`(.+?)`", r"\1", text)
    # Remove links, keep text
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Remove bullet points
    text = re.sub(r"^[\-\*]\s+", "", text, flags=re.MULTILINE)
    # Remove numbered list markers
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    # Clean up multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown into sections by ## headers. Returns (title, content) pairs."""
    sections = []
    current_title = "Introduction"
    current_lines = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append((current_title, content))
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("# ") and not sections:
            # Top-level title becomes the intro section title
            current_title = line[2:].strip()
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append((current_title, content))

    return sections


def slugify(text: str) -> str:
    """Convert title to filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:50]


async def generate_audio(text: str, output_path: Path, voice: str):
    """Generate MP3 from text using Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


async def list_voices():
    """List available English voices."""
    voices = await edge_tts.list_voices()
    english = [v for v in voices if v["Locale"].startswith("en-")]
    print(f"\nAvailable English voices ({len(english)}):\n")
    for v in sorted(english, key=lambda x: x["ShortName"]):
        gender = v["Gender"]
        name = v["ShortName"]
        locale = v["Locale"]
        print(f"  {name:<30} {gender:<8} {locale}")
    print(f"\nPreset shortcuts:")
    for key, val in VOICES.items():
        print(f"  --voice {key:<12} → {val}")


async def main():
    parser = argparse.ArgumentParser(
        description="Generate audiobook MP3s from Markdown files (free, using Edge TTS)"
    )
    parser.add_argument("input", nargs="?", help="Input Markdown file")
    parser.add_argument(
        "--output-dir", "-o", default=None, help="Output directory (default: audio/ next to input)"
    )
    parser.add_argument(
        "--voice", "-v", default=DEFAULT_VOICE,
        help=f"Voice name or preset ({', '.join(VOICES.keys())}). Default: {DEFAULT_VOICE}"
    )
    parser.add_argument(
        "--single", "-s", action="store_true",
        help="Generate a single MP3 instead of per-section files"
    )
    parser.add_argument(
        "--list-voices", action="store_true", help="List available voices and exit"
    )

    args = parser.parse_args()

    if args.list_voices:
        await list_voices()
        return

    if not args.input:
        parser.error("Input file required (or use --list-voices)")

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    # Resolve voice preset
    voice = VOICES.get(args.voice, args.voice)

    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = input_path.parent / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Input:  {input_path}")
    print(f"Output: {output_dir}/")
    print(f"Voice:  {voice}")
    print()

    # Read and process markdown
    raw = input_path.read_text(encoding="utf-8")

    if args.single:
        # Single file mode
        plain = strip_markdown(raw)
        output_file = output_dir / f"{input_path.stem}.mp3"
        print(f"Generating single audio file...")
        await generate_audio(plain, output_file, voice)
        print(f"  Saved: {output_file}")
    else:
        # Per-section mode
        sections = split_sections(raw)
        print(f"Found {len(sections)} sections\n")

        for i, (title, content) in enumerate(sections, 1):
            plain = strip_markdown(content)
            if not plain or len(plain) < 20:
                print(f"  [{i:02d}] {title} — skipped (too short)")
                continue

            # Add section title as spoken intro
            spoken = f"{title}.\n\n{plain}"

            slug = slugify(title)
            output_file = output_dir / f"{i:02d}-{slug}.mp3"

            print(f"  [{i:02d}] {title}...")
            await generate_audio(spoken, output_file, voice)
            print(f"       Saved: {output_file} ({len(plain):,} chars)")

    # Generate Camtasia import script
    camtasia_script = output_dir / "camtasia-import.txt"
    mp3s = sorted(output_dir.glob("*.mp3"))
    with open(camtasia_script, "w") as f:
        f.write("# Camtasia Import Instructions\n")
        f.write("# \n")
        f.write("# 1. Open Camtasia\n")
        f.write("# 2. File > Import > Media\n")
        f.write("# 3. Select all MP3 files from this folder\n")
        f.write("# 4. Drag them to the timeline in order\n")
        f.write("# 5. Add title cards between sections if desired\n")
        f.write("# \n")
        f.write("# Files to import (in order):\n")
        for mp3 in mp3s:
            f.write(f"#   {mp3.name}\n")
        f.write("# \n")
        f.write(f"# Voice used: {voice}\n")
        f.write(f"# Total files: {len(mp3s)}\n")

    print(f"\n  Camtasia import guide: {camtasia_script}")
    print(f"\nDone! {len(mp3s)} audio files generated in {output_dir}/")


if __name__ == "__main__":
    asyncio.run(main())
