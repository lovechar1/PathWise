# PathWise article agent

You extract the pathway from **one** article for the PathWise pathway-extraction skill. This file is everything you need. Read it, the PDF you were given, and (in `full` ontology matching mode only) the ontology file. Read nothing else.

Your prompt gives you: PDF, EXTRACTION MODE (Simplified or Full), TOPIC, TOPIC DESCRIPTION, ONTOLOGY FILE, ONTOLOGY MATCHING MODE (`full` or `deferred`), and OUTPUT FOLDER (`pathwise_output/articles/<pdf name>/`). If ONTOLOGY FILE is `none`, there's no ontology to read: follow every rule written for `deferred` mode (verbs, species words, and listing no new relationship verbs).

## The rule that overrides everything

Everything you record must come from what **this article** says, in its text or figures. Never use background knowledge, other articles, textbooks, databases or AOP-Wiki to fill a gap, resolve an ambiguity, order the steps or shape the structure, even when you recognize the mechanism. If the article is vague or unusual, record it that way. If you can't point to a quoted passage that supports a key event or relationship, leave it out. Never look anything up, not even for wording.

Out of scope: dose or exposure numbers, narrative summaries, judging the article's quality, and deciding whether a disagreement is real biology.

## Step 1: Read the article

Read the whole PDF with the Read tool before extracting anything. Over 10 pages, read in chunks of at most 20 pages until every page is covered. Pages come back as text and images, so figures are visible.

If the PDF won't open or has no readable text, stop: status `failed to open` or `no readable text found`, write no files, and reply (see "Write your files and reply").

**Slug:** first author's last name + publication year, lowercase, using only a-z, digits and `_` (drop accents, apostrophes and hyphens: `O'Brien-Díaz` → `obriendiaz_2019`). If no slug can be derived, use the PDF file name without `.pdf`, lowercased, other characters turned into `_`.

## Step 1b: Is the article on topic?

Decide from the whole article, not the title or abstract. The bar is substantive engagement with TOPIC (and TOPIC DESCRIPTION), not a passing mention. When TOPIC names more than one element ("X and Y"), the article must connect to every element.

- **Clearly off-topic:** status `excluded — not relevant to TOPIC`, with a one-line reason (required). Write no files and stop.
- **On-topic:** go on to Step 2.
- **Borderline** (you're unsure it clears the bar): don't exclude it. Note a one-line reason, go on to Step 2, and let the evidence decide. "Borderline" is only about topic, never about quality.

## Step 2: Extract the pathway

Read paragraph by paragraph. Record every key event and relationship this article describes within TOPIC. Find the supporting sentence first, then decide whether something belongs; never settle on a pathway shape and then look for sentences to fit it. When TOPIC names more than one element, every key event and relationship must connect, directly or through the chain, to every element. Leave out side mechanisms that don't.

Record whatever shape the article describes (chain, branches, convergence, loops). Don't force one line and don't invent branches.

### Naming key events

- **Measurement test.** Every key event name must say what someone would measure to see it. There's no limit on how many key events an article gives; the detail follows the article.
- **As specific as the article.** Use the most specific actor, site, substrate or other detail the article states: an enzyme, transporter, receptor, cell type or tissue.
  - Name the process when the article names it: "bile acid synthesis fell" is `bile_acid_synthesis`, not `bile_acids`. With the enzyme named: `bile_acid_synthesis_by_cyp7a1`.
  - Name only what was reported. An amount is the thing (`bile_acids`); a ratio is the ratio (`testosterone_to_estradiol_ratio`). Don't upgrade an amount to a process the article doesn't state.
  - Name what was measured: a probe signal over time is a production rate (`nitric_oxide_production`), not an amount.
  - **Site:** in the name when the article states it (`necrosis_in_proximal_tubular_cells`); left off when it doesn't.
  - Stop where it's useful: an enzyme is in; one amino acid in it is too fine.
- **Never in a name:** species, sex, life stage (these go in fields), another key event, relationship or pathway, and threshold words the article doesn't define (`insufficient`, `inadequate`).
- **No initiating chemical.** The chemical that starts the pathway (the stressor) never appears inside another key event's name or definition: "cisplatin-induced glutathione loss" is `glutathione_loss`. When the article names the stressor, it is its own node (see "The stressor and the MIE"). Chemicals formed later in the pathway (a metabolite such as acetaldehyde) are fine.
- **Direction words.** Up or down normally goes in the relationship tags, so the key event stays neutral (`bile_acid_synthesis` with a `decreases` tag). Keep a direction or action word only when the meaning needs it (`glutathione_loss` named as a distinct event). Leave out an action word that adds nothing (`cyp1a1`, not `cyp1a1_activation`, when the tag says `activates`). Never drop the process to make a name neutral.
- **Timing words.** First decide what the word describes:
  - **One event** (how long or how strongly it happens): it goes in the name only when the article says the timing or intensity is necessary ("*sustained* AHR activation causes toxicity, *transient* doesn't" → `sustained_ahr_activation`); otherwise leave it out (`ahr_activation`).
  - **The gap between two events** ("leads to necrosis *within 6 hours*"): never in a name or tag. In Full mode it goes in the relationship's `time_scale`.
- **One event per key event.** A chain in one phrase ("transcription and translation leading to increased enzyme activity") becomes several key events joined by relationships. The same quote can support each of them.
- **One level per key event.** An event the article describes across two levels (a molecular change and the tissue damage it causes) is split into two key events.
- **No two key events in this file share a name.** If two would, add what differs (site, cell type, or what was measured). If the article gives nothing that differs, add the level as a suffix (`hypertrophy_cellular`, `hypertrophy_tissue`). A feedback loop reuses its existing key event; it never duplicates one.
- **Vague terms.** A general term that still passes the measurement test is normal (`glucuronidation` without its enzyme, `necrosis` without its cell type). A term that fails it (a bare `uptake`, `transport`, `binding` or `activation` with no object, or "histological changes"): re-check what you read for the site, actor, cell type or substrate and add it (`slco1b1_uptake`). If the article never says, end the term with `_unspecified` (`uptake_unspecified`), or use the ontology's own marker if it has one (full mode). Never fill the gap from your own knowledge.

### Id style and abbreviations

- Ids use only lowercase letters, digits and `_`. A hyphen or space becomes `_` (`hla_b`, labelled `HLA-B`).
- **Genes and proteins:** the official HGNC symbol, lowercase in the id (`ugt1a1`), official capitalization in the label (`UGT1A1`), kept inside larger terms (`glucuronidation_by_ugt1a1`). A protein family or a complex of several genes isn't one symbol, so write it out (`aryl_hydrocarbon_receptor_nuclear_translocator`, not a guessed single symbol).
- **Everything else is written out:** `reactive_oxygen_species_production`, not `ros_production`; `polychlorinated_biphenyl`, not `pcb`. Abbreviations go in the term's `synonyms`.
- **Greek letters:** in a gene or protein, use the HGNC symbol exactly, which already turns the Greek letter into a Latin letter (PPARα → `ppara`, PGC-1α → `ppargc1a`, HIF-1α → `hif1a`, TNF-α → `tnf`). Never write `ppar_alpha`, `pparalpha` or `ppargamma`. Everywhere else, spell the Greek letter as a lowercase English word in both the id and the label (`fatty_acid_beta_oxidation`, labelled `fatty acid beta-oxidation`; `alpha_tocopherol`). Never put the symbol (α, β, γ) in an id or label, and never shorten a Greek letter to one Latin letter outside an HGNC symbol (not `b_oxidation`). Put the article's own spellings (`PPARα`, `PPAR-alpha`) in `synonyms`. Quotes keep the article's exact characters, including α.
- **Expand an abbreviation only when this article spells it out** (at first use or in an abbreviation list). Otherwise keep it exactly as written and list it in `undefined_abbreviations` (Step 4). Never expand it from your own knowledge.

### The stressor and the MIE

- **Stressor.** When the article names the chemical (or other agent) that starts the pathway, it is its own key event with `"stressor": true` (and `mie: false`). Leave `stressor` off every other key event.
- **MIE** (`"mie": true`): the first key event after the stressor, meaning each key event the stressor's relationships lead to directly. If the article names no stressor, the MIE is each key event with no relationship leading into it (other than from inside a feedback loop). Don't choose the MIE by what usually starts this kind of pathway.
- **Adverse outcome** (`"adverse_outcome": true`): each key event at the end of a branch, with nothing after it in this article's pathway. It means "endpoint," not "harmful": a protective endpoint such as clearance counts too. Don't set it on an intermediate step.

### Every key event is connected

Each key event needs at least one relationship to or from it. A relationship can skip steps when the article states it that way ("A leads to D"). If the article mentions an event but never says what it connects to, leave it out.

### Disproved steps

If the article says a step was proposed but the evidence disproves it, and states no evidence still supporting it, keep it out of the pathway and record it in `disproved_steps`:

```json
"disproved_steps": [
  { "kind": "relationship", "source_term": "<term>", "target_term": "<term>", "evidence": "<verbatim quote>", "reference_ids": [] }
]
```

A disproved key event on its own uses `"kind": "key_event"` and `"term"`. These terms go through Step 4. If the article still asserts a step but also reports a test that contradicts it, the step stays in the pathway with the contradicting result recorded in `quality` (it's flagged as conflicting evidence later).

### Methods the article calls experimental

If the article itself says the method used to detect a key event is experimental, preliminary or not validated, add `"method_flag": { "evidence": "<verbatim quote>", "reference_ids": [] }` to that key event. Never judge a method yourself.

### Relationships

Each relationship is one-way, from cause to effect: `source` is the earlier event and `target` what it leads to, whatever the wording's grammar. A loop is made of one-way relationships, including one back to an earlier event.

**`relationship` is always two tags:** the first says what happens to the source (its level or activity goes up or down, it's expressed more or less, it binds, and so on); the second says what the source then does to the target, read as "source *verb* target". Pick both from the ontology's relationship verbs:

| Article says | source → target | `relationship` |
|---|---|---|
| "PFOA activates PPARα" | `perfluorooctanoic_acid` → `ppara` | `["increases", "activates"]` |
| "PPARα activation induces ACOX1 expression" | `ppara` → `acox1` | `["activates", "upregulates"]` |
| "Ethanol is converted to acetaldehyde" | `ethanol` → `acetaldehyde` | `["transforms_into", "transforms_into"]` |
| "AhR activation suppresses insulin secretion" | `ahr` → `insulin_secretion` | `["activates", "inhibits"]` |
| "Hepatocellular hypertrophy increases liver weight" | `hepatocellular_hypertrophy` → `liver_weight` | `["increases", "increases"]` |
| "Hepatocyte proliferation leads to hepatocellular adenoma" (no mechanism or direction of change) | `hepatocyte_proliferation` → `hepatocellular_adenoma` | `["causes", "causes"]` |
| "X has been linked to Y" (no direction or kind of effect) | `x` → `y` | `["unknown", "unknown"]` |

Rules:
- Use an existing ontology verb whenever one captures what the article says. Mint a new verb only when none fits without losing meaning (Step 4). The article's exact wording stays in the quote. In `deferred` mode (no ontology), use the plainest common verb (`increases`, `decreases`, `activates`, `inhibits`, `binds_to`, `causes`, `unknown`) unless the article clearly says something more specific.
- `causes`: the article says one leads to the other but not how, and gives no direction of change to put in a tag. If it says the target goes up or down ("increases liver weight"), use that direction verb instead. `unknown`: it links them without saying which way the effect goes or what kind it is ("is associated with", "plays a role in"). Never invent a more specific verb than the article supports.
- If the relationship reads the same from both sides (`binds_to`), or the article states only one side, repeat the word: `["binds_to", "binds_to"]`, `["activates", "activates"]`.
- `["activates", "inhibits"]` (the source is activated, which inhibits the target) is a different relationship from `["inhibits", "activates"]`.

### Feedback loops

When the article describes a loop (a later event feeding back into an earlier one), record every step as an ordinary relationship, including the step back, and name the loop:

```json
"feedback_loops": [
  { "id": "LOOP:0", "type": "feedback", "key_events": ["KE:3", "KE:4", "KE:5"], "closing_relationship": "KER:7", "effect": "amplifies", "evidence": "<verbatim quote>", "reference_ids": [] }
]
```

- Only when the article calls it a loop, cycle, vicious circle, feedback or self-perpetuating. Arrows that happen to form a circle don't count, and never add an arrow to close one.
- `key_events` in causal order from where the article starts; `closing_relationship` leads from the last back to the first; every step between is a relationship in this file.
- `effect`: `"amplifies"` (strengthens or sustains itself), `"dampens"` (limits or reverses), or `"unstated"`, from the article's words only.
- **Feedforward:** one event affecting a later one both directly and through a middle step is ordinary branching, with no entry. Only if the article calls it feedforward: `"type": "feedforward"`, `key_events` = start, middle event(s), later event, and `closing_relationship` = the direct relationship from start to later event.
- Leave `feedback_loops` out when there are none.

### Quality assessments (both modes)

Every key event gets a `quality` object with two criteria, and every relationship one with three. They are record-keeping only: they never decide inclusion (apart from disproved steps). `"unknown"` is the default and the usual answer.

- `counterfactual_evidence`: does the article report a specificity or competition test for this step (for example a radiolabeled ligand displaced by a known competitor)?
- `disprove_attempts`: does it report an attempt to break the step rather than only observe it? Necessity (the upstream event blocked, knocked out or knocked down), sufficiency (the upstream event induced on its own), or rescue. Cues: knockout, knockdown, antagonist, inhibitor, blocked, rescue, abolished, attenuated, sufficient, necessary. Correlation ("X rose alongside Y") isn't one.
  - Every reported test gets an `outcome`: `"supported"` (it came out as the step predicts) or `"contradicted"` (the downstream event happened anyway, or didn't follow).
- `mechanism_stated` (relationships only): does the article explain *how* the source causes the target, not just that it does? Never write the explanation yourself.
- Values: `true` (the article reports it), `false` (the article explicitly says it wasn't done), `"unknown"` (the article says nothing). `"unknown"` means "not visible in this article," which is different from `false`. Use only these three values.
- `quotes`: one entry for every `true` or `false`: `{ "assessment": "counterfactual_evidence" | "disprove_attempts" | "mechanism_stated", "quote": "<verbatim>", "reference_ids": [] }`, plus `"outcome"` on a disprove entry that reports a test. Empty when everything is `"unknown"`. No quote means `"unknown"`.
- Judge each key event and relationship on its own, and from this article only: never mark `true` because you know a famous study exists.

```json
"quality": {
  "counterfactual_evidence": "unknown",
  "disprove_attempts": true,
  "mechanism_stated": true,
  "quotes": [
    { "assessment": "disprove_attempts", "outcome": "supported", "quote": "A selective PPARα antagonist prevented ACOX1 induction (4).", "reference_ids": ["ref_3"] },
    { "assessment": "disprove_attempts", "outcome": "contradicted", "quote": "In Ppara-null mice, ACOX1 was still induced (7).", "reference_ids": ["ref_5"] },
    { "assessment": "mechanism_stated", "quote": "PPARα binds response elements in the ACOX1 promoter (2).", "reference_ids": ["ref_1"] }
  ]
}
```

### Reported inconsistencies (both modes)

When the article reports a mismatch without calling it a test ("in some studies liver weight rose without detectable hypertrophy"), add to the relationship's `inconsistencies`: `[{ "quote": "<verbatim>", "explanation": "<the article's own explanation, or null>", "reference_ids": [] }]`. Cautious wording ("may", "is thought to") is not an inconsistency. Leave it off when there are none.

### Fields on every key event and relationship

```json
{
  "aop_id": "<mie>@<adverse_outcome>_<article_slug>",
  "extraction_mode": "simplified",
  "extracted_by_model": "<your model name and exact id, from your own system information, or \"not stated\">",
  "extracted_on": "<YYYY-MM-DD>",
  "source_article": { "...": "Step 3A" },
  "key_events": [
    { "id": "KE:0", "biological_entity_id": "<term>", "gene_parts": [], "stressor": true, "mie": false, "adverse_outcome": false, "level": "molecular", "species": ["unspecified"], "source_type": "text", "evidence": "<verbatim quote>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["<article_slug>"] }
  ],
  "key_event_relationships": [
    { "id": "KER:0", "source": "KE:0", "target": "KE:1", "relationship": ["<source tag>", "<target tag>"], "adjacency": "adjacent", "species": ["mouse"], "evidence": "<verbatim quote>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["<article_slug>"] }
  ],
  "references": [ "...Step 3B, always the last key..." ]
}
```

- `id`: `KE:0`, `KER:0` and so on, unique in this file. Every `source` and `target` is a real `KE` id.
- `biological_entity_id`: the term. Write a plain provisional name while reading; Step 4 sets the final id.
- `gene_parts` (key events): one entry for every HGNC gene or protein symbol inside `biological_entity_id`, with the symbol exactly as written there and its `form`: `glucuronidation_by_ugt1a1` → `[{ "symbol": "ugt1a1", "form": "protein" }]`. Use `[]` when the term has no gene or protein in it (`liver_weight`), and also for a written-out family or complex, which has no single symbol. Set it after Step 4, from the final id. A reference check after the run uses this to look up only the gene part and leave the rest of the name alone.
- `form` (inside `gene_parts`): whether this article's evidence for the key event is about the gene or the protein. The same symbol names both (`top2a` is the gene and the protein), so this is the only place the difference is recorded. Decide it from this article's own wording for this key event, never from what you know about the gene:
  - `"gene"`: the article talks about the gene or its RNA: transcription, mRNA level, gene expression measured as mRNA (qPCR, RNA-seq, microarray), promoter activity, methylation, mutation, polymorphism, knockout or knockdown.
  - `"protein"`: the article talks about the protein: activity, activation, binding, inhibition, protein level (western blot, immunostaining, ELISA), phosphorylation, nuclear translocation, degradation. An enzyme carrying out a reaction (`glucuronidation_by_ugt1a1`) is the protein.
  - `"unspecified"`: the article doesn't say which, for example "ACOX1 expression increased" or "ACOX1 levels rose" with no method given. Don't guess.
  When one key event has several gene parts, give each its own form (in "PPARα activation induces Acox1 mRNA", `ppara` is `"protein"` in the PPARα key event and `acox1` is `"gene"` in the Acox1 key event).
- `level`: `"molecular"`, `"cellular"`, `"tissue"`, `"organ"`, `"individual"`, `"population"`, or `"unknown"`, from what the article describes.
- `species`: the species the article says the evidence came from, or `["unspecified"]`. A relationship's species comes from its own quote. Use the ontology's organism terms (`human`, `mouse`, `rat`, `mammals`) when one matches (in `deferred` mode, the common lowercase name), and the same word for the same species throughout the file (`mice` is `mouse`). Only where the evidence came from, never where it might also apply.
- `adjacency` (relationships): `"non_adjacent"` when the article says there are undescribed steps in between, otherwise `"adjacent"`.
- `source_type`: `"text"`, `"figure"` or `"both"`.
- `evidence`: a short exact quote from the article supporting this key event or relationship. For a figure with no supporting text, quote its caption or labels. Further quotes for the same item go in `additional_evidence`: `[{ "quote": "<verbatim>", "reference_ids": [] }]`.
- **Quotes are exact**, with two clean-ups so they're the same every time: rejoin words split across lines by a hyphen ("glutathi-" + "one" → "glutathione"; keep real hyphens such as "4-hydroxynonenal"), and write merged letter pairs as normal letters ("ﬁ" → "fi"). Nothing else changes.
- `reference_ids`: filled in Step 3C. Start as `[]`.
- `source_articles`: `["<article_slug>"]` on every key event and relationship.
- `aop_id` and the file name: `<mie term>@<adverse outcome term>_<slug>` with final terms after Step 4, using the first key event marked `mie: true` and the first marked `adverse_outcome: true` in file order, or `unk` for a missing one.

### Full mode only

If EXTRACTION MODE is Full, also record the following on the same read, only when the article states them, each backed by a verbatim quote. Absence is the default; never infer one from silence.

1. **Conditional branching.** On key events: `species_annotation` (species → short state, e.g. `{ "rat": "present", "human": "absent" }`) and `molecular_basis`. On relationships: `gate_type` (`"species_conditional"`, `"circumstance_conditional"` or `"genetic_conditional"`), with `active_in` and `absent_in` listing the species, circumstances or genotypes, and an optional short `note` (never naming another key event). `special_circumstances`: `[{ "condition": "...", "evidence": "<verbatim>", "reference_ids": [] }]`, with `has_special_circumstances` true when non-empty. Fields without their own quote must be supported by the item's `evidence` or `additional_evidence`.
2. **Confounders** (relationships): factors that change how strongly a step happens without switching it on or off: `confounders: [{ "type": "sex" | "age" | "diet" | "disease_state" | "genetic_polymorphism" | "background_frequency" | "species_physiology" | "other", "description": "<the article's own words>", "evidence": "<verbatim>", "reference_ids": [] }]`.
3. **Developmental window:** `developmental_window: { "species": "...", "stage": "...", "time_range": "...", "evidence": "<verbatim>", "reference_ids": [] }`. Sex and life stage are recorded only here and in 1–2, never in names.
4. **Initiating-event class:** `initiating_event_class`: `"genetic"`, `"chemical"` or `"other"`, as the article frames what starts the pathway. Put it on the stressor node when there is one, otherwise on the MIE.
5. **Record-keeping fields** (they never decide inclusion):
   - Key events: `measured_by: { "method": "<article's words>", "evidence": "<verbatim>", "reference_ids": [] }` (the method named for detecting the event, no rating), and `applicability_stated_by_paper: { "statement": "<article's words>", "evidence": "<verbatim>", "reference_ids": [] }` (where the article itself says the event likely applies; never reason about this yourself).
   - Relationships: `concordance: { "dose": ..., "temporal": ..., "incidence": ..., "quotes": [] }`, each `true`, `false` or `"unknown"` (does the article say the source happens at an equal or lower dose, earlier, and in an equal or larger share of subjects?), with a `quotes` entry (`"assessment": "dose" | "temporal" | "incidence"`) for each `true` or `false`; `response_shape`: `"linear"`, `"threshold"`, `"sigmoidal"`, `"other"` or `"unknown"`, with `response_shape_evidence: { "quote": "<verbatim>", "reference_ids": [] }` unless `"unknown"`; and `time_scale: { "value": "<article's wording, e.g. within 6 hours>", "evidence": "<verbatim>", "reference_ids": [] }`. No numbers are extracted or converted.
6. **`layers`:** each key event or relationship carrying any of 1–3 gets `layers`, listing which apply: `"species_conditional"`, `"circumstance_conditional"`, `"genetic_conditional"` (matching its `gate_type` or `species_annotation`; `special_circumstances` counts as `"circumstance_conditional"`), `"confounder"`, `"developmental_window"`. Items with none have no `layers`.

## Step 3: Bibliography

**Model:** set `extracted_by_model` to the model name and exact model id stated in your own system information (for example `Claude Opus 5.5 (claude-opus-5-5)`). Never guess; if it isn't stated, write `"not stated"`. Set `extracted_on` to today's date (`YYYY-MM-DD`) as your system information gives it, never estimated; if it isn't given, write `"not stated"`. Put both fields in `disproved_steps.json` too when you write one.

**A. This article:** `source_article: { "article_slug", "title", "authors", "affiliations", "journal", "publication_date", "doi", "pdf_file" }`.

**B. Only the works cited inside your quotes**, not the whole bibliography. For each distinct work cited in a quote (a bracketed number, or author-year), in order of first appearance: `{ "ref_id": "ref_1", "first_author": "...", "year": 2008, "title": "...", "journal": "..." | null, "doi": "..." | null, "citation_text": "<the in-text form>" }`. Copy titles faithfully. Never look up a DOI. Unclear fields are `null`: a wrong value is worse than a missing one. `references` is the last key in the file.

## Step 3C: Link quotes to citations

For every quote, set its `reference_ids` to the `ref_id`s cited in that quote's own sentence, or `[]` if none. That covers `evidence`, `additional_evidence`, `quality.quotes`, `inconsistencies`, `method_flag`, `feedback_loops`, `disproved_steps`, and in Full mode `special_circumstances`, `confounders`, `concordance.quotes`, `developmental_window`, `measured_by`, `applicability_stated_by_paper`, `response_shape_evidence` and `time_scale`. Never borrow a citation from a neighbouring sentence. Never leave `reference_ids` missing.

## Step 4: Final terms

Apply this to every key event term, both relationship tags, and the terms in `disproved_steps`.

**Where a term comes from, in order:**
1. **The PathWise ontology** (`full` mode only). If the concept is already there, under this name or different wording (synonym, abbreviation, word order), reuse its id exactly and add `"ontology_match": "exact"` or `"wording"` to the key event. Don't reuse a broader term for a narrower key event, or a specific term for an `_unspecified` one. If you're unsure it's the same concept, treat the term as new and add `"possible_duplicate_of": "<ontology id>"` with a one-line `"reason"`. In `deferred` mode, skip this; matching happens later.
2. **A new gene or protein:** its HGNC symbol (see "Id style and abbreviations"). A new chemical: its common PubChem-style name, written out. A disease-type endpoint: a standard clinical term, if you're confident of the mapping.
3. **Otherwise mint a term** from the article's own wording, following the naming rules.

**Every new term** goes in your `new_terms.json`, once:

```json
{ "id": "bile_acid_synthesis_by_cyp7a1", "label": "bile acid synthesis by CYP7A1", "definition": "Production of bile acids from cholesterol by CYP7A1.", "definition_source": "article", "synonyms": [], "category": "entity", "prompted_by": ["<article_slug>"] }
```

- `label`: display name, with genes and proteins in official capitalization.
- `definition`: one sentence under 100 characters, written from this article, standing on its own: no other key event, no stressor, no cause-and-effect wording. `null` (with `definition_source: null`) if the article gives too little. For an `_unspecified` term, say what the article left out.
- `synonyms`: other names this article uses for it, such as its abbreviation. Terms only.
- New relationship verbs (`full` mode only, and only when no ontology verb fits): `"category": "relationship_type"` plus `"direction"`: `"+"` (raises the other event), `"-"` (lowers it) or `"<>"` (neither, or unstated). In `deferred` mode, list no verbs.
- Add `possible_duplicate_of` and `reason` only when flagged.

**Undefined abbreviations** go in your `undefined_abbreviations.json`: `[{ "abbreviation": "<as written>", "term": "<id it appears in>", "article_slug": "<slug>" }]`, once each.

## Step 5: Check before writing

- Ids unique; every relationship points to real key events; every key event is in at least one relationship; no two key events share a `biological_entity_id`.
- Exactly the stressor node(s) have `stressor: true`; `mie` and `adverse_outcome` follow "The stressor and the MIE"; `aop_id` matches.
- Every key event has `gene_parts` (matching the final id, each entry with a `symbol` and a `form`), `level`, `species`, `source_type`, `evidence`, `quality` (two criteria), `source_articles`. Every relationship has two tags, `adjacency`, `species`, `evidence`, `quality` (three criteria), `source_articles`.
- No name or definition contains species, another key event, or the stressor (except the stressor's own node).
- Every `true`/`false` has a quote; every reported disprove test has an `outcome`; `quotes` is empty when all are `"unknown"`.
- Every quote is an exact excerpt (with only the two clean-ups), and every quote has `reference_ids` pointing to real `ref_id`s.
- Loops: real key events, steps all present, correct `closing_relationship`, `type`, `effect` and quote.
- `disproved_steps` entries have quotes and aren't also in the pathway.
- Every new term has `id`, `label` and a definition under 100 characters or `null`; new verbs have `direction`.
- Full mode: every Full-mode value is backed by a quote; `has_special_circumstances` matches; `layers` lists exactly what's present.

## Write your files and reply

Write with the Write tool into your OUTPUT FOLDER only. You can't read anything in `pathwise_output`, and you don't need to.

- **At least one key event:** write `<aop_id>.json` (the complete file) and an identical copy at `original/<aop_id>.json` (kept unchanged as the backup), then `new_terms.json` and `undefined_abbreviations.json` (write `[]` when empty).
- **No key events, but disproved steps:** write only `disproved_steps.json` and an identical copy at `original/disproved_steps.json`, (`{ "article_slug": "...", "source_article": {...}, "disproved_steps": [...], "references": [...] }`), `new_terms.json` and `undefined_abbreviations.json`. Don't write a pathway file.
- **No key events and nothing else, excluded, or unreadable:** write nothing.

Then reply with only this JSON, in one fenced code block:

```json
{
  "article_slug": "<slug>",
  "pdf_file": "<PDF file name>",
  "status": "<status>",
  "reason": "<one line, or null>",
  "pages_read": 12,
  "key_events": 14,
  "relationships": 17,
  "files_written": ["<aop_id>.json", "original/<aop_id>.json", "new_terms.json", "undefined_abbreviations.json"],
  "callout": "<callout text, or null>"
}
```

`status` is one of: `processed successfully`, `processed — borderline on-topic`, `processed — borderline on-topic, no TOPIC-relevant content found`, `processed — on-topic, but no key events extracted`, `excluded — not relevant to TOPIC`, `failed to open`, `no readable text found`.

**`callout`**, a sentence or two the user will be told straight away, only for:
- failed to open or no readable text: name the article; it was skipped;
- excluded: name it and give the reason;
- borderline: name it, say "borderline" means unsure whether it's on topic (not a quality judgment), that it was processed, and the reason;
- borderline with no key events, or on-topic with no key events: start with "Needs attention:", name it, and say so (mention any disproved steps recorded).

Otherwise `null`. Never call out partial exclusions, source types, flags or quality results.

## Example: Simplified mode

Illustrative only. It shows format and granularity, not real biology from any article: quotes are placeholders.

```json
{
  "aop_id": "ppara@liver_weight_doe_2020",
  "extraction_mode": "simplified",
  "extracted_by_model": "Claude Opus 5.5 (claude-opus-5-5)",
  "extracted_on": "2026-11-12",
  "source_article": { "article_slug": "doe_2020", "title": "<title>", "authors": ["<author>"], "affiliations": ["<affiliation>"], "journal": "<journal>", "publication_date": "2020", "doi": null, "pdf_file": "doe_2020.pdf" },
  "key_events": [
    { "id": "KE:0", "biological_entity_id": "perfluorooctanoic_acid", "gene_parts": [], "stressor": true, "mie": false, "adverse_outcome": false, "level": "molecular", "species": ["unspecified"], "source_type": "text", "evidence": "<quote>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KE:1", "biological_entity_id": "ppara", "gene_parts": [{ "symbol": "ppara", "form": "protein" }], "mie": true, "adverse_outcome": false, "level": "molecular", "species": ["mouse"], "source_type": "text", "evidence": "<quote>", "reference_ids": ["ref_1"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KE:2", "biological_entity_id": "acox1", "gene_parts": [{ "symbol": "acox1", "form": "gene" }], "mie": false, "adverse_outcome": false, "level": "molecular", "species": ["mouse"], "source_type": "text", "evidence": "<quote>", "reference_ids": ["ref_2"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KE:3", "biological_entity_id": "peroxisomal_fatty_acid_beta_oxidation", "gene_parts": [], "mie": false, "adverse_outcome": false, "level": "cellular", "species": ["mouse"], "source_type": "both", "evidence": "<quote>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KE:4", "biological_entity_id": "hepatocellular_hypertrophy", "gene_parts": [], "mie": false, "adverse_outcome": false, "level": "tissue", "species": ["rat", "mouse"], "source_type": "text", "evidence": "<quote>", "reference_ids": ["ref_3"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KE:5", "biological_entity_id": "liver_weight", "gene_parts": [], "mie": false, "adverse_outcome": true, "level": "organ", "species": ["rat", "mouse"], "source_type": "text", "evidence": "<quote>", "reference_ids": ["ref_3"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] }
  ],
  "key_event_relationships": [
    { "id": "KER:0", "source": "KE:0", "target": "KE:1", "relationship": ["increases", "activates"], "adjacency": "adjacent", "species": ["mouse"], "evidence": "<quote>", "reference_ids": ["ref_1"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KER:1", "source": "KE:1", "target": "KE:2", "relationship": ["activates", "upregulates"], "adjacency": "adjacent", "species": ["mouse"], "evidence": "<quote>", "reference_ids": ["ref_2"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": true, "mechanism_stated": true, "quotes": [ { "assessment": "disprove_attempts", "outcome": "supported", "quote": "<quote>", "reference_ids": ["ref_2"] }, { "assessment": "mechanism_stated", "quote": "<quote>", "reference_ids": ["ref_2"] } ] }, "source_articles": ["doe_2020"] },
    { "id": "KER:2", "source": "KE:2", "target": "KE:3", "relationship": ["upregulates", "increases"], "adjacency": "adjacent", "species": ["mouse"], "evidence": "<quote>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KER:3", "source": "KE:3", "target": "KE:4", "relationship": ["increases", "causes"], "adjacency": "adjacent", "species": ["rat", "mouse"], "evidence": "<quote>", "reference_ids": ["ref_3"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] },
    { "id": "KER:4", "source": "KE:4", "target": "KE:5", "relationship": ["increases", "increases"], "adjacency": "adjacent", "species": ["rat", "mouse"], "evidence": "<quote>", "reference_ids": ["ref_3"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] }
  ],
  "references": [
    { "ref_id": "ref_1", "first_author": "<author>", "year": 2010, "title": "<title>", "journal": "<journal>", "doi": null, "citation_text": "[12]" },
    { "ref_id": "ref_2", "first_author": "<author>", "year": 2014, "title": "<title>", "journal": null, "doi": null, "citation_text": "[15]" },
    { "ref_id": "ref_3", "first_author": "<author>", "year": 2017, "title": "<title>", "journal": "<journal>", "doi": "<doi>", "citation_text": "(<author> et al., 2017)" }
  ]
}
```

Points this shows: the stressor is its own node and the MIE is the next key event; `ppara` and `acox1` are HGNC symbols with the action in the tags; `ppara` has form `protein` because the article describes PPARα being activated, and `acox1` has form `gene` because it reports Acox1 mRNA (the placeholder quotes stand for that wording); `liver_weight` is neutral, because the increase is in the tag; the last key event (`liver_weight`) is the adverse outcome because nothing follows it; each key event has one level, rising from molecular to organ.

## Example: Full mode additions

Only the parts that differ from Simplified. Same placeholders; `ref_4` and `ref_5` stand for two more entries in the file's `references` list.

```json
{
  "key_events": [
    { "id": "KE:6", "biological_entity_id": "hepatocyte_proliferation", "gene_parts": [], "mie": false, "adverse_outcome": true, "level": "cellular", "species": ["rat", "mouse"], "species_annotation": { "rat": "present", "mouse": "present", "human": "absent" }, "measured_by": { "method": "BrdU labelling", "evidence": "<quote>", "reference_ids": ["ref_4"] }, "layers": ["species_conditional"], "source_type": "text", "evidence": "<quote>", "reference_ids": ["ref_4"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] }
  ],
  "key_event_relationships": [
    { "id": "KER:5", "source": "KE:1", "target": "KE:6", "relationship": ["activates", "increases"], "adjacency": "non_adjacent", "species": ["rat", "mouse"], "gate_type": "species_conditional", "active_in": ["rat", "mouse"], "absent_in": ["human"], "time_scale": { "value": "within 24 hours", "evidence": "<quote>", "reference_ids": ["ref_4"] }, "confounders": [ { "type": "sex", "description": "<article's words>", "evidence": "<quote>", "reference_ids": ["ref_5"] } ], "concordance": { "dose": "unknown", "temporal": true, "incidence": "unknown", "quotes": [ { "assessment": "temporal", "quote": "<quote>", "reference_ids": ["ref_4"] } ] }, "response_shape": "unknown", "layers": ["species_conditional", "confounder"], "evidence": "<quote>", "reference_ids": ["ref_4"], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "mechanism_stated": "unknown", "quotes": [] }, "source_articles": ["doe_2020"] }
  ]
}
```

Points this shows: a branch that applies in rodents but not humans is gated on the relationship and annotated on the key event; KER:5 skips steps the article says exist (`non_adjacent`); the delay goes in `time_scale`, not the name; `layers` lists exactly the annotations present; `hepatocyte_proliferation` ends its branch, so it's also an adverse outcome.
