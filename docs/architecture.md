# SixPass — Architecture

## System overview

```
┌─────────────────────────────────────────────────┐
│                   Browser                        │
│  Dashboard → Upload → Editor → Pipeline → Export │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              Next.js App                         │
│  App Router (pages) + API Routes (server)        │
│  ┌───────────┐  ┌───────────┐  ┌─────────────┐ │
│  │  Upload    │  │  Pipeline │  │  Export      │ │
│  │  Handler   │  │  Engine   │  │  Generator   │ │
│  └─────┬─────┘  └─────┬─────┘  └──────┬──────┘ │
└────────┼──────────────┼────────────────┼────────┘
         │              │                │
         ▼              ▼                ▼
┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│  Document    │ │  Claude API │ │  python-docx│
│  Processor   │ │  (Anthropic)│ │  (FastAPI)  │
│  (mammoth)   │ └─────────────┘ └─────────────┘
└──────┬───────┘
       ▼
┌─────────────────────────────────────────────────┐
│              PostgreSQL                          │
│  authors, projects, chapters, edits, exports     │
└─────────────────────────────────────────────────┘
```

## Data flow per pass

### Pass 1: Ingest
```
DOCX upload → mammoth (DOCX → HTML) → turndown (HTML → Markdown)
→ split by headings into chapters → store in DB → preserve original in S3
```

### Pass 2: Grammar
```
Chapter Markdown → Claude API (sonnet, grammar prompt)
→ JSON array of {line, old, new, reason} → store as pending edits
→ Author reviews in Editor UI → accept/reject each → apply accepted edits
```

### Pass 3: Voice
```
Chapter Markdown + genre context → Claude API (opus, voice prompt)
→ JSON array of suggestions → store as pending edits
→ Author reviews → accept/reject
```

### Pass 4: Continuity
```
All chapters + character sheet + outline → Claude API (opus, continuity prompt)
→ Flags: {chapter, line, issue, reference_chapter, reference_line}
→ Author reviews flags → resolve or dismiss
```

### Pass 5: Structure
```
All chapters → Claude API (sonnet, structure prompt)
→ Suggested breaks, chapter balance report, beat map
→ Author reviews → accept/reject break placements
```

### Pass 6: Export
```
Final chapter Markdown → python-docx (FastAPI service)
→ Formatted DOCX with title page, fonts, spacing, margins
→ Download link
```

## Database schema (v1)

```sql
CREATE TABLE projects (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  author_name TEXT NOT NULL,
  genre       TEXT,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE manuscripts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  filename    TEXT NOT NULL,
  file_path   TEXT NOT NULL,  -- S3 path to original
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chapters (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  number      INT NOT NULL,
  title       TEXT,
  content     TEXT NOT NULL,  -- Markdown
  word_count  INT DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE edits (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id  UUID REFERENCES chapters(id) ON DELETE CASCADE,
  pass        INT NOT NULL,  -- 1-6
  line        INT,
  old_text    TEXT NOT NULL,
  new_text    TEXT NOT NULL,
  reason      TEXT NOT NULL,
  status      TEXT DEFAULT 'pending',  -- pending, accepted, rejected
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE exports (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
  format      TEXT NOT NULL,  -- docx, pdf
  file_path   TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE pipeline_status (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
  pass_1      TEXT DEFAULT 'pending',
  pass_2      TEXT DEFAULT 'locked',
  pass_3      TEXT DEFAULT 'locked',
  pass_4      TEXT DEFAULT 'locked',
  pass_5      TEXT DEFAULT 'locked',
  pass_6      TEXT DEFAULT 'locked'
);
```

## AI model selection

| Pass | Model | Why |
|------|-------|-----|
| Grammar | claude-sonnet-4-5-20250929 | High precision, fast, cost-effective for rule-based checks |
| Voice | claude-opus-4-6 | Needs deep literary understanding, nuance, style sensitivity |
| Continuity | claude-opus-4-6 | Needs to hold full manuscript context, cross-reference chapters |
| Structure | claude-sonnet-4-5-20250929 | Structural analysis is pattern-matching, sonnet handles it well |

## MVP boundaries (v1)

**In scope**: Upload DOCX → Grammar pass → Export DOCX. Single user, no auth.
**Out of scope for v1**: Voice, Continuity, Structure passes. Multi-user. PDF export. Real-time collaboration.
