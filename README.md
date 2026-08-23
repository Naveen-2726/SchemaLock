\# SchemaLock



\### AI-Assisted PostgreSQL Migration Safety \& Deployment Intelligence



SchemaLock is a developer-focused safety analysis tool for PostgreSQL database migrations.



It analyzes migration SQL before deployment using a \*\*deterministic safety engine\*\*, \*\*risk intelligence\*\*, \*\*AI-assisted reasoning\*\*, \*\*AI validation guardrails\*\*, \*\*migration integrity verification\*\*, and a \*\*deterministic deployment gate\*\*.



The goal is not to claim that a migration is "100% safe".



Instead, SchemaLock provides explainable evidence about potential migration risks and recommends whether a migration should proceed to normal review, receive additional review, or be blocked from deployment.



\---



\## 🚨 Problem



A database migration can be syntactically valid and still create serious production risks.



Examples include:



\- Dropping production tables

\- Removing columns still used by applications

\- Adding `NOT NULL` columns to tables containing existing rows

\- Changing column data types

\- Creating indexes on large production tables

\- Introducing multiple destructive operations in one migration

\- Generating unsafe or incomplete rollback SQL

\- Modifying migration files after they have been reviewed



Traditional SQL validation primarily answers:



> "Is this SQL valid?"



SchemaLock asks a different question:



> "What operational risks could this migration introduce?"



\---



\# 💡 Solution



SchemaLock uses a defense-in-depth architecture:



```text

&#x20;                PostgreSQL Migration SQL

&#x20;                          │

&#x20;                          ▼

&#x20;               Deterministic Analyzer

&#x20;                          │

&#x20;            ┌─────────────┴─────────────┐

&#x20;            ▼                           ▼

&#x20;      Risk Scoring               Rule Findings

&#x20;            │

&#x20;            ▼

&#x20;      Risk Intelligence

&#x20;            │

&#x20;     ┌──────┼──────────┐

&#x20;     ▼      ▼          ▼

&#x20;  Data    Locking   Compatibility

&#x20;  Loss     Risk        Risk

&#x20;            │

&#x20;            ▼

&#x20;       Blast Radius

&#x20;            │

&#x20;            ▼

&#x20;       Gemini AI Reasoning

&#x20;            │

&#x20;            ▼

&#x20;        AI Guard Layer

&#x20;            │

&#x20;     ┌──────┴───────────┐

&#x20;     ▼                  ▼

&#x20;Safer Migration     Rollback Advice

&#x20;            │

&#x20;            ▼

&#x20;      SHA-256 Integrity

&#x20;            │

&#x20;            ▼

&#x20;      Deployment Gate

&#x20;            │

&#x20;      ┌─────┼─────┐

&#x20;      ▼     ▼     ▼

&#x20;   READY  REVIEW BLOCKED

🧠 Core Design Principle

Deterministic safety first, AI second.



SchemaLock does not allow an LLM to become the source of truth for deterministic migration risks.



The pipeline first identifies known risks using deterministic PostgreSQL analysis.



Gemini is then given the verified findings and migration context to provide:



Risk explanations

Additional contextual risks

Safer migration strategies

Rollback recommendations

Operational deployment advice



If Gemini is unavailable or fails, the deterministic analysis continues to work.



🔍 Deterministic PostgreSQL Analyzer



The analyzer currently detects:



Rule	Severity	Risk

DROP TABLE	CRITICAL	Removes an entire table

TRUNCATE	CRITICAL	Removes all rows

DROP COLUMN	HIGH	Permanently removes column data

ADD COLUMN ... NOT NULL	HIGH	Potentially unsafe for existing rows

ALTER COLUMN ... TYPE	HIGH	Data conversion/compatibility risk

ADD UNIQUE	MEDIUM	Existing duplicates may cause failure

CREATE INDEX	MEDIUM	Potential production performance/locking impact

CREATE INDEX CONCURRENTLY	LOW	Reduced locking impact compared with standard index creation



The analyzer also detects:



Multiple destructive/high-risk operations

Empty SQL

Invalid SQL input

SQL comments that could otherwise cause false positives



The analyzer intentionally focuses on important PostgreSQL migration patterns rather than attempting to implement a complete PostgreSQL parser.



📊 Risk Scoring



SchemaLock uses transparent deterministic scoring.



Risk scores are calculated from documented rule weights rather than arbitrary AI classification.



Example:



DROP TABLE

&#x20;   ↓

CRITICAL finding

&#x20;   ↓

Risk score increases

&#x20;   ↓

Deployment Gate evaluates

&#x20;   ↓

BLOCKED



The score represents a risk index, not a probability of failure.



For example:



90/100 does not mean "90% chance of failure."



It means the migration contains a combination of high-impact risk signals according to SchemaLock's deterministic scoring model.



💥 Risk Intelligence \& Blast Radius



SchemaLock converts individual findings into four operational dimensions:



Data Loss Risk



Potential permanent loss or destruction of stored data.



Locking Impact



Potential impact from PostgreSQL schema operations, validation, or table modification.



Application Compatibility



Potential breakage of application code that depends on the affected schema.



Performance Risk



Potential query-performance or migration-execution impact.



The system also calculates a Potential Blast Radius based on:



Number of destructive operations

Number of affected operations

Application compatibility impact

Combined risk dimensions



Example:



Data Loss          HIGH

Locking Impact     HIGH

Compatibility      HIGH

Performance        MEDIUM



Blast Radius       HIGH

Destructive Ops    1

Affected Ops       3



These are static estimates based on migration analysis.



🤖 Gemini AI Reasoning



Gemini provides contextual reasoning after deterministic analysis.



The AI is instructed to:



Use the deterministic findings as evidence

Avoid inventing database facts

Generate PostgreSQL-compatible SQL only

Clearly distinguish known risks from recommendations

Avoid claiming guaranteed safety

Avoid claiming guaranteed zero downtime

Refuse to invent missing schema information



Example output can include:



Risk explanation

Additional risks

Safer migration

Rollback SQL

Deployment recommendation

🛡️ AI Guard Layer



One of the most important reliability features in SchemaLock is the AI validation layer.



During testing, an unsafe AI behavior was discovered.



Given:



ALTER TABLE users DROP COLUMN legacy\_email;



the migration does not contain the original column's data type.



An LLM may nevertheless generate:



ALTER TABLE users ADD COLUMN legacy\_email VARCHAR(255);



This is unsafe because the original type could have been:



CITEXT

JSONB

UUID



or something else.



SchemaLock therefore detects this situation and adds an explicit warning:



Original column data type and constraints are unknown

from the migration input.



Verify the original table schema before applying

rollback DDL.



The guard also sanitizes overconfident AI claims such as:



100% safe

guaranteed zero-downtime



The deterministic findings always remain authoritative.



🔐 Migration Integrity



SchemaLock generates a SHA-256 fingerprint from normalized migration SQL.



Normalization includes:



Line-ending normalization

SQL comment removal

Whitespace normalization

SQL keyword normalization



Example:



Migration SQL

&#x20;    ↓

Normalize

&#x20;    ↓

SHA-256

&#x20;    ↓

Migration Fingerprint



If the migration is modified after analysis, SchemaLock can detect the change.



Example:



🟢 CONTENT INTEGRITY GENERATED



After modification:



🟡 Migration modified —

&#x20;  re-analyze to refresh fingerprint



The verification endpoint can also compare an expected fingerprint with the current migration.



Important scope



The SHA-256 system verifies migration content integrity.



It does not inspect or compare a live production database schema.



🚦 Deployment Gate



The final decision layer is deterministic.



SchemaLock produces one of three recommendations:



🟢 READY FOR REVIEW



The migration has low static risk and no blocking conditions.



This does not mean the migration is guaranteed safe.



🟡 REQUIRES REVIEW



The migration contains meaningful risk that should receive additional engineering review.



🔴 BLOCKED



The migration contains conditions that should prevent normal deployment until the identified risks are addressed.



The gate can block when:



Deterministic severity is CRITICAL

Risk score is >= 80

Blast radius is CRITICAL

Multiple destructive operations exist

AI guard reports an unsafe/unsupported recommendation

Migration integrity reports drift



The deployment gate is a recommendation system, not an actual deployment system.



There is intentionally no "Override and Deploy" functionality.



🧪 Reliability \& Testing



SchemaLock has an automated backend test suite covering:



Deterministic migration analysis

Destructive operations

NOT NULL additions

Column type changes

Index creation

Multiple-risk migrations

Comment handling

Gemini success/failure scenarios

Missing API key fallback

AI hallucination guard

Zero-downtime claim sanitization

Risk Intelligence

Blast Radius

SHA-256 fingerprints

Migration drift detection

Deployment Gate decisions

Current test result

40 / 40 backend tests PASSED



The frontend production build was also verified successfully:



vite v5.4.14 building for production...

✓ 1842 modules transformed.

✓ built successfully

🖥️ User Interface



SchemaLock uses:



React

Vite

Monaco Editor

Lucide React



The interface provides:



┌───────────────────────────────────────────┐

│ SchemaLock                                │

├───────────────────┬───────────────────────┤

│                   │ Risk Score             │

│   Monaco SQL      │ Deployment Gate        │

│   Migration       │ Migration Integrity    │

│   Editor          │ Risk Intelligence      │

│                   │ Blast Radius           │

│                   │ Findings               │

│                   │ Gemini Analysis        │

│                   │ Safer Migration        │

│                   │ Rollback               │

└───────────────────┴───────────────────────┘

🛠️ Technology Stack

Frontend

React

Vite

Monaco Editor

Lucide React

Backend

Python

FastAPI

Pydantic

sqlparse

Google GenAI SDK

AI

Gemini

Security / Integrity

SHA-256

Testing

pytest

🚀 Running Locally

Backend

cd backend



python -m venv .venv



\# Windows PowerShell

.\\.venv\\Scripts\\Activate.ps1



pip install -r requirements.txt



python -m uvicorn main:app --host 127.0.0.1 --port 8000



Backend:



http://127.0.0.1:8000

Frontend

cd frontend



npm install



npm run dev



Frontend:



http://127.0.0.1:5173

🔑 Gemini Configuration



Create an environment file for local development:



GEMINI\_API\_KEY=your\_api\_key\_here



Never commit the real API key to GitHub.



SchemaLock continues to provide deterministic migration analysis even when Gemini is unavailable.



📡 API

Analyze Migration

POST /api/analyze



Request:



{

&#x20; "sql": "DROP TABLE users;"

}



Response contains:



{

&#x20; "risk\_score": 50,

&#x20; "severity": "CRITICAL",

&#x20; "findings": \[],

&#x20; "summary": "...",

&#x20; "risk\_intelligence": {},

&#x20; "migration\_integrity": {},

&#x20; "ai\_analysis": {},

&#x20; "deployment\_gate": {}

}

Verify Migration Fingerprint

POST /api/verify-fingerprint



The endpoint compares the expected SHA-256 fingerprint with the fingerprint calculated from the supplied migration.



🎯 Example



Input:



ALTER TABLE users

ADD COLUMN phone VARCHAR(20) NOT NULL;



ALTER TABLE users

DROP COLUMN legacy\_email;



SchemaLock can identify:



Risk Score             90/100

Severity               CRITICAL



ADD\_COLUMN\_NOT\_NULL    HIGH

DROP\_COLUMN            HIGH

Multiple Operations    HIGH



Data Loss              HIGH

Locking                HIGH

Compatibility          HIGH

Performance            MEDIUM



Blast Radius           HIGH



Deployment Gate        🔴 BLOCKED



Gemini can then provide a safer staged migration strategy while the AI Guard prevents unsupported rollback assumptions from being treated as authoritative.



🎥 Recommended Demo Flow



A typical demonstration can show:



1\. Dangerous migration

ALTER TABLE users

ADD COLUMN phone VARCHAR(20) NOT NULL;



ALTER TABLE users

DROP COLUMN legacy\_email;



Show:



90/100

CRITICAL

DEPLOYMENT BLOCKED

2\. Explain deterministic evidence



Show:



ADD\_COLUMN\_NOT\_NULL

DROP\_COLUMN

Multiple destructive operations

Risk Intelligence

Blast Radius

3\. Show AI reasoning



Show:



Safer Migration

Rollback recommendation

Operational advice

4\. Show the AI Guard



Demonstrate why an invented rollback type such as VARCHAR(255) cannot be trusted without schema information.



5\. Show migration integrity



Generate the SHA-256 fingerprint, modify the SQL, and demonstrate drift detection.



6\. Show a low-risk migration

ALTER TABLE users

ADD COLUMN last\_login TIMESTAMP;



Show:



0/100

LOW

READY FOR REVIEW

⚠️ Limitations



SchemaLock intentionally does not:



Connect to a live production PostgreSQL database

Execute migrations

Inspect real production traffic

Measure actual lock duration

Inspect the current production schema

Guarantee zero downtime

Guarantee rollback correctness when schema information is missing

Implement the complete PostgreSQL grammar



The system provides static migration safety intelligence, not a guarantee of production behavior.



🔭 Future Possibilities



Potential future extensions could include:



PostgreSQL schema introspection

CI/CD integration

Migration approval workflows

Production telemetry integration

Historical migration analysis

Database dependency graphs

Organization-level policy configuration



These are intentionally outside the current MVP scope.

