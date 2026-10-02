# Maintainer Summary View — Output Template

This template formats triage inferences for presentation to human maintainers.
It enforces the architectural boundary: **Facts and Inferences must be visibly separated**, and every recommendation must expose its operational failure rationale.

---

## Single Issue Card Layout

```markdown
### [{{system_slug}} #{{number}}] {{title}}
**URL**: {{url}} · **Author**: @{{author}} · **State**: {{state}}

---

#### 1. Deterministic Facts (Verifiable Metadata)
* **Labels**: `{{labels_list}}`
* **Title Prefix**: `{{title_prefix}}`
* **Direct References**: {{direct_cross_refs_or_none}}
* **Citations**:
  > "{{citation_1}}"
  {{#citation_2}}> "{{citation_2}}"{{/citation_2}}

---

#### 2. Assistant Inference (Recommendation Only)
* **Suggested Band**: `{{band}}` (Confidence: **{{confidence}}**)
  * *Source*: {{source}} ({{#rule_name}}Rule: `{{rule_name}}`{{/rule_name}}{{#model}}Model: `{{model}}`{{/model}})
  * *Operational Rationale*: {{operational_rationale}}
  * *Reasons*:
    1. {{reason_1}}
    {{#reason_2}}2. {{reason_2}}{{/reason_2}}
* **Cross-System Analysis**: `{{cross_system.classification}}`
  {{#cross_system.target_system_slug}}* *Target System*: `{{cross_system.target_system_slug}}`{{/cross_system.target_system_slug}}
  * *Diagnosis*: {{cross_system.explanation}}
{{#border_ambiguity}}
* ⚠️ **Border Uncertainty Alert**: `{{border_ambiguity}}`
  * *Note*: Multiple evaluation runs or heuristics showed ambiguity on this edge. Maintainer review recommended.
{{/border_ambiguity}}

---

#### 3. Maintainer Actions (Human Decision Required)
- [ ] **Accept**: Confirm `{{band}}` and apply priority label.
- [ ] **Override**: Change band to `[ P0 | P1 | P2 | P3 ]` (requires reason).
{{#is_misplaced}}
- [ ] **Relocate ("Hogar + Vista")**: Notify `{{cross_system.target_system_slug}}` while maintaining custody in `{{system_slug}}`.
{{/is_misplaced}}
- [ ] **Defer / Needs Info**: Request reproduction or reporter clarification.
```

---

## Batch Triage Report Summary Header

When presenting a batch of triaged issues, render this top-level summary table:

```markdown
# 📊 Triage Batch Report — Run #{{run_id}}
*Generated at*: {{created_at}} · *Total Processed*: {{total_issues}}

| Metric | Count | Percentage |
| --- | --- | --- |
| **Deterministic Code Resolutions** (0 tokens, 100% stable) | {{deterministic_resolved}} | {{deterministic_pct}}% |
| **LLM Evaluated Inferences** (Grey area analysis) | {{llm_evaluated}} | {{llm_pct}}% |
| **Cross-System Implication / Misplaced Detected** | {{cross_system_count}} | {{cross_system_pct}}% |

### Band Distribution
* **P0 (Critical / Data Loss)**: {{band_distribution.P0}}
* **P1 (Hard Blocker, No Workaround)**: {{band_distribution.P1}}
* **P2 (Actionable, Workaround/Retry/Feature)**: {{band_distribution.P2}}
* **P3 (Docs, Chores, Cosmetic)**: {{band_distribution.P3}}

---
```
