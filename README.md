# clawhub-analysis

Empirical analysis of the ClawHub skill ecosystem — 13,729 skills, clustered by interface pattern, evaluated for reliability.

This repository backs the claim that **67% of agent capabilities fail in practice** and provides the data, methodology, and reproducible analysis behind it.

---

## Key Findings

| Metric | Value | Source |
|--------|-------|--------|
| Skills analyzed | 13,729 | ClawHub registry snapshot 2026-02 |
| Agent failure rate | 67% | Execution trace sampling (n=2,847) |
| Skills with no typed interface | 89% | Frontmatter field analysis |
| Skills with permission over-declaration | 41% | Permission vs. behavior diff |
| Skills with undeclared dependencies | 34% | Dependency graph analysis |
| Mean input types per skill | 1.2 | Frontmatter + body NLP extraction |

## The Problem

ClawHub hosts 13,729 skills — the largest public registry of agent capabilities. But quantity ≠ quality. Our analysis found:

1. **67% of sampled skill invocations fail.** The primary failure modes: missing prerequisites (28%), ambiguous instructions (22%), permission errors at runtime (11%), and environment drift (6%).

2. **89% of skills declare no typed interface.** Without input/output types, the runtime cannot pre-validate composition. Skills that look compatible by name often fail by shape.

3. **41% over-declare permissions.** Skills requesting `network + filesystem + subprocess` when they only use `curl`. This expands attack surface with zero functional benefit.

These numbers are why we believe the ecosystem needs a type layer.

## Methodology

### Data Collection

- **Source**: ClawHub registry API (`clawhub search --limit 15000 --format json`), snapshot taken 2026-02-08.
- **Scope**: All publicly listed skills. Extensions, workflows, and workspace templates were excluded (separate analysis pending).
- **Fields extracted**: `name`, `description`, `metadata.openclaw.requires`, `metadata.openclaw.install`, SKILL.md body text.

### Clustering

We clustered skills by inferred interface pattern using a three-stage pipeline:

1. **Frontmatter extraction** — Parse YAML frontmatter for `requires.bins`, `requires.env`, `install[].kind`.
2. **Body NLP** — Extract input/output types from SKILL.md body using pattern matching on command sections (regex for `curl`, `jq`, file operations, etc.) + a lightweight classifier trained on 500 manually labeled skills.
3. **K-means clustering** — TF-IDF vectors of (inferred input type, inferred output type, required bins, required env) → k=12 clusters, silhouette score 0.61.

### Failure Rate Measurement

- **Sample**: 2,847 skills (stratified random sample across all 12 clusters).
- **Method**: Each skill was invoked in a sandboxed OpenClaw environment with the declared prerequisites installed. Success = the skill produced parseable output matching its stated purpose within 60 seconds. Failure = timeout, crash, missing dependency, or output that did not match the stated description.
- **Limitations**: Some skills require paid API keys or specific hardware. These were marked as `untestable` (n=412) and excluded from the failure rate calculation. The effective sample for the 67% figure is n=2,435.

### Permission Analysis

- **Method**: For each skill, we compared `metadata.openclaw.requires` (declared) against actual behavior inferred from SKILL.md body text (detected `curl`, `tee`, `>`, `exec`, `pip install`, etc.).
- **Over-declaration**: Skill declares a permission not exercised in the body.
- **Under-declaration**: Skill exercises a capability not declared in frontmatter.

## Data Files

```
data/
├── registry-snapshot.csv        # 13,729 rows: name, description, requires, install
├── cluster-assignments.csv      # skill → cluster_id, inferred_input, inferred_output
├── failure-rates-by-cluster.csv # cluster_id, n, success_rate, primary_failure_mode
├── permission-drift.csv         # skill, declared_perms, detected_perms, drift_type
├── type-frequency.json          # Aggregated type distributions (input/output/context)
└── README.md                    # Data dictionary
```

## Type Distribution (Aggregated)

### Input Types

| Type | Frequency | Example Skills |
|------|-----------|----------------|
| String | 62% | summarizer, translator, search |
| FilePath | 18% | doc-converter, file-parser, image-resize |
| URL | 12% | web-scraper, link-checker, api-fetcher |
| JSON | 5% | data-transformer, schema-validator |
| RepositoryRef | 4% | deploy-and-notify, repo-scanner |
| CodeDiff | 3% | pr-guardian, code-reviewer |

### Output Types

| Type | Frequency | Example Skills |
|------|-----------|----------------|
| Markdown | 45% | summarizer, pr-summarizer, doc-converter |
| JSON | 28% | data-extractor, api-caller, file-parser |
| PlainText | 15% | translator, formatter, shell-runner |
| File | 8% | image-resize, pdf-merge, export-csv |
| Notification | 3% | slack-poster, teams-notifier |
| OperationStatus | 1% | docker-build, kubectl-apply |

### Context Requirements

| Context | Frequency | Notes |
|---------|-----------|-------|
| GitHubCredentials | 38% | GITHUB_TOKEN — by far the most common |
| Git | 34% | Local git binary |
| Docker | 22% | Docker daemon access |
| GenericAPIKey | 20% | Various API keys (overlaps with above) |
| Node.js / Python | 18% | Runtime language dependency |
| Kubernetes | 15% | kubectl + cluster context |
| SlackCredentials | 12% | SLACK_BOT_TOKEN |

## Reproducibility

### Requirements

```
Python >= 3.10
pandas >= 2.0
scikit-learn >= 1.3
matplotlib >= 3.8
seaborn >= 0.13
jupyter >= 4.0
```

### Run

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01-data-overview.ipynb
```

Or run the full pipeline:

```bash
python scripts/run_analysis.py --data data/registry-snapshot.csv --output figures/
```

## Relationship to effectorHQ

This analysis motivated the creation of the [Effector type system](https://github.com/effectorHQ/effector-spec). The core argument:

- If 67% of skills fail because of untyped interfaces, missing prerequisites, and permission mismatches...
- ...then the fix is a type layer that makes these properties explicit, checkable, and composable.

The type frequency data in `data/type-frequency.json` directly informed the [`effector-types`](https://github.com/effectorHQ/effector-types) standard library — every type in the stdlib has an empirical grounding in this corpus.

## Citation

If you use this data in research or writing:

```
effectorHQ. (2026). ClawHub Skill Ecosystem Analysis: Type Distributions
and Failure Rates Across 13,729 Agent Capabilities.
https://github.com/effectorHQ/clawhub-analysis
```

## License

This project is currently licensed under the [Apache License, Version 2.0](LICENSE.md) 。
