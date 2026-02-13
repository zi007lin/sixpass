# SixPass MVP — GitHub Issues Plan

Issues to create once the repo is on GitHub. MVP covers passes 1, 2, and 6.

---

## Phase 0: Project Setup

### Issue #1 — SETUP: Initialize Next.js project with TypeScript and Tailwind
- `npx create-next-app@latest` with App Router, TypeScript, Tailwind, ESLint
- Add shadcn/ui
- Configure path aliases
- Add Prettier config
- Verify dev server runs

### Issue #2 — SETUP: Database schema and connection
- Set up PostgreSQL (local dev via Docker or Neon)
- Create schema (projects, manuscripts, chapters, edits, exports, pipeline_status)
- Add Drizzle ORM or Prisma
- Seed script with test data

### Issue #3 — SETUP: FastAPI document processor service
- Python service in `services/processor/`
- Endpoints: POST `/convert` (DOCX → Markdown), POST `/export` (Markdown → DOCX)
- mammoth for DOCX → HTML → Markdown
- python-docx for Markdown → DOCX (port from The Trip's export_docx.py)
- requirements.txt, Dockerfile

---

## Phase 1: Ingest (Pass 1)

### Issue #4 — FEAT: Upload page with drag-and-drop
- Drag-and-drop zone for DOCX/PDF/TXT
- Title, author name, genre fields
- File validation (type, size limit)
- Upload to API route → store original → call processor

### Issue #5 — FEAT: DOCX to Markdown conversion
- API route receives uploaded DOCX
- Calls FastAPI processor `/convert`
- Splits Markdown into chapters by heading
- Stores chapters in DB
- Redirects to project dashboard

### Issue #6 — FEAT: Project dashboard
- List all projects with title, genre, date, word count
- Pipeline progress indicator (6 dots)
- Click project → chapter list
- Chapter list shows number, title, word count

---

## Phase 2: Grammar (Pass 2)

### Issue #7 — FEAT: Grammar pass engine
- API route: POST `/api/pipeline/grammar/:chapterId`
- Sends chapter content to Claude API (sonnet) with grammar prompt
- Parses JSON response into edits
- Stores edits in DB with status "pending"

### Issue #8 — FEAT: Chapter editor with accept/reject UI
- Side-by-side view: original (left) vs. working copy (right)
- Inline diff highlights for each pending edit
- Accept/reject buttons per edit
- Reason shown on hover/click
- Word count shown in corner
- Apply accepted edits to chapter content

### Issue #9 — FEAT: Run grammar pass on all chapters
- "Run Grammar Pass" button on project dashboard
- Queues all chapters for grammar analysis
- Progress indicator per chapter
- Batch status: pending → running → complete

---

## Phase 3: Export (Pass 6)

### Issue #10 — FEAT: Export configuration page
- Author name, contact info fields
- Title, subtitle fields
- Format selection (DOCX for v1)
- Preview title page

### Issue #11 — FEAT: DOCX export generation
- API route: POST `/api/export/:projectId`
- Collects all chapters from DB
- Calls FastAPI processor `/export`
- Returns download link
- Stores export record in DB

### Issue #12 — FEAT: Download page
- List of generated exports with date and format
- Download button
- Regenerate button

---

## Phase 4: Polish

### Issue #13 — STYLE: Landing page
- Hero: "Six editorial passes. One publication-ready manuscript."
- 6-pass visual breakdown
- Upload CTA
- Case study reference (The Trip)

### Issue #14 — CHORE: Error handling and loading states
- Upload errors (bad file type, too large)
- API errors (Claude rate limit, processor down)
- Loading skeletons for dashboard, editor, pipeline
- Toast notifications for actions

### Issue #15 — TEST: End-to-end test with sample manuscript
- Upload a test DOCX
- Run grammar pass
- Accept/reject some edits
- Export DOCX
- Verify output formatting
