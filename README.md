# SixPass

**Six editorial passes. One publication-ready manuscript.**

SixPass is a webapp that helps authors prepare their manuscripts for publication. Upload your manuscript and SixPass guides it through a structured 6-pass editorial pipeline — from raw draft to publisher-ready DOCX.

## The 6 Passes

| Pass | What it does |
|------|-------------|
| 1. **Ingest** | Upload your DOCX, PDF, or TXT. SixPass converts it to working chapters and preserves your original. |
| 2. **Grammar** | Catches missing articles, punctuation errors, spelling, and awkward phrasing. You accept or reject each suggestion. |
| 3. **Voice** | Identifies flat transitions, redundant beats, and pacing problems. Suggests rewrites that preserve your voice. |
| 4. **Continuity** | Tracks character names, timeline logic, motif escalation, and physical state across all chapters. |
| 5. **Structure** | Places scene breaks, balances chapter lengths, generates a beat map and outline. |
| 6. **Export** | Generates a publication-ready DOCX — title page, proper fonts, double-spacing, margins, page numbers. |

## How it works

1. Upload your manuscript
2. Select your genre (the pipeline adapts its sensibility)
3. Run each pass — review and accept/reject suggestions
4. Download your publication-ready manuscript

Your original manuscript is never modified. Every edit is tracked with a reason. You control what changes.

## Built on a proven process

SixPass productizes an editorial workflow developed on a real 40,600-word novella. The original project ([The Trip](https://github.com/zi007lin/The-Trip-Story)) went through 6 phases across 21 editorial issues, producing a publication-ready manuscript. SixPass makes that same process available to any author.

## Tech stack

Next.js / TypeScript / Tailwind CSS / Claude API / PostgreSQL / python-docx

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run document processor
cd services/processor && pip install -r requirements.txt && uvicorn main:app --reload
```

## Credits

| Role | Name |
|------|------|
| Created by | **Zi Lin** |
| Reference manuscript | **Jake Orshansky** — *The Trip* |

## License

TBD
