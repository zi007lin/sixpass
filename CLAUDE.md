# SixPass — Editorial Pipeline for Authors

## What this is

A webapp that helps authors prepare their manuscripts for publication. Authors upload a manuscript and SixPass guides it through a 6-phase editorial pipeline — from raw DOCX to publication-ready output.

## Origin

This product is based on a proven editorial workflow developed on Jake Orshansky's novella "The Trip" (github.com/zi007lin/The-Trip-Story). That project took a 40,600-word manuscript through 6 phases across 21 GitHub issues, producing a publication-ready manuscript. SixPass makes this process available to any author through a browser.

## The 6 Passes

1. **Ingest** — Upload DOCX/PDF/TXT → convert to Markdown, preserve original
2. **Grammar** — Missing articles, punctuation, spelling, doubled words
3. **Voice** — Flat transitions, redundant beats, pacing, tonal inconsistencies
4. **Continuity** — Character names, timeline, motif tracking, physical state
5. **Structure** — Sub-chapter breaks, chapter balancing, beat map, outline
6. **Export** — Publication-ready DOCX (title page, TNR 12pt, double-spaced, margins, page numbers)

## Tech stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Next.js API routes + FastAPI for document processing
- **AI**: Claude API (sonnet for grammar/structure, opus for voice/continuity)
- **Document processing**: mammoth (DOCX → Markdown), python-docx (Markdown → DOCX)
- **Database**: PostgreSQL
- **Storage**: S3-compatible for manuscripts
- **Auth**: Clerk

## Project structure

```
src/
  app/              — Next.js App Router pages
  components/       — React components
    ui/             — shadcn/ui primitives
    editor/         — Chapter editor components
    pipeline/       — Pipeline phase components
    dashboard/      — Dashboard components
  lib/              — Shared utilities
    ai/             — Claude API integration
    documents/      — DOCX/PDF/Markdown conversion
    pipeline/       — Phase logic (grammar, voice, continuity, structure)
  server/           — API routes
    api/
      projects/     — CRUD for projects
      chapters/     — Chapter management
      pipeline/     — Phase execution endpoints
      export/       — DOCX/PDF generation
  db/               — Database schema and migrations
services/
  processor/        — FastAPI document processing service
public/             — Static assets
docs/               — Architecture docs, API specs
```

## Core principles

- **Author sovereignty** — Never rewrite without explicit approval. All suggestions are accept/reject.
- **Original preserved** — Uploaded manuscript is immutable. All edits tracked separately.
- **Genre-aware** — Pipeline adapts to genre (horror permits fragments, thriller demands pace, etc.)
- **Transparent** — Every edit has a reason. Full diff view. Audit trail exportable.

## Conventions

### Git commits
Format: `TYPE: description`
Types: `FEAT`, `FIX`, `CHORE`, `DOCS`, `STYLE`, `REFACTOR`, `TEST`, `BUILD`

### Code style
- TypeScript strict mode
- Functional components with hooks
- Server components by default, `"use client"` only when needed
- Tailwind for styling, no CSS modules
- API routes return `{ data, error }` shape

## MVP scope (v1)

Passes 1, 2, and 6 only:
- Upload DOCX → convert to Markdown chapters
- Grammar pass with accept/reject UI
- Export to publication-ready DOCX
- Single-user, no auth needed for v1

## Reference implementation

The original project that proved this pipeline:
- Repository: github.com/zi007lin/The-Trip-Story
- Export script: `tools/export_docx.py`
- Word count tool: `tools/wordcount.py`
- Character sheet format: `characters/johnny.md`
- Motif tracking format: `notes/style-notes.md`
- Beat map format: `outline.md`
