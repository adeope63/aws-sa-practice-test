# Architect Lab · AWS SAA-C03

A personal, locally hosted practice platform with React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide icons, FastAPI, SQLite, SQLAlchemy, and Alembic. No AWS account, authentication, or cloud database is required.

## Run locally

Requires Python 3.12+, Node.js 20.19+ or 22.12+, and pnpm 11 (npm can also install and run the frontend). The scripts automatically find this device's bundled Codex runtimes when normal installations are absent.

```bash
./scripts/setup.sh
./scripts/dev.sh
```

Open http://127.0.0.1:5173. FastAPI runs on http://127.0.0.1:8000, and its API explorer is at `/docs`. Vite proxies `/api` to FastAPI.

If those ports are occupied, use:

```bash
LAB_BACKEND_PORT=8002 LAB_FRONTEND_PORT=5175 ./scripts/dev.sh
```

The current preview uses **http://127.0.0.1:5175** with the backend on port 8002. Ctrl-C stops the servers started by the script. Dependencies need internet access during installation; study activity and data storage remain local. Official documentation links open external AWS pages when clicked.

## Features

- All 13 sidebar pages work: study guide, dashboard, mock exams, quick practice, domain/task practice, architecture challenges, comparisons, wrong answers, bookmarks, history, analytics, bank, and settings.
- Responsive dark and light themes; timezone and daily-goal settings are stored in SQLite.
- A 65-question, 130-minute full mock randomizes selection and option order. Standard grading uses 20/17/15/13 questions across the four domains. Optional unscored simulation uses **15/13/12/10 scored** plus 15 random hidden unscored questions.
- Full mocks withhold correctness, option explanations, and scored/unscored flags until submission. This is a study tool, not a secure proctoring system: the separate question bank intentionally allows studying answer explanations.
- Exact-match grading for multiple response; unanswered and partially correct selections receive no credit.
- Immediate optional feedback in practice, Previous/Next controls, a navigable grid, flags, bookmarks, manual submit, automatic expiry, and saved incomplete sessions.
- The server stores absolute timer deadlines and enforces expiry on reads, answer saves, history, and analytics. Browser refresh does not reset time. Closing the browser does not pause a timed exam; the server finalizes an overdue exam on the next relevant request.
- Quick practice supports 10/20/30/50 or custom 1–1,000 questions, domain/task filters, and optional timing. If a filtered pool is smaller than the requested count, the UI reports its available size.
- Wrong-answer revision uses the latest completed attempt; a later correct attempt clears the item. Bookmarks are independent of revision.
- 10 architecture case challenges with selectable service/control choices and explanatory feedback. The architecture diagram is an illustrative review aid rather than a drag-and-drop simulator.
- 12 comparison groups include service use cases, constraints, trade-offs, official references, and task-linked practice.

## Data and analytics

`backend/lab.db` is created and migrated automatically at startup, then seeded idempotently. Bookmarks survive reseeding. No demonstration scores or fabricated study history are inserted.

All activity metrics come from SQLite records. Accuracy is correct graded questions / all graded questions, including unanswered. Unscored simulation items are excluded from accuracy and score but answered unscored items count as attempted activity. Session averages include completed mock, practice, revision, and challenge sessions. Domain coverage counts distinct answered graded question IDs. Streak and daily goal use the saved IANA timezone (initially Asia/Dubai).

Readiness is the mean percentage of the last three completed full mocks and is absent until three are complete. It is a study indicator, **not an AWS scaled score, pass probability, or certification guarantee**. AWS scoring is different from simple percentages.

To back up or restore, stop the server and copy/replace `backend/lab.db`. Keep runtime data out of Git. Tests use separate temporary SQLite databases and do not touch personal history. `DATABASE_URL` can override the file location with another SQLite URL.

## Question bank status

Before the Sybex import, the combined bank contained **800 items**: 400 original case questions plus 400 questions imported at the user's request from the supplied James Howlett PDF. The import includes **1,600 option explanations**, retained source wording/keys, current practice corrections, official task mappings, documentation references, and editorial review status.

Import review: **247 reviewed**, **45 corrected or clarified**, **108 study-only**. The **292 scored-eligible imported questions** participate in mixed quick/domain practice, revision and weighted mocks; the 108 ambiguous, defective or out-of-scope items are excluded from scored selection but remain visible for study. Those two collections provide 692 scored items; the Sybex import adds 235 more. Editorial review is not an independent AWS endorsement. Imported questions are user-supplied book content, not newly authored platform questions.

In Question Bank, select **Howlett book · 400 imported** in the collection filter. Use **Study-only review items** to inspect ambiguous questions, or **Eligible for scored practice** to practice the usable imports. The source/review disclosure shows original text, original answer key, review status and changes. Source keys and provenance are withheld during active mock/practice attempts until normal feedback becomes available.

The readable export is `output/text/AWS SAA-C03 - Questions Answers and Explanations.txt`; corrections/review report is `docs/BOOK_IMPORT_REVIEW.json`. Sources live in `backend/app/book_source.json`, `book_review.py`, `book_facts.py` and `book_import.py`. To rebuild the explanatory text without changing SQLite or the original extraction:

```bash
.venv/bin/python scripts/export_book_explanations.py
```

Alembic migration 002 adds provenance and scored eligibility without replacing attempts or bookmarks. Startup reseeds by stable IDs H001–H400. Existing original-bank IDs remain unchanged. Per-book source domains are retained separately; practice uses the reviewed official task/domain mapping. Each source item has its own record, with shared concept families identified; concept overlap is not claimed to be 400 independent architecture scenarios.


The original collection contains **400 original items exploring 100 architecture cases through four related perspectives**: architecture selection, design review, two-action implementation, and operational controls. This is not 400 unrelated scenarios; related families are explicitly identified. Mock generation prefers different families for scored questions. No dumps, paid questions, or proprietary exam items are included.

Original collection distribution: Security 120, Resilience 104, Performance 96, Cost Optimization 80. Every item maps to one of the 14 official task statements. Every item includes service tags, concepts, a scenario, four single-answer or five multiple-response options, keys, per-option reasoning, difficulty, documentation references, and a verification status.

Automated validation checks IDs, exact duplicate stems, domain distribution, task mapping, selection counts, option uniqueness, key membership, explanations, and reference domains. **Independent technical review is pending**, and all items retain that flag. Related variants intentionally overlap in concepts and options; exact-stem checking is not a claim of semantic independence. See `docs/CONTENT_REVIEW.md` for review limitations and reference notes. Prioritize the linked AWS service documentation when resolving ambiguity.

Question sources are `backend/app/cases.txt` and the perspective builder `backend/app/seed.py`; `python -m app.seed` validates them. Restart to apply source updates without deleting history.

## Verify

```bash
PYTHONPATH=backend .venv/bin/pytest backend/tests -q
cd frontend
pnpm test
pnpm build
pnpm exec playwright install chromium
pnpm test:e2e
```

Playwright starts isolated backend/frontend servers on 8001/5174. Tests cover saved answers after refresh, flag persistence, submission and review, search filters, bookmarks, comparisons, hidden unscored items, and mobile navigation. On this device Chromium was installed in `/private/tmp/architect-lab-browsers`; set `PLAYWRIGHT_BROWSERS_PATH` to that path to reuse it.

Validated after Sybex question import: 13 backend tests, 5 frontend unit tests, 8 browser tests, TypeScript and production build. Desktop/mobile screenshots are in `docs/`.

## Official scope

The implementation follows the [official SAA-C03 guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html), including its four domains, 14 task statements, knowledge/skill lists, concepts, and service scope pages. Source index: `docs/BLUEPRINT.md`.

The supplied request ended at “Tim” in section 9. This implementation covers the supplied requirements and includes optional timed practice. It does not assume any missing sections. Docker deployment is optional in the brief and is not included.


## Study Guide and quick flashcards

The Study Guide sidebar page contains **100 original condensed flashcards** based on the supplied Ben Piper/David Clinton fourth-edition study guide chapter topics. The deck covers all 13 chapters, four domains (30/26/24/20 cards), and 14 official tasks. Cards include the chapter, PDF/book-page cross-reference, concise answer and an AWS documentation link. Answers include current clarifications, including S3 strong consistency/default encryption, resource-policy principals and current calculator/service names. The extracted book text is kept faithful rather than silently revised.

Filter by chapter, domain, task, keyword, due/new status or favorites. Start a shuffled set of 10, 20, 50 or up to 100 matching cards. Click the card (or use Space when focus is outside a control) to reveal the answer. Ratings are disabled until reveal. **Again** returns the card once later in the session and makes it due in one minute; **Got it** schedules it in one day, doubling subsequent intervals up to 30 days. Per-card ratings, favorites and due dates persist in SQLite; the current in-memory set is restarted after a refresh. These are self-reported recall ratings, separate from exam scores.

The full extracted text is `output/text/AWS SAA-C03 Study Guide - Ben Piper and David Clinton.txt`, with **477 PDF-page markers**, assessment questions/answers, chapter reviews, appendices and index. The image-only cover is transcribed; blank/non-text pages are marked. Diagrams and visual layout are not reproduced. The cover's 900-question/100-flashcard offer refers to publisher online resources; those online resources are not included in the supplied PDF extraction, and this app's 100 cards are a separate original study set.

Use **Download extracted guide** on the Study Guide page. Direct page link: `http://127.0.0.1:5175/?page=Study%20Guide`. Alembic migration 003 adds a separate flashcards table; existing question-bank and exam history records remain intact. Card definitions are in `backend/app/flashcard_content.txt` and `study_cards.json`; `scripts/prepare_study_cards.py` attaches source-page cross-references using the intermediate extracted page index. Seed updates preserve flashcard ratings and favorites.


## Sybex review questions and option explanations

The question bank now contains **1,117 items**: 400 original case questions, 400 Howlett imports and **317 Sybex study guide imports**. The scored pool contains **927 items**. Select **Sybex study guide · 317 imported** in Question Bank to browse or practice this source. Every Sybex question has a general rationale and every one of its **1,279 answer choices** has an explanation. These are visible through Study explanation and normal practice feedback, while answer keys remain hidden during unanswered attempts.

Sybex review: **199 retained-key source reviews**, **38 corrected/clarified items**, **80 study-only items** and **two exact duplicates** excluded from scored selection. This leaves **235 Sybex questions** eligible for mixed practice, domain practice, revision and weighted mocks. Study-only entries explain ambiguities, outdated services and source defects rather than assigning an invented unique answer. Original question text, choices and publisher keys remain in source/review disclosures. Retained-key reviews use the publisher explanation plus editorial option notes; targeted AWS documentation checks cover changes and current service differences, not an independent certification endorsement.

The readable export is `output/text/AWS SAA-C03 Study Guide - Questions Answers and Explanations.txt`; regenerate it with `.venv/bin/python scripts/export_sybex_explanations.py`. Import definitions are `backend/app/sybex_source.json`, `sybex_option_notes.txt`, `sybex_review.py` and `sybex_import.py`; the decision report is `docs/SYBEX_IMPORT_REVIEW.json`. Stable IDs Y00-001 through the per-chapter Y13 range keep imports separate from H-prefixed Howlett IDs and original cases. Startup upserts definitions without overwriting bookmarks, exam history or flashcard progress. No database schema migration is required.
