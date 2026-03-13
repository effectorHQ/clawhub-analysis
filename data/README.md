# Data Dictionary

## registry-snapshot.csv

Full registry export from ClawHub API (2026-02-08 snapshot).

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Skill name (kebab-case) |
| `description` | string | Skill description from frontmatter |
| `emoji` | string | Display emoji |
| `requires_bins` | string (pipe-separated) | Required CLI binaries |
| `requires_env` | string (pipe-separated) | Required environment variables |
| `install_kinds` | string (pipe-separated) | Available install methods (brew, apt, manual, npm, pip) |
| `has_purpose` | bool | SKILL.md has Purpose section |
| `has_when_to_use` | bool | SKILL.md has When to Use section |
| `has_examples` | bool | SKILL.md has Examples section |
| `body_length` | int | Character count of SKILL.md body (excluding frontmatter) |
| `command_count` | int | Number of detected command/action sections |

## cluster-assignments.csv

K-means cluster labels for each skill (k=12, silhouette=0.61).

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Skill name |
| `cluster_id` | int | Cluster label (0-11) |
| `inferred_input` | string | Inferred primary input type |
| `inferred_output` | string | Inferred primary output type |
| `inferred_context` | string | Inferred context requirement |
| `confidence` | float | Classification confidence (0-1) |

## failure-rates-by-cluster.csv

Success/failure rates by cluster from sandbox execution.

| Column | Type | Description |
|--------|------|-------------|
| `cluster_id` | int | Cluster label |
| `cluster_label` | string | Human-readable cluster name |
| `n_total` | int | Total skills in cluster |
| `n_sampled` | int | Skills actually tested |
| `n_success` | int | Successful invocations |
| `n_fail` | int | Failed invocations |
| `n_untestable` | int | Excluded (paid APIs, hardware) |
| `success_rate` | float | n_success / (n_sampled - n_untestable) |
| `primary_failure_mode` | string | Most common failure reason in cluster |

## permission-drift.csv

Permission analysis — declared vs. detected capabilities.

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Skill name |
| `declared_network` | bool | Frontmatter declares network access |
| `detected_network` | bool | Body contains curl/wget/fetch patterns |
| `declared_filesystem` | string | Declared fs permissions |
| `detected_filesystem` | string | Detected fs operations (read/write) |
| `declared_subprocess` | bool | Declares subprocess |
| `detected_subprocess` | bool | Detects exec/spawn patterns |
| `drift_type` | string | `none`, `over-declared`, `under-declared`, `both` |

## type-frequency.json

Aggregated type distributions. This file directly informed the `effector-types` standard library.

```json
{
  "input": { "String": 0.62, "FilePath": 0.18, ... },
  "output": { "Markdown": 0.45, "JSON": 0.28, ... },
  "context": { "GitHubCredentials": 0.38, "Git": 0.34, ... },
  "metadata": {
    "corpus_size": 13729,
    "snapshot_date": "2026-02-08",
    "clustering_k": 12,
    "silhouette_score": 0.61
  }
}
```
