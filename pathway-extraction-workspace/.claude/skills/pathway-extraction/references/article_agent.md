# PathWise article agent

You extract the pathway from **one** article for the PathWise pathway-extraction skill. This file is everything you need. Read it, the PDF you were given, and (in `full` ontology matching mode only) the ontology file. Read nothing else.

Your prompt gives you: PDF, EXTRACTION MODE (Simplified or Full), TOPIC, TOPIC DESCRIPTION, ONTOLOGY FILE, ONTOLOGY MATCHING MODE (`full` or `deferred`), and OUTPUT FOLDER (`pathwise_output/articles/<pdf name>/`). If ONTOLOGY FILE is `none`, there's no ontology to read: treat the ontology matching mode as `deferred`.

Short forms used below: MIE is the molecular initiating event; `KE:n` and `KER:n` are the ids of key events and key event relationships; HGNC is the official gene-symbol list.

## The rule that overrides everything

Everything you record must come from what **this article** says, in its text or figures. Never use background knowledge, other articles, textbooks, databases or AOP-Wiki to fill a gap, resolve an ambiguity, order the steps or shape the structure, even when you recognize the mechanism. If the article is vague or unusual, record it that way. If you can't point to a quoted passage that supports a key event or relationship, leave it out. Never look anything up, not even for wording.

General knowledge may be used only to rename something the article already names, never to add a fact about the biology: to name a family or group when the article lists some of its members (see the enzymes and families rule under "Naming key events"), to write an organ adjective as its noun (`hepatic` as `liver`), and for the naming sources in Step 4 (official gene symbol, common chemical name, standard clinical term). Use these only when you are sure; otherwise keep the article's own wording.

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

Read paragraph by paragraph. Record every key event and relationship this article describes within TOPIC. Find the supporting sentence first, then decide whether something belongs; never settle on a pathway shape and then look for sentences to fit it. When TOPIC names more than one element, every key event and relationship must connect, directly or through the chain, to every element. Leave out anything that doesn't.

Record whatever shape the article describes (chain, branches, convergence, loops). Don't force one line and don't invent branches.

### What to record

- **Every step the article states.** If the article says A leads to B and B leads to C, record both steps. Don't link A straight to C unless the article states A leading to C itself.
- **One relationship per arrow.** A sentence with a condition ("if `<X>` is low, `<A>` acts on `<B>`, causing `<C>`") gives one relationship for each arrow in it: `<X>` → `<B>`, `<A>` → `<B>` and `<B>` → `<C>`. The condition is a key event of its own, with its own arrow, upstream of what it makes possible.
- **Introduction and background.** A statement from the introduction or background is recorded only when the article itself presents it as a step of the pathway it describes. General statistics or epidemiology about the exposure (for example what share of cases go on to a later outcome) are never recorded, as key events or as endpoints.
- **Only what the article presents as part of the pathway.** A key event or relationship is recorded when the article presents it as a step of the pathway, whether it spends one sentence on it or five. Something the article only mentions, without tying it into the pathway (for example a marker that was measured, or a side remark), is not recorded. Something the article presents as proposed, suggested, possible or unsure ("may", "is thought to", "it has been suggested") is not recorded as a fact, and none of its detail goes into a key event name (see "Naming key events").

### Naming key events

Here "tags" are the two verbs of a relationship (see "Relationships"), and `form` and `gene_parts` are defined under "Fields".

- **Measurement test.** Every key event name must say what someone would measure to see it. Review articles rarely say how something was measured, so judge from the wording what could be measured.
- **As specific as the article.** Whenever the article states it as established, the name carries the most specific entity, process, actor (enzyme, transporter, receptor and so on), gene, cell type, tissue or compartment it gives for that event. Never add a word the article doesn't state for that event, even one that seems obvious (if it never says "mitochondrial", the name never says it).
  - **Two terms for one event.** When the article uses a general and a more specific term for the same event, use the more specific one. When the two differ on different points (one gives the site, the other the kind of change) and the article ties them to the same event, combine the most specific parts of both into one key event. When the article treats them as different steps or different kinds of change, keep two key events. Only parts the article presents as established are combined.
  - **Amount or process.** Name only what was reported. An amount is the thing (`bile_acids`); a ratio is the ratio (`testosterone_to_estradiol_ratio`). Don't turn an amount into a process the article doesn't state, and don't reduce a stated process to an amount. If the article says the process ("bile acid synthesis fell"), the name says it (`bile_acid_synthesis`).
  - **Name what was measured.** A probe signal over time is a production rate (`nitric_oxide_production`) only when the article says production, formation or release; otherwise name the thing (`nitric_oxide`).
  - **Same wording, same key event.** The same statement always gets the same name, and one file never holds two key events for the same wording.
  - **Stop where it's useful.** Never go below a gene, protein, metabolite, cell type or compartment (no residues or domains).
- **Name structure.** Build every name from these parts, in this order, using only the parts the article gives:
  `[<timing>_][<state>_]<entity>_<process>_by_<actor>_in_<site>[_<level>]`
  - **Timing** (optional): a timing or intensity word, only when the article says it is necessary (see "Timing words").
  - **State** (optional): a modified form that acts next, only when the article says so (see "Process words"): `phosphorylated_<entity>_translocation_to_<site>`.
  - **Entity:** what the event is about: a gene or protein (HGNC symbol), a metabolite, a lipid, a complex or another thing.
  - **Process:** only when it passes "Process words" below.
  - **Actor** (after `by`): what carries the process out, when stated: an enzyme, transporter, receptor, channel, transcription factor, kinase or other.
  - **Site** (after `in`): where it happens, when stated: an organ, tissue, cell type or compartment (`in_liver`, `in_hepatocytes`, `in_cytosol`).
  - **Level** (optional suffix): only to separate two otherwise identical names (see "No two key events in this file share a name").
  - **Movement:** use `_from_<origin>` when the process word is release, efflux or export, otherwise `_to_<destination>`: `<entity>_translocation_to_<site>`, `<entity>_release_from_<site>`. A movement name takes no `in_<site>`.
  - A name holds one entity, at most one process, at most one actor and at most one site; the one exception is a `_ratio` name, which holds two entities (`testosterone_to_estradiol_ratio`). It is at most 70 characters: if a name is longer, drop the actor first, then the site, then the process, never the entity.
  - **A site is never a prefix** (no `mitochondrial_…`, `hepatic_…`). A site is introduced only by `in`, `to` or `from`, never `on`.
  - **Organs** are written as the organ noun, using the ontology's `locations` words when it has them (`liver`, not `hepatic`). Cell types are plural (`hepatocytes`, `kupffer_cells`); a compartment is its plain noun (`mitochondria`, `cytosol`, `nucleus`).
  - **This order applies to terms you mint.** A term that is already in the ontology is reused exactly as written, even when its name doesn't follow this order (an established phrase such as "mitochondrial dysfunction" can live in the ontology as it is); see Step 4.
- **Process words.** A word that says what happens to the thing goes in the name only if the relationship tags can't carry the same biology without it. The test: leave the word out and read the arrows. If the meaning changes, keep the word.
  - **Leave out** a word that only says something went up, went down or became active, because a tag already says it: activation, inhibition, induction, upregulation, downregulation, increase, decrease, elevation, reduction, accumulation, expression. The tags `activates`, `inhibits`, `upregulates`, `downregulates`, `increases` and `decreases` already say these (`cyp1a1`, not `cyp1a1_activation`). `expression` is carried by `form` in `gene_parts` and the tags. The one exception is a process word kept with a timing word (see "Timing words").
  - **Keep** a word that says *how* an amount or state changed, when the article uses it, because `increases` and `decreases` only mean a general change in level: made (production, formation, synthesis), used up or removed (depletion, degradation), moved (release, uptake, secretion, translocation), chemically modified (phosphorylation, ubiquitination, acetylation and the like).
  - **Exception:** leave a kept word out when the verb on the arrow the article states it with already says it (`phosphorylates`, `translocates_to`, `binds_to`, `transforms_into`). When a named actor phosphorylates a target, the verb carries it and the key event is the bare target; when no actor is named, the word stays in the name.
  - **When you aren't sure** whether a word only says up, down or active, or names a distinct kind of change, keep the article's own word.
  - **A modified form** (phosphorylated, oxidized) is written as a state prefix (`phosphorylated_<entity>_…`), and only when the article says that form is what acts next.
  - **A bare gene or protein name** means its activity or level; `form` in `gene_parts` and the tags say which.
- **Level words.** A word that only restates the level (cellular, molecular, tissue, organ) stays out of the name, because `level` carries it. Keep one only when it adds biological information, for example when the article contrasts the same event at two levels. When the cell type is stated, name that instead (`necrosis_in_hepatocytes`). The one other exception is the level suffix that separates two otherwise identical names (see the rule "No two key events in this file share a name" below).
- **A compound the relationship already names.** When the relationship into a key event comes from a compound that is itself a key event, don't repeat that compound in the target's name (`<compound>` → `protein_adducts`, not `<compound>_protein_adducts`). An actor or site that is also a key event may still appear in a name.
- **Enzymes, other actors and families.**
  - One actor stated: it goes in the name (`_by_<symbol>`).
  - **Several members of one family** stated, or the article says several family members act but names only one: name the family in the key event. This applies only in the actor position (`by_<actor>`) or when the article itself groups the members under one word; entities joined by "and" are split (see "One measurable change per key event"). Use the article's own group word when it has one, otherwise an established family name (this includes writing out a family abbreviation the article only gives as an abbreviation), written out, in the singular, with underscores. List the members the article names in `family_members` (see "Fields"), marking `"primary": true` on the one the article calls the main or primary one (`false` on all of them when it names none). `gene_parts` stays `[]` for a family, because it only holds symbols that are inside the id.
  - Several actors from different families are separate key events, because a name holds one actor.
- **One measurable change per key event.** A key event is one measurable change in one thing. Judge from the wording what would plausibly be measured separately: a different assay, readout, cell type or compartment.
  - When the article joins several items with "and", "or", a comma, "then" or "followed by", give each item its own key event when each could be measured on its own. They are parallel key events, and each gets its own relationship to the shared source or target.
  - Keep them as one only when the article measures them together as a single class (one combined readout).
  - A chain in one phrase ("X is released and then moves to Y") becomes one key event per step, joined by relationships. The same quote can support each of them.
- **One level per key event.** An event the article describes across two levels (a molecular change and the tissue damage it causes) is split into two key events, each named on its own (`<entity>_<process>_in_<cell type>` for the molecular change, `injury_in_<organ>` for the damage).
- **Never in a name:** species, sex, life stage, the whole name of another key event, a relationship or pathway, and threshold words the article doesn't define (`insufficient`, `inadequate`). An actor or site that is also a key event may appear in a name.
- **No initiating chemical.** The chemical that starts the pathway (the stressor) never appears inside another key event's name or definition: "cisplatin-induced glutathione loss" is `glutathione_loss`. When the article names the stressor, it is its own node (see "The stressor, the MIE and the endpoint"). Chemicals formed later in the pathway (a metabolite such as acetaldehyde) are fine as their own key events, and follow the compound rule above.
- **Direction.** Up or down goes in the relationship tags, so the key event stays neutral (`bile_acid_synthesis` with a `decreases` tag). Never drop a process the test above says to keep just to make a name neutral.
- **Timing words.** First decide what the word describes:
  - **One event** (how long or how strongly it happens): it goes in the name only when the article says the timing or intensity is necessary ("*sustained* AHR activation causes toxicity, *transient* doesn't" → `sustained_ahr_activation`); otherwise leave it out (`ahr`). This is the one case where `activation` stays in a name: the timing word needs the process it describes.
  - **The gap between two events** ("leads to necrosis *within 6 hours*"): never in a name or tag. In Full mode it goes in the relationship's `time_scale`.
- **No two key events in this file share a name.** If two would, add what differs (site, cell type, or what was measured). If the article gives nothing that differs, add the level as a suffix (`hypertrophy_cellular`, `hypertrophy_tissue`). A feedback loop reuses its existing key event; it never duplicates one.
- **Vague terms.** A general term that still passes the measurement test is normal (`glucuronidation` without its enzyme, `necrosis` without its cell type). A term that fails it (a bare `uptake`, `transport` or `binding` with no object, or "histological changes"): re-check what you read for the site, actor, cell type or substrate and add it (`slco1b1_uptake`). If the article never says, end the term with `_unspecified` (`uptake_unspecified`), or use the ontology's own marker if it has one (full mode). Never fill the gap from your own knowledge.

### Id style and abbreviations

- Ids use only lowercase letters, digits and `_`. A hyphen or space becomes `_` (`hla_b`, labelled `HLA-B`).
- **Genes and proteins:** the official HGNC symbol, lowercase in the id (`ugt1a1`), official capitalization in the label (`UGT1A1`), kept inside larger terms (`glucuronidation_by_ugt1a1`). A protein family or a complex of several genes isn't one symbol, so write it out (`nuclear_factor_kappa_b`, not a guessed single symbol). If you aren't sure which official symbol an alias stands for, write the alias exactly as the article does (lowercase, underscores); the reference check at the end of the run renames it.
- **Expand an abbreviation only when this article spells it out** (at first use or in an abbreviation list). Otherwise keep it exactly as written and list it in `undefined_abbreviations` (Step 4). Never expand it from your own knowledge; the exceptions are the allowed uses listed at the top of this file.
- **Everything else is written out** (when the article spells it out): `reactive_oxygen_species_production`, not `ros_production`; `polychlorinated_biphenyl`, not `pcb`. Abbreviations go in the term's `synonyms`.
- **Greek letters in a gene or protein:** use the HGNC symbol exactly, which already turns the Greek letter into a Latin letter (PPARα → `ppara`, PGC-1α → `ppargc1a`, HIF-1α → `hif1a`, TNF-α → `tnf`). Never write `ppar_alpha`, `pparalpha` or `ppargamma`.
- **Greek letters everywhere else:** spell the letter as a lowercase English word in both the id and the label (`fatty_acid_beta_oxidation`, labelled `fatty acid beta-oxidation`; `alpha_tocopherol`). Never put the symbol (α, β, γ) in an id or label, and never shorten a Greek letter to one Latin letter outside an HGNC symbol (not `b_oxidation`). Put the article's own spellings (`PPARα`, `PPAR-alpha`) in `synonyms`. Quotes keep the article's exact characters, including α.

### The stressor, the MIE and the endpoint

- **Stressor.** When the article names the chemical (or other agent) that starts the pathway, it is its own key event with `"stressor": true` (and `mie: false`). Every other key event has `"stressor": false`.
- **MIE** (`"mie": true`): the first key event after the stressor, meaning each key event the stressor's relationships lead to directly. If the article names no stressor, the MIE is each key event with no relationship leading into it, other than from inside a feedback loop and other than a condition. Don't choose the MIE by what usually starts this kind of pathway. A condition is a key event that only makes a step possible (for example a protective molecule being used up): it feeds into the route with its own arrow, and is never an MIE.
- **Endpoint** (`"endpoint": true`): each key event at the end of a branch of this article's pathway that leads toward what TOPIC is about, with nothing after it. The pathway goes as far as the article takes it: the endpoint is the furthest event the article links to the pathway, whatever its level. If the article stops at a cell-level event, that event is the endpoint. "Endpoint" means the end of the article's chain, not "harmful": a protective endpoint such as clearance counts too. Don't set it on an intermediate step, and never on something stated only as background (see "What to record").

### Every key event is on a route

Each key event needs at least one relationship to or from it, and must lie on a stated route, through other key events, to an endpoint. The route starts at the stressor, an MIE, or a condition (see above). A branch that ends away from the endpoints, neither reaching one nor coming back into the route, is left out. A branch that leaves and comes back into the route (including a loop) is part of it.

### Disproved steps

If the article says a step was proposed but the evidence disproves it, and states no evidence still supporting it, keep it out of the pathway and record it in `disproved_steps`. A disproved relationship has `kind` `"relationship"`, `source_term` and `target_term`; a disproved key event on its own has `kind` `"key_event"` and `term`. Each also has `evidence` and `reference_ids` (see the shapes table under "The file layout"). These terms go through Step 4. If the article still asserts a step but also reports a test that contradicts it, the step stays in the pathway with the contradicting result recorded in `quality` (it's flagged as conflicting evidence later).

### Methods the article calls experimental

If the article itself says the method used to detect a key event is experimental, preliminary or not validated, set that key event's `method_flag` to `{ "evidence": "<verbatim quote>", "reference_ids": [] }`. It is `null` otherwise. Never judge a method yourself.

### Relationships

Each relationship is one-way, from cause to effect: `source` is the earlier event and `target` what it leads to, whatever the wording's grammar. A loop is made of one-way relationships, including one back to an earlier event.

**`relationship` is always two tags:** the first says what happens to the source (its level or activity goes up or down, it's expressed more or less, it binds, and so on); the second says what the source then does to the target, read as "source *verb* target". Pick both from the ontology's relationship verbs:

| Article says | source → target | `relationship` |
|---|---|---|
| "PFOA activates PPARα" | `perfluorooctanoic_acid` → `ppara` | `["increases", "activates"]` |
| "PPARα activation induces ACOX1 expression" | `ppara` → `acox1` | `["activates", "upregulates"]` |
| "Ethanol is converted to acetaldehyde" | `ethanol` → `acetaldehyde` | `["transforms_into", "transforms_into"]` |
| "AhR activation suppresses insulin secretion" | `ahr` → `insulin_secretion` | `["activates", "inhibits"]` |
| "Hypertrophy of hepatocytes increases liver weight" | `hypertrophy_in_hepatocytes` → `liver_weight` | `["increases", "increases"]` |
| "Proliferation of hepatocytes leads to adenoma of the liver" (no mechanism or direction of change) | `proliferation_in_hepatocytes` → `adenoma_in_liver` | `["causes", "causes"]` |
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
  {
    "id": "LOOP:0",
    "type": "feedback",
    "key_events": ["KE:3", "KE:4", "KE:5"],
    "closing_relationship": "KER:7",
    "effect": "amplifies",
    "evidence": "<verbatim quote>",
    "reference_ids": []
  }
]
```

- Only when the article calls it a loop, cycle, vicious circle, feedback or self-perpetuating. Arrows that happen to form a circle don't count, and never add an arrow to close one.
- `key_events` in causal order, starting at the loop event the article names first; `closing_relationship` leads from the last back to the first; every step between is a relationship in this file.
- `effect`: `"amplifies"` (strengthens or sustains itself), `"dampens"` (limits or reverses), or `"unstated"`, from the article's words only.
- **Feedforward:** one event affecting a later one both directly and through a middle step is ordinary branching, with no entry. Only if the article calls it feedforward: `"type": "feedforward"`, `key_events` = start, middle event(s), later event, and `closing_relationship` = the direct relationship from start to later event.
- `feedback_loops` is `[]` when there are none.

### Quality assessments (both modes)

Every key event gets a `quality` object with two criteria, and every relationship one with three. They are record-keeping only: they never decide inclusion (apart from disproved steps). `"unknown"` is the default and the usual answer.

- `counterfactual_evidence`: does the article report a specificity or competition test for this step (for example a radiolabeled ligand displaced by a known competitor)?
- `disprove_attempts`: does it report an attempt to break the step rather than only observe it? Necessity (the upstream event blocked, knocked out or knocked down), sufficiency (the upstream event induced on its own), or rescue. Cues: knockout, knockdown, antagonist, inhibitor, blocked, rescue, abolished, attenuated, sufficient, necessary. Correlation ("X rose alongside Y") isn't one.
  - Every reported test gets an `outcome`: `"supported"` (it came out as the step predicts) or `"contradicted"` (the downstream event happened anyway, or didn't follow).
- `mechanism_stated` (relationships only): does the article explain *how* the source causes the target, not just that it does? Never write the explanation yourself.
- Values: `true` (the article reports it), `false` (the article explicitly says it wasn't done), `"unknown"` (the article says nothing). `"unknown"` means "not visible in this article," which is different from `false`. Use only these three values.
- `quotes`: one entry for every `true` or `false`: `{ "assessment": "counterfactual_evidence" | "disprove_attempts" | "mechanism_stated", "quote": "<verbatim>", "reference_ids": [] }`, plus `"outcome"` (placed after `assessment`) on a disprove entry that reports a test. Empty when everything is `"unknown"`. No quote means `"unknown"`.
- Judge each key event and relationship on its own, and from this article only: never mark `true` because you know a famous study exists.

### Reported inconsistencies (both modes)

When the article reports a mismatch without calling it a test ("in some studies the first measure rose without the second"), add to the relationship's `inconsistencies` a `quote` and an `explanation` (the article's own, or `null`). Cautious wording ("may", "is thought to") is not an inconsistency. `inconsistencies` is `[]` when there are none.

## The file layout

Every pathway file has exactly the same layout, so files from different articles can be read and compared line by line.

1. **Write the file exactly like the template below:** two-space indentation, one field per line, every key in the template's order. Don't add a key and don't leave one out.
2. **Every field in the template for your mode is always present.** When the article doesn't state it, write `[]` for a list, `null` for text or an object, `false` for a true/false flag, and `"unknown"` where the template shows it. Never invent another marker. The only other values are the ones defined in this file: `["unspecified"]` for `species` and `"unknown"` for `level` when the article doesn't say, `"unspecified"` for a `form`, and `"not stated"` for `extracted_by_model` and `extracted_on`. A `source_article` detail you can't read is `null` (`[]` for `authors` and `affiliations`).
3. **Simplified mode writes only the fields in the Simplified template.** It doesn't write the Full-mode fields at all, not even empty. **Full mode** writes the Simplified fields and the Full-mode fields.
4. A list of plain words stays on one line (`"species": ["<species>"]`). Every object, and every list of objects, is spread over lines, one key per line. Braces written on one line elsewhere in this file only show which keys an object has; in the file, always spread them.
5. `references` is the last key.

### Template (Simplified fields)

Placeholders in `<angle brackets>` stand for real values. The template shows one key event and one relationship; write as many of each as the article needs, each in exactly this layout.

```json
{
  "aop_id": "<mie_term>@<endpoint_term>_<article_slug>",
  "extraction_mode": "<simplified or full>",
  "extracted_by_model": "<model name and exact id, or not stated>",
  "extracted_on": "<YYYY-MM-DD, or not stated>",
  "source_article": {
    "article_slug": "<slug>",
    "title": "<title>",
    "authors": ["<author>"],
    "affiliations": ["<affiliation>"],
    "journal": "<journal>",
    "publication_date": "<date>",
    "doi": null,
    "pdf_file": "<pdf file name>"
  },
  "key_events": [
    {
      "id": "KE:0",
      "biological_entity_id": "<term_id>",
      "gene_parts": [],
      "family_members": [],
      "stressor": false,
      "mie": false,
      "endpoint": false,
      "level": "<level>",
      "species": ["<species>"],
      "source_type": "<text, figure or both>",
      "evidence": "<verbatim quote>",
      "additional_evidence": [],
      "reference_ids": [],
      "ontology_match": null,
      "method_flag": null,
      "quality": {
        "counterfactual_evidence": "unknown",
        "disprove_attempts": "unknown",
        "quotes": []
      },
      "source_articles": ["<article_slug>"]
    }
  ],
  "key_event_relationships": [
    {
      "id": "KER:0",
      "source": "KE:0",
      "target": "KE:1",
      "relationship": ["<source tag>", "<target tag>"],
      "adjacency": "<adjacent or non_adjacent>",
      "species": ["<species>"],
      "evidence": "<verbatim quote>",
      "additional_evidence": [],
      "reference_ids": [],
      "quality": {
        "counterfactual_evidence": "unknown",
        "disprove_attempts": "unknown",
        "mechanism_stated": "unknown",
        "quotes": []
      },
      "inconsistencies": [],
      "source_articles": ["<article_slug>"]
    }
  ],
  "disproved_steps": [],
  "feedback_loops": [],
  "references": [
    {
      "ref_id": "ref_1",
      "first_author": "<author>",
      "year": 2000,
      "title": "<title>",
      "journal": null,
      "doi": null,
      "citation_text": "<in-text form>"
    }
  ]
}
```

### Full mode only: extra fields in the template

In Full mode, add these keys to every key event, between `quality` and `source_articles`, in this order:

```json
      "species_annotation": null,
      "molecular_basis": null,
      "initiating_event_class": null,
      "measured_by": null,
      "applicability_stated_by_paper": null,
      "developmental_window": null,
      "special_circumstances": [],
      "has_special_circumstances": false,
      "confounders": [],
      "layers": [],
```

and these to every relationship, between `inconsistencies` and `source_articles`, in this order:

```json
      "gate_type": null,
      "active_in": [],
      "absent_in": [],
      "note": null,
      "special_circumstances": [],
      "has_special_circumstances": false,
      "confounders": [],
      "concordance": {
        "dose": "unknown",
        "temporal": "unknown",
        "incidence": "unknown",
        "quotes": []
      },
      "response_shape": "unknown",
      "response_shape_evidence": null,
      "time_scale": null,
      "developmental_window": null,
      "layers": [],
```

### Shapes of objects and list entries

When a field holds something, its object or list entry is spread over lines in this key order, and every key is always present (the one exception is `outcome` in a `quality.quotes` entry, which appears only on a disprove entry that reports a test):

| Field | Keys, in order |
|---|---|
| `gene_parts` entry | `symbol`, `form` |
| `family_members` entry | `symbol`, `form`, `primary` |
| `additional_evidence` entry | `quote`, `reference_ids` |
| `quality.quotes` entry | `assessment`, `outcome` (only on a disprove entry that reports a test), `quote`, `reference_ids` |
| `method_flag` | `evidence`, `reference_ids` |
| `inconsistencies` entry | `quote`, `explanation`, `reference_ids` |
| `species_annotation` (Full) | one key per species, its short state as the value |
| `measured_by` (Full) | `method`, `evidence`, `reference_ids` |
| `applicability_stated_by_paper` (Full) | `statement`, `evidence`, `reference_ids` |
| `developmental_window` (Full) | `species`, `stage`, `time_range`, `evidence`, `reference_ids` |
| `special_circumstances` entry (Full) | `condition`, `evidence`, `reference_ids` |
| `confounders` entry (Full) | `type`, `description`, `evidence`, `reference_ids` |
| `concordance.quotes` entry (Full) | `assessment`, `quote`, `reference_ids` |
| `response_shape_evidence` (Full) | `quote`, `reference_ids` |
| `time_scale` (Full) | `value`, `evidence`, `reference_ids` |
| `disproved_steps` entry, kind `relationship` | `kind`, `source_term`, `target_term`, `evidence`, `reference_ids` |
| `disproved_steps` entry, kind `key_event` | `kind`, `term`, `evidence`, `reference_ids` |
| `feedback_loops` entry | `id`, `type`, `key_events`, `closing_relationship`, `effect`, `evidence`, `reference_ids` |
| `references` entry | `ref_id`, `first_author`, `year`, `title`, `journal`, `doi`, `citation_text` |

### `disproved_steps.json` (an article with no key events)

An article that has disproved steps but no key events writes this file instead of a pathway file, in the same layout:

```json
{
  "article_slug": "<slug>",
  "extracted_by_model": "<model name and exact id, or not stated>",
  "extracted_on": "<YYYY-MM-DD, or not stated>",
  "source_article": {
    "article_slug": "<slug>",
    "title": "<title>",
    "authors": ["<author>"],
    "affiliations": ["<affiliation>"],
    "journal": "<journal>",
    "publication_date": "<date>",
    "doi": null,
    "pdf_file": "<pdf file name>"
  },
  "disproved_steps": [
    {
      "kind": "relationship",
      "source_term": "<term>",
      "target_term": "<term>",
      "evidence": "<verbatim quote>",
      "reference_ids": []
    }
  ],
  "references": []
}
```

## Fields

- `id`: `KE:0`, `KER:0` and so on, unique in this file. Every `source` and `target` is a real `KE` id.
- `biological_entity_id`: the term. Write a plain provisional name while reading; Step 4 sets the final id.
- `gene_parts` (key events): one entry for every HGNC gene or protein symbol inside `biological_entity_id`, with the symbol exactly as written there and its `form`: `glucuronidation_by_ugt1a1` → `[{ "symbol": "ugt1a1", "form": "protein" }]`. Use `[]` when the term has no gene or protein in it (`liver_weight`), and also for a written-out family or complex, which has no single symbol. Set it after Step 4, from the final id. A reference check after the run uses this to look up only the gene part and leave the rest of the name alone.
- `family_members` (key events): when the key event is named by a family (see the enzymes and families rule under "Naming key events"), one entry for each member the article names: its HGNC symbol in lowercase, its `form` (as for `gene_parts`) and `primary` (`true` for the one the article calls the main or primary one, otherwise `false`). `[]` when the key event is not named by a family. It is never used to look up names and never changes when terms are relabeled.
- `form` (inside `gene_parts` and `family_members`): whether this article's evidence for the key event is about the gene or the protein. The same symbol names both (`top2a` is the gene and the protein), so this is the only place the difference is recorded. Decide it from this article's own wording for this key event, never from what you know about the gene:
  - `"gene"`: the article talks about the gene or its RNA: transcription, mRNA level, gene expression measured as mRNA (qPCR, RNA-seq, microarray), promoter activity, methylation, mutation, polymorphism, knockout or knockdown.
  - `"protein"`: the article talks about the protein: activity, activation, binding, inhibition, protein level (western blot, immunostaining, ELISA), phosphorylation, nuclear translocation, degradation. An enzyme carrying out a reaction (`glucuronidation_by_ugt1a1`) is the protein.
  - `"unspecified"`: the article doesn't say which, for example "ACOX1 expression increased" or "ACOX1 levels rose" with no method given. Don't guess.
  When one key event has several gene parts, give each its own form (a name holding two symbols, such as `<symbol a>_<process>_by_<symbol b>`, has two gene parts, each with its own `form`).
- `level`: `"molecular"`, `"cellular"`, `"tissue"`, `"organ"`, `"individual"`, `"population"`, or `"unknown"`, from what the article describes. A stressor's `level` is `"unknown"`.
- `species`: the species the article says the evidence came from, or `["unspecified"]`. A relationship's species comes from its own quote. Use the ontology's organism terms (`human`, `mouse`, `rat`, `mammals`) when one matches (in `deferred` mode, the common lowercase name), and the same word for the same species throughout the file (`mice` is `mouse`). Record only the species the evidence came from, never species it might also apply to.
- `adjacency` (relationships): `"non_adjacent"` when the article says there are undescribed steps in between, otherwise `"adjacent"`.
- `source_type` (key events only): `"text"`, `"figure"` or `"both"`. Relationships don't have it.
- `evidence`: a short exact quote from the article supporting this key event or relationship. For a figure with no supporting text, quote its caption or labels. Further quotes for the same item go in `additional_evidence`.
- **Quotes are exact**, with two clean-ups so they're the same every time: rejoin words split across lines by a hyphen ("glutathi-" + "one" → "glutathione"; keep real hyphens such as "4-hydroxynonenal"), and write merged letter pairs as normal letters ("ﬁ" → "fi"). Nothing else changes.
- `reference_ids`: filled in Step 3C. Start as `[]`.
- `source_articles`: `["<article_slug>"]` on every key event and relationship.
- `ontology_match`: `null`, or `"exact"` or `"wording"` for a key event whose term was reused from the ontology (Step 4).
- `aop_id` and the file name: `<mie_term>@<endpoint_term>_<article_slug>` with final terms after Step 4, using the first key event marked `mie: true` and the first marked `endpoint: true` in file order, or `unk` for a missing one. List key events in the order the article first presents them, and relationships in the order of their `evidence` quotes in the article.

### Full mode only

If EXTRACTION MODE is Full, also record the following on the same read, only when the article states them, each backed by a verbatim quote. Absence is the default and is written as the empty value from the layout rules above (`[]`, `null`, `false`, `"unknown"`); never infer anything from silence.

1. **Conditional branching.** On key events: `species_annotation` (each species → the article's short state word, such as `present` or `absent`) and `molecular_basis` (the article's own short phrase for the molecular reason a species differs, or `null`). On relationships: `gate_type` (`"species_conditional"`, `"circumstance_conditional"` or `"genetic_conditional"`), with `active_in` and `absent_in` listing the species, circumstances or genotypes, and an optional short `note` (never naming another key event). `special_circumstances` (on key events and relationships), with `has_special_circumstances` true when it is non-empty. Fields without their own quote must be supported by the item's `evidence` or `additional_evidence`.
2. **Confounders** (on key events and relationships): factors the article names that change how strongly a step happens, or how strongly or how much of a key event occurs, without switching it on or off. Each `confounders` entry has a `type` (`sex`, `age`, `diet`, `disease_state`, `genetic_polymorphism`, `background_frequency`, `species_physiology` or `other`) and a `description` in the article's own words. Record one on a relationship when it changes the strength of that step, and on a key event when it changes how much or how strongly that event occurs, including its baseline level.
3. **Developmental window** (on key events and relationships): `developmental_window` (the species, stage and time range the article gives). Sex and life stage are recorded only here and in 1–2, never in names.
4. **Initiating-event class:** `initiating_event_class`: `"genetic"`, `"chemical"` or `"other"`, as the article frames what starts the pathway. Put it on the stressor node when there is one, otherwise on each MIE. It is `null` on every other key event.
5. **Record-keeping fields** (they never decide inclusion):
   - Key events: `measured_by` (the method named for detecting the event, no rating) and `applicability_stated_by_paper` (where the article itself says the event likely applies; never reason about this yourself), each in the article's words.
   - Relationships: `concordance` (`dose`, `temporal` and `incidence`, each `true`, `false` or `"unknown"`: does the article say the source happens at an equal or lower dose, earlier, and in an equal or larger share of subjects?), with a `quotes` entry (`assessment` `dose`, `temporal` or `incidence`) for each `true` or `false`; `response_shape` (`"linear"`, `"threshold"`, `"sigmoidal"`, `"other"` or `"unknown"`), with `response_shape_evidence` unless it is `"unknown"` (then `null`); and `time_scale` (the article's wording, e.g. "within 6 hours"). Dose and exposure numbers are never extracted; write times as the article words them.
6. **`layers`:** each key event or relationship carrying any of 1–3 lists which apply: `"species_conditional"`, `"circumstance_conditional"`, `"genetic_conditional"` (matching its `gate_type` or `species_annotation`; `special_circumstances` counts as `"circumstance_conditional"`), `"confounder"`, `"developmental_window"`. Items with none have `"layers": []`.

## Step 3: Bibliography

**Model:** set `extracted_by_model` to the model name and exact model id stated in your own system information (for example `Claude Opus 5.5 (claude-opus-5-5)`). Never guess; if it isn't stated, write `"not stated"`. Set `extracted_on` to today's date (`YYYY-MM-DD`) as your system information gives it, never estimated; if it isn't given, write `"not stated"`.
**A. This article:** `source_article` (its keys are in the template).

**B. Only the works cited inside your quotes**, not the whole bibliography. For each distinct work cited in a quote (a bracketed number, or author-year), in order of first appearance in the quotes as they stand in your file: its `ref_id` (`ref_1`, `ref_2`, ...), `first_author`, `year`, `title`, `journal`, `doi` and `citation_text` (the in-text form). Copy titles faithfully. Never look up a DOI. Unclear fields are `null`: a wrong value is worse than a missing one.

## Step 3C: Link quotes to citations

For every quote, set its `reference_ids` to the `ref_id`s cited in that quote's own sentence, or `[]` if none. That covers `evidence`, `additional_evidence`, `quality.quotes`, `inconsistencies`, `method_flag`, `feedback_loops`, `disproved_steps`, and in Full mode `special_circumstances`, `confounders`, `concordance.quotes`, `developmental_window`, `measured_by`, `applicability_stated_by_paper`, `response_shape_evidence` and `time_scale`. Never borrow a citation from a neighbouring sentence.

## Step 4: Final terms

Apply this to every key event term, both relationship tags, and the terms in `disproved_steps`.

**Where a term comes from, in order:**
1. **The PathWise ontology** (`full` mode only). If the concept is already there, under this name or different wording (synonym, abbreviation, word order), reuse its id exactly and set `"ontology_match"` to `"exact"` or `"wording"` on the key event. Don't reuse a broader term for a narrower key event, or a specific term for an `_unspecified` one. If you're unsure it's the same concept, treat the term as new and set `possible_duplicate_of` to the ontology id, with a one-line `reason`, in its `new_terms.json` entry. In `deferred` mode, skip this; matching happens later.
2. **A new gene or protein:** its HGNC symbol (see "Id style and abbreviations"). A new chemical: its common PubChem-style name, written out. A disease-type endpoint: a standard clinical term, if you're confident of the mapping.
3. **Otherwise mint a term** from the article's own wording, following the naming rules.

**Every new term** goes in your `new_terms.json`, once, with every field present:

```json
[
  {
    "id": "<term_id>",
    "label": "<display name>",
    "definition": "<one sentence, or null>",
    "definition_source": "<article, or null>",
    "synonyms": [],
    "category": "<entity or relationship_type>",
    "direction": null,
    "prompted_by": ["<article_slug>"],
    "possible_duplicate_of": null,
    "reason": null
  }
]
```

- `label`: display name, with genes and proteins in official capitalization.
- `definition`: one sentence under 100 characters, written from this article, standing on its own: no other key event, no stressor, no cause-and-effect wording. `definition_source` is `"article"`, or `null` together with a `null` definition when the article gives too little. An `_unspecified` term always gets a definition that says what the article left out.
- `synonyms`: other names this article uses for it, such as its abbreviation. Terms only.
- New relationship verbs (`full` mode only, and only when no ontology verb fits): `"category": "relationship_type"` plus `"direction"`: `"+"` (raises the other event), `"-"` (lowers it) or `"<>"` (neither, or unstated). In `deferred` mode, list no verbs. `direction` is `null` for an entity.
- `possible_duplicate_of` and `reason` are `null` unless flagged.

**Undefined abbreviations** go in your `undefined_abbreviations.json`, once each (with the first term it appears in), written in the same layout (`[]` when there are none):

```json
[
  {
    "abbreviation": "<as written>",
    "term": "<id it appears in>",
    "article_slug": "<slug>"
  }
]
```

## Step 5: Check before writing

- Ids are unique; every relationship points to real key events; no two key events share a `biological_entity_id`.
- Every key event lies on a stated route to an endpoint, every stated step is recorded, and the article presents each one as part of the pathway (no background statistics, passing mentions or suggestions).
- Names follow "Naming key events": no word the article doesn't state, no site prefix, no level word that adds nothing, process words by the test, within 70 characters. No name or definition holds a species or the stressor (except the stressor's own node).
- Exactly the stressor node(s) have `stressor: true`; `mie`, `endpoint` and `aop_id` follow their rules; `gene_parts` matches the final ids.
- Every `true`/`false` has a quote; every reported disprove test has an `outcome`; every quote is an exact excerpt (the two clean-ups only) with `reference_ids` that point to real `ref_id`s.
- Loops and `disproved_steps` follow their sections; a disproved step is not also in the pathway.
- Every new term has all the fields in the `new_terms.json` layout, with a definition under 100 characters or `null`; new verbs have `direction`.
- Full mode: every Full-mode value is backed by a quote, and `has_special_circumstances` and `layers` match what is present.
- **Layout:** the file matches the template for your mode exactly: every key present and in order, two-space indentation, one field per line, `references` last, and no Full-mode key in Simplified mode.

## Write your files and reply

Write with the Write tool into your OUTPUT FOLDER only, in the layout above (two-space indentation, one field per line) for every JSON file. You can't read anything in `pathwise_output`, and you don't need to.

- **At least one key event:** write `<aop_id>.json` (the complete file) and an identical copy at `original/<aop_id>.json` (kept unchanged as the backup), then `new_terms.json` and `undefined_abbreviations.json` (write `[]` when empty).
- **No key events, but disproved steps:** write only `disproved_steps.json` and an identical copy at `original/disproved_steps.json` (laid out as in "`disproved_steps.json`" above), `new_terms.json` and `undefined_abbreviations.json`. Don't write a pathway file.
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

`status` is one of: `processed successfully`, `processed — borderline on-topic`, `processed — borderline on-topic, no TOPIC-relevant content found`, `processed — on-topic, but no key events extracted`, `excluded — not relevant to TOPIC`, `failed to open`, `no readable text found`. When nothing is written, `key_events` and `relationships` are 0 and `files_written` is `[]`. An article with only disproved steps uses the status `processed — on-topic, but no key events extracted`.

**`callout`**, a sentence or two the user will be told straight away, only for:
- failed to open or no readable text: name the article; it was skipped;
- excluded: name it and give the reason;
- borderline: name it, say "borderline" means unsure whether it's on topic (not a quality judgment), that it was processed, and the reason;
- borderline with no key events, or on-topic with no key events: start with "Needs attention:", name it, and say so (mention any disproved steps recorded).

Otherwise `null`. Never call out partial exclusions, source types, flags or quality results.
