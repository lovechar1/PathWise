# Extraction Procedure — Full Mechanics

This is the specification SKILL.md points to. Follow it precisely — the discipline here (verbatim evidence, causal source/target ordering, the reuse-or-mint terminology process) is what makes the merged output trustworthy across articles written by different authors in different styles.

## Scope

Always in scope, in both extraction modes: pathway extraction (key events, key event relationships, MIE/AO flags), a flat bibliography per article, terminology alignment across the batch, per-KE/KER citation linking (Step 3C), two quality assessments on every key event and relationship (see "Quality assessments" in Step 2), and a final tally of how many articles *and* how many distinct cited sources support each key event and relationship.

Always out of scope, by deliberate design choice, not because anything is unknown: review-type/certainty-language tagging and any automated judgment about whether a disagreement between articles is real biology or an extraction error — flag it, don't resolve it. Don't add any of this on your own initiative even if it looks easy; ask the user first if they want scope expanded.

### Extraction mode: Simplified vs. Full

Ask which mode the user wants first, before any other input and before Step 1, and tell them the choice is final for the run — it changes what Step 2 looks for while reading, not just what gets shown afterward, so switching later means re-reading every PDF.

**Simplified** — extract only the core chain: MIEs, KEs, KERs, AO flags, evidence quotes, citation links, and the tally. Don't go looking for species/circumstance qualifiers, confounder language, developmental-timing statements, or initiating-event-class distinctions — if a sentence happens to carry one, don't chase it down, just extract the underlying KE/KER as usual and move on.

**Full** — everything in Simplified, plus four additional kinds of annotation, captured only when the article's own text states them (same verbatim-evidence discipline as everything else — if you can't quote it, don't add it):

1. **Species-specific / conditional branching** — a KE/KER that only applies to certain species, or only under a stated non-species condition (e.g. a minor enzyme pathway that matters "under specific circumstances," a genotype-driven fast/slow-metabolizer split). Fields: `species_annotation` (object, species → short state string) and `molecular_basis` (string) on the KE; `gate_type`, `active_in`, `absent_in`, and an optional `note` (short free-text) on the KER for structural on/off-in-this-species-or-condition branching (`gate_type` is one of `"species_conditional"`, `"circumstance_conditional"`, or `"genetic_conditional"`; `active_in` and `absent_in` list the species, circumstances, or genotypes the relationship does or doesn't operate in, matching the `gate_type`); `special_circumstances` (array of `{ "condition": "...", "evidence": "<verbatim quote>", "reference_ids": [] }`) for non-species qualifiers that don't cleanly fit the species fields; `has_special_circumstances` (true/false, derived from whether that array is non-empty). `species_annotation`, `molecular_basis`, `gate_type`, `active_in`, `absent_in`, and `note` carry no quote of their own: the KE's or KER's own `evidence` (or `additional_evidence`) quote must support them, and if no quote does, leave them out.
2. **Confounders** — a variable that shifts a KER's probability or magnitude without gating whether it exists at all (sex, background malformation frequency, species physiology, a genetic polymorphism that changes metabolic rate rather than switching a pathway on/off). KER-level field: `confounders` (array of `{ "type": "sex" | "genetic_polymorphism" | "background_frequency" | "species_physiology" | "other", "description": "...", "evidence": "<verbatim quote>", "reference_ids": [] }`).
3. **Developmental/temporal window** — a KE/KER that's only operative within a stated developmental stage or time window. Field: `developmental_window` (object: `{ "species": "...", "stage": "...", "time_range": "...", "evidence": "<verbatim quote>", "reference_ids": [] }`) on the KE or KER.
4. **Initiating-event class** — on MIE key events only (`"mie": true`), whether the article frames this MIE's origin as genetic, chemical, or something else (disease-driven, endogenous, etc.). Field: `initiating_event_class`: `"genetic" | "chemical" | "other"`, grounded in the KE's `evidence` quote, or in an `additional_evidence` quote if the classification is stated in a different sentence — never inferred from what kind of entity it is.

Any KE/KER carrying #1, #2, or #3 also gets a `layers` field: an array drawn from `["species_conditional", "confounder", "developmental_window"]`, naming which of these three apply. This is the field a future visualizer toggle would filter on — it doesn't drive any behavior in this skill itself. A KE/KER with none of these stays untagged (no `layers` field), meaning "core pathway, always shown."

Why these four and not others, and why Case Study 2-style genetic/chemical convergence isn't in this list: an article describing two mechanisms (e.g. a chemical branch and a genetic-susceptibility branch) that converge on a shared downstream KE is just ordinary branching/convergence topology — Step 2 already encodes that natively as separate KE chains meeting at one node. It doesn't need a special field; only genuinely *conditional* content (present in this species but not that one, active only past a threshold, magnitude shifted by a modifier, valid only in a time window) needs one of the four fields above.

## Step 1: Read each article

Once, at the start of the run (not again for each article), check whether the `output/` folder already exists and has files in it. If it does, it's from an earlier run: ask the user for a new output folder name (for example `output_2`) and use that for everything below, and don't overwrite the old one without an explicit yes. Reruns (for example after switching extraction mode) would otherwise overwrite `new_terms.json` and the review decisions saved in it. Wherever this document says `output/`, it means whichever folder was chosen.

If ARTICLES names a folder, list every PDF in it now and process in filename order; record the lockdown check result (first line, see "Before anything else" in SKILL.md), the full resolved list, and the extraction mode chosen, in the run log before starting, so there's a record of exactly what got processed this run and how.

For each PDF: use the Read tool. If it's more than 10 pages, pass a page range (max 20 pages per call) and read in sequential chunks until the whole document is covered — don't assume one call gets everything. Read the entire article before starting Step 2; a connection between something introduced early and something described later would otherwise get missed. Each page returns as both text and an image, so figures/diagrams are visible as you read — no separate step needed for that.

If a PDF fails to open or returns no readable content (likely scanned/image-only), note it in the run log, tell the user right away (see "Per-article callouts" below), and move to the next article rather than stopping the whole run.

Derive this article's slug now: first author's last name + publication year, lowercase (e.g. `smith_2019`). Use it consistently everywhere this article is referenced. If a later article in the batch would produce a slug already used by an earlier one, give the later article a `-b` suffix (then `-c`, and so on); the first article keeps the plain slug, because its file is already written and shouldn't be renamed. If the PDF is unreadable and no slug can be derived, use the PDF's filename (without `.pdf`) in the run log and in the callout.

## Step 1b: Confirm this article is actually relevant to TOPIC

Do this after finishing the full read of the article and before starting Step 2 — a title or abstract alone can be misleading in either direction, so decide this from the whole article, not a skim.

The bar is substantive engagement with TOPIC (and TOPIC DESCRIPTION, if given), not mere adjacency. An article that mentions TOPIC in passing, cites it as background for a different mechanism, or covers a related-but-distinct pathway that never actually connects to what TOPIC names, is not relevant, even if it's well-written and pathway-shaped in isolation. This is the same "must connect to every element TOPIC names" discipline from Step 2 (see below), applied to the whole article instead of one candidate key event — a batch assembled by keyword search routinely pulls in a few articles that are adjacent but don't actually belong, and this is the point where they get caught rather than quietly producing a padded pathway.

- **Clearly off-topic** — the article isn't substantively about TOPIC at all. Exclude it: write one line to `output/run_log.md` as `excluded — not relevant to TOPIC (reason: <one line>)`, don't produce a pathway file for it, and move to the next article. The one-line reason is required, not optional — it's what the user is told live and what the end-of-run recap repeats, so a bare label isn't enough. Don't spend Steps 2-5 on an article you've already determined doesn't belong.
- **Genuinely on-topic** — proceed to Step 2 normally. If Step 2 then produces zero key events, that is not a normal result: log it as `processed — on-topic, but no key events extracted` and handle it like the borderline-with-zero case below (flagged prominently).
- **Borderline** (touches TOPIC's subject area but you're not certain it clears the bar) — don't exclude it on suspicion alone. Write down a one-line reason for the uncertainty (what part of TOPIC it touches and what's missing or unclear). Proceed to Step 2 and let the evidence requirement do the filtering: if nothing in the article actually supports a TOPIC-connected key event, Step 2 will legitimately produce zero key events for it. That's a real, informative outcome in its own right. Log it as `processed — borderline on-topic (reason: <one line>)`, or if Step 2 produced zero key events, as `processed — borderline on-topic, no TOPIC-relevant content found (reason: <one line>)`, rather than silently producing an empty file with no explanation.

"Borderline" here means only one thing: uncertainty about whether the article is on-topic for TOPIC / TOPIC DESCRIPTION. It says nothing about the article's quality, methods, or reliability.

Don't use this step to second-guess an article's scientific quality or methodology — that's out of scope here. This is strictly a topic-boundary check.

## Per-article callouts — tell the user live

Right after each article is finished (its file written in Step 5, or it was skipped in Step 1/1b), check whether it falls into one of the five cases below. If so, say so in chat immediately, in a sentence or two — don't hold it for the end of the run, and don't leave it only in `run_log.md`.

- **Failed to parse** — name the article, say the PDF was unreadable and skipped, and that it didn't contribute to the run.
- **Excluded as entirely off-topic** — name the article and give the one-line reason from Step 1b.
- **Borderline on-topic** — name the article, say plainly that "borderline" means the skill was unsure whether it's on-topic for the topic/description given (not a comment on quality), that it was processed anyway, and give the one-line reason.
- **Borderline and zero key events extracted** — a more serious case than plain borderline: the uncertain call also produced nothing usable. Flag it more prominently than the plain borderline message (e.g. open with "Needs attention:"), name the article, and give the reason.
- **On-topic but zero key events extracted** — the article was judged on-topic yet nothing usable came out of it. Same prominent flag as the borderline-with-zero case ("Needs attention:"), naming the article and saying that it was judged on-topic but yielded no key events.

Never call out, at this stage or any other: a normal processed article with no issues; a *partial* exclusion (leaving out a tangential section or side mechanism of an article that is on-topic overall — that is ordinary scoping, it isn't logged as an exclusion, and it isn't mentioned to the user); the source type (text/figure/both) or adverse-outcome flag of any individual key event or relationship; single-source flags on individual key events or relationships; quality results (counterfactual evidence or disprove attempts).

## Step 2: Extract the pathway from this article

Read paragraph by paragraph. Pull out every molecular initiating event, key event, adverse outcome, and the relationships connecting them, as actually described in THIS article's text and figures, restricted to TOPIC (and TOPIC DESCRIPTION, if given). Use only what this article states — don't fill gaps from background knowledge.

When TOPIC names more than one element (e.g. "X and Y"), a candidate key event or relationship must connect — directly, or through the chain — to every element named, not just one of them. A mechanism that's clearly related to the article's subject but never actually touches the other half of a multi-part topic is exactly the kind of thing to leave out, no matter how well-evidenced or pathway-shaped it looks in isolation. Check this explicitly before keeping a branch, not just at the end.

Work from the text outward: find the actual sentence or passage that supports a candidate key event or relationship before deciding it belongs. Don't settle on a plausible pathway shape first and then go looking for sentences to fit it — that ordering is exactly how prior familiarity with a mechanism ends up substituting for what the article actually says. If you can't point to a specific supporting passage, leave it out.

Match the granularity shown in the reference example below — that's the actual standard for how finely to chunk biology into separate key events, more so than the abstract schema.

Encode as:

```json
{
  "aop_id": "<initiating_event>@<adverse_outcome>_<article_slug>",
  "extraction_mode": "simplified",
  "key_events": [
    { "id": "KE:0", "biological_entity_id": "<term_id>", "mie": true, "adverse_outcome": false, "source_type": "text", "evidence": "<verbatim quote from the article supporting this key event>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["<article_slug>"] }
  ],
  "key_event_relationships": [
    { "id": "KER:0", "source": "KE:0", "target": "KE:1", "relationship": ["<tag for the source event>", "<tag for the target event>"], "evidence": "<verbatim quote from the article supporting this relationship>", "reference_ids": [], "quality": { "counterfactual_evidence": "unknown", "disprove_attempts": "unknown", "quotes": [] }, "source_articles": ["<article_slug>"] }
  ]
}
```

**Naming (`aop_id` and the file name).** `aop_id` is `<initiating event>@<adverse outcome>_<article slug>`, all lowercase with underscores, for example `cyp2e1@hepatocyte_necrosis_jones_2021`. This matches the pathway names already used elsewhere (`drug@limb_formation`), with the article slug added so the source is visible. For the first part, use the final `biological_entity_id` of the key event marked `mie: true`; for the second part, use the one marked `adverse_outcome: true`. If there are several of either, use the first one in the file's key-event order. If no key event is marked `mie: true`, use `unk` for the first part; if none is marked `adverse_outcome: true` (including an article that yielded zero key events), use `unk` for the second part. Work this out when the file is written (Step 5), after term matching in Step 4. The file is named `<aop_id>.json`, because the upload script sets each pathway's id from its file name, and that is what shows up in the visualizer's pathway list. The article slug alone stays the identifier everywhere else (`source_articles`, the tallies, the run log). If Step 8 relabels a term later, don't rename the file or change `aop_id`, so the file name keeps matching what was uploaded.

`extraction_mode` is `"simplified"` or `"full"`, as chosen at the start of the run. In Step 2, write each `biological_entity_id` and relationship term as a provisional plain-language name; Step 4 replaces them with the final ids before the file is written in Step 5.

`source_type` is `"text"`, `"figure"`, or `"both"` — whichever the key event was actually drawn from. Keep this distinction visible: figure-derived extractions are expected to be less reliable than text-derived ones.

`reference_ids` starts as `[]` here in Step 2 — it gets filled in during Step 3C, once the article's reference list has ref_ids to point to. Don't try to resolve citations while still in Step 2; just keep the field present so Step 3C has something to fill in. (It lists the citations attached to the `evidence` quote on the same node. The article's full list of cited works, at the end of the file, is a different thing and is called `references`.)

`evidence` is a short, exact quote copied from the article's own text — not a paraphrase, not a summary — that directly supports this specific key event or relationship. If something is genuinely drawn from a figure with no supporting text, quote the figure's caption or axis/node labels instead, and set `source_type` accordingly. If you can't quote support for a candidate, that's a sign it doesn't belong in this file.

If the article supports the same key event or relationship in more than one place (separate sentences, possibly with different citations), keep the clearest quote as `evidence` and add each further quote to an `additional_evidence` array on the same node: `[{ "quote": "<verbatim quote>", "reference_ids": [] }]`. Each quote keeps its own citations, so a source cited for only one of the sentences isn't lost. Leave `additional_evidence` off when there's only one quote.

**The `relationship` field always has exactly two tags, in a fixed order, separated by a comma:** the first says what happens to the `source` event (for example activated, inhibited, metabolized, bound), and the second says what that does to the `target` event. For example, `["oxidizes_to", "formed_from"]` on an arrow from CYP2E1 to NAPQI, or `["metabolized_by", "binds_to"]` on an arrow from a parent drug to its enzyme. The tags can be any relationship terms (`metabolized_by`, `binds_to`, `increases`, `decreases`, and so on), and the two are allowed to be different words. Rules:
- Follow the article's own wording as closely as possible for each side. If the article describes both sides, use its words for each (for example `["oxidizes_to", "formed_from"]`). Step 4 then reuses an existing verb from the ontology or from earlier in the run when it means the same thing.
- If the relationship reads the same from both sides (for example `binds_to`), repeat the word: `["binds_to", "binds_to"]`.
- If the article states only one side, repeat that word: `["activates", "activates"]`. Don't make up a counterpart verb the article doesn't use.
- The two tags can differ in direction. `["activates", "inhibits"]` is a valid relationship: the source is activated, and that inhibits the target. It is a different relationship from `["inhibits", "activates"]`.
- An opposite claim about the same step is a different pathway, not the same one. If one article says A activates B (`["activates", "activates"]`) and another says A inhibits B (`["inhibits", "inhibits"]`), that leads to a different outcome, so they stay separate relationships and are listed in `relationship_disagreement_flags` (Step 7).
- When a later article describes the same relationship as an earlier one, reuse the verbs already minted for it, in the same positions (Step 4). For example, if article 1 recorded CYP2E1 to NAPQI as `["oxidizes_to", "formed_from"]` and article 2 describes the same thing, article 2 also uses `["oxidizes_to", "formed_from"]`, even if its wording is "forms". Use different verbs only when the article describes a different biological relationship. Step 7 counts two articles as the same relationship only when both verbs match exactly.

`id` values (KE:0, KER:0, etc.) only need to be unique within this one article's file. Every KER's `source`/`target` must point to a real KE id in the same file. Every KE and KER must have a unique id within the file, no repeats.

`adverse_outcome: true` marks a terminal/endpoint node of a branch — nothing downstream of it in this article's pathway — not "something harmful." A benign or protective endpoint (e.g. successful clearance of a drug) gets `adverse_outcome: true` just as much as a toxic endpoint does, if it's the last thing this branch describes. Don't reserve this flag for harm only, and don't set it on an intermediate step just because it sounds significant.

`source`/`target` direction is always causal/temporal order: `source` is the earlier event, `target` is what it leads to, regardless of how the relationship phrase is worded. This holds even when the relationship label reads passively in one direction and actively in the next (an upstream node can be the `source` of a "metabolized_by" edge and the `target` of the next "oxidizes_to" edge — still source=earlier, target=later in both, don't flip the edge to make the verb read more naturally). If unsure which end is earlier, use what actually happens first biologically, not which phrasing sounds more natural.

Encode whatever topology the article actually describes — chain, branch, convergence — don't force a single line and don't invent branches that aren't there.

**Quality assessments (both modes).** Every key event and relationship gets a `quality` object. It records whether the review reports two kinds of evidence that make a step more trustworthy. This is record-keeping only for now. Many steps will come back `"unknown"`, and that is expected and fine. The two criteria are always two separate fields, never one combined score.
- `counterfactual_evidence`: does the review report a specificity or competition-type test for this step? The classic case is a ligand-binding claim backed by a competition experiment (for example, a radiolabeled ligand displaced by a known competitive ligand until binding is no longer appreciable), or an equivalent control showing the interaction is specific rather than incidental. Academic studies rarely do this, so a `true` here is meaningful.
- `disprove_attempts`: does the review report an attempt to break this step rather than only observe it? Look for necessity and sufficiency testing. Necessity: the upstream event was blocked, knocked out, or knocked down to see whether the downstream event still happens. Sufficiency: the upstream event was induced on its own to see whether the downstream event follows without the usual trigger. Rescue experiments also count. Textual cues: knockout, knockdown, antagonist, inhibitor, blocked, rescue, abolished, attenuated, sufficient, necessary. Purely correlational language ("X increased alongside Y") is not a disproof attempt, however confidently the review states the relationship.
- Each criterion takes one of three values. `true`: the review reports this kind of test for this step. `false`: the review explicitly says this kind of test was not done or has not been done. `"unknown"`: the review says nothing either way. `"unknown"` is the default. Reviews often omit methodological detail even when the underlying study did it, so `"unknown"` means "not visible from this review," which is different from `false`. Never collapse the two.
- Use only these three values. If a step is clearly not the kind of claim a competition test could apply to (for example, a downstream phenotype), use `"unknown"` for `counterfactual_evidence`. Don't add a "not applicable" value.
- `quotes` is a list, empty when both criteria are `"unknown"`. Every `true` or `false` needs an entry: `{ "assessment": "counterfactual_evidence" | "disprove_attempts", "quote": "<verbatim quote>", "reference_ids": [] }`. The quote is a short verbatim excerpt from the review, with the same exact-quote rule as `evidence`. `reference_ids` lists the cited papers the review attaches to that quote. If there's no quote you can point to, the answer is `"unknown"`.
- Judge from the review only. Never open, fetch, or read the cited articles, and never mark something `true` because you know a well-known binding or knockout study exists for that mechanism.
- Judge each key event and each relationship on its own. A review may describe tests for one relationship and not another. If a test covers only one end of a relationship, mark it `true` and let the quote show which part.
- Never add the two criteria into a point total anywhere. A "1 out of 2" would hide which one was met.
- Store this in each article's own pathway file. The same step can be well tested in one review and unaddressed in another.
- Don't mention quality results to the user, during parsing or in the end-of-run summary. It stays in the JSON only.

Example:

```json
"quality": {
  "counterfactual_evidence": true,
  "disprove_attempts": "unknown",
  "quotes": [
    { "assessment": "counterfactual_evidence", "quote": "Blocking CYP2E1 prevented NAPQI formation (4).", "reference_ids": ["ref_3"] }
  ]
}
```

**Full mode only — capture the four additional annotation types as you read.** If EXTRACTION MODE is Full, do this on this same paragraph-by-paragraph read; don't make a second pass over the article for it. For any KE or KER where the article's own text states one of the four kinds of qualifier described in "Extraction mode: Simplified vs. Full" above, add the matching field(s), grounded in a verbatim quote exactly like every other evidence-bearing field in this skill. Add the `layers` array to any KE/KER that received a species/circumstance, confounder, or developmental-window annotation. Don't go hunting for these if the article doesn't clearly state one — absence of a qualifier is the default, not something to infer from silence. The citations for these quotes are linked in Step 3C, and any new term names go through Step 4, like everything else.

**Hard constraint:** see SKILL.md's opening section — it applies here in full, including the AOP-Wiki restriction.

## Step 3: Extract bibliographic information from this article

Two distinct things, don't conflate them:

**A. Metadata about this source article itself** (the article you're reading, not something it cites). Add a `source_article` object: `article_slug`, title, full author list, author institutions/affiliations (as printed near the title or in a footnote), journal, publication date (year, full date if given), DOI, and the PDF filename read.

**B. References actually cited inside the key events and relationships you extracted** — not the article's full bibliography. A review article can cite hundreds of works; only the ones backing a specific evidence quote you wrote down belong here. As you write each KE/KER's `evidence` field, note whether that sentence carries an inline citation (a bracketed number resolved against the article's numbered reference list, or an author-year mention like "(Chen et al., 2008)"). After finishing Step 2, collect the distinct works actually cited this way — typically a handful per article, not the whole bibliography — and for each capture just enough to locate it later: a `ref_id` (`"ref_1"`, `"ref_2"`, ... assigned in order of first appearance — this is what Step 3C links to, and it's only unique within this one article's file, not across the batch), first author plus "et al." if there are more, publication year, title, and `journal` if the entry prints one (otherwise `null`). Also record the DOI as `doi` if the reference-list entry prints one, otherwise `null` — don't look one up, and don't assume every PDF's reference section will include one. Skip volume and page range. The title (and DOI when present) is what lets Step 7 tell two different papers by the same first author and year apart, so copy the title faithfully rather than abbreviating it. Keep the original in-text citation form as `citation_text` (e.g. `"Chen et al. (2008)"` or the bracketed number plus what it resolved to) as a fallback. Don't guess at a date or spell out an institution; leave a field `null` rather than invent it.

Write `references` as the **last** key in the file, after `key_event_relationships` — so a human opening the file sees the actual pathway extraction first and doesn't have to scroll past citations to get to it.

If any field in A or B is unclear or not plainly stated, leave it `null`. A wrong value here is worse than a missing one — this data needs to be traceable.

Add a `source_articles: ["<article_slug>"]` field to every key event and key event relationship created in Step 2 — this is what makes counting possible later, don't skip it.

## Step 3C: Link each key event and relationship to its specific citations

This is what makes the reference list traceable back to individual claims instead of sitting as an undifferentiated block at the end of the file — do this right after Step 3B, once every reference has a `ref_id`.

Go back through every KE and KER from Step 2. For each quote on it, look at the sentence it came from: if that sentence carried an inline citation (the same ones you resolved in Step 3B), set the `reference_ids` next to that quote to the `ref_id`(s) it resolved to, e.g. `"reference_ids": ["ref_2"]`, or `["ref_2", "ref_5"]` if the sentence cited more than one. This applies to every quote, with no exceptions: the main `evidence` quote, each entry in `additional_evidence`, each entry in `quality.quotes`, and (Full mode) each entry in `special_circumstances` and `confounders` and the `developmental_window`, which each carry their own `reference_ids`. If a quote synthesizes several sentences and only part of it carries a citation, still just record whichever `ref_id`(s) actually appear attached to that quote — don't extend it to nearby citations that support a different sentence.

If a quote's sentence carries no inline citation at all (it's the reviewing authors' own uncited synthesis, or a figure with no citation in its caption), leave its `reference_ids` as `[]` — don't guess a source for it, and don't leave the field missing entirely; an empty array and "not yet checked" need to stay distinguishable, so always set it one way or the other before Step 5.

## Step 4: Align terminology against the ontology and everything minted so far

Applies to every `biological_entity_id` AND every `relationship` type written in Step 2 — both go through the same process.

**First check:** does this concept already exist, under this name or different wording, in the ontology file, or in terms already minted earlier in this same run (article 2 onward)? If yes, reuse that existing ID exactly.

If not confident it's the same concept, **default to treating it as new rather than merging**, but flag it: add `"possible_duplicate_of": "<existing_id>"` and a one-line `"reason"` explaining the resemblance, so it surfaces for manual review instead of silently becoming an unreviewed merge or an unreviewed new term. Only skip this flag when genuinely confident it's a clean reuse or a clean new term.

If no match exists at all, before writing a free-text term, check for an already-accepted name:

- Gene or protein → the official HGNC gene symbol
- Chemical → the standard/common name as used in PubChem
- A disease or adverse-outcome-type node → check if this maps to a standard clinical term (SNOMED CT, MedDRA, MeSH-style naming); use it if confident of the mapping
- A mechanistic key event step (not a named disease) with no HGNC/PubChem/SNOMED-style match → write a clear, plain-language `id` (lowercase, underscores, matching the ontology's existing style) and a one-sentence `definition`, formatted exactly like existing entries. Do **not** check AOP-Wiki or any other outside source here, even just for wording. New terms are minted from the article's own wording and nothing else.
- Otherwise, write a clear, plain-language `id` (lowercase, underscores, matching the ontology's existing style) and a one-sentence `definition`, formatted exactly like existing entries.

Relationship types follow the same reuse-or-mint discipline, not a separate one, and this applies to both tags of every relationship (the source-side tag and the target-side tag, Step 2). Check the ontology's relationship-type category first (activates, inhibits, binds_to, etc.) and reuse an existing verb whenever it captures the actual meaning, even if the article's phrasing is more elaborate. Only mint a new relationship term when an existing one would genuinely lose meaning, not just because the article's wording is more specific or colorful. A new relationship term gets a clear `id`, a one-sentence `definition`, and a `direction` field describing which end is earlier/causal, matching the format of existing relationship-type entries. Log it in `new_terms.json` under the relationship-type category, not mixed in with entity terms.

Record every genuinely new term (don't write into the ontology file itself): you'll add it to `output/new_terms.json` in Step 5, so the file builds up article by article and survives an interrupted run. Each entry is `{ "id": "...", "definition": "...", "category": "entity" | "relationship_type", "direction": "..." (relationship types only), "prompted_by": ["<article_slug>", ...], "possible_duplicate_of": "...", "reason": "..." }`, with the last two present only when flagged. If a later article mints or reuses a term already in the file, add its slug to `prompted_by` rather than adding a second entry.

## Step 5: Validate and write this article's file now

Before moving to the next article, check: every KE and KER id is unique within this file; every KER's source/target points to a real KE id; every KE has `source_articles`, `source_type`, and `evidence` set; every KER has `source_articles` and `evidence` set, and its `relationship` has exactly two entries; every `additional_evidence` quote is also an exact excerpt; every `evidence` value is an actual excerpt from the article's own text or figure (not a paraphrase or something generated to sound plausible); `source_article` (Step 3A) and the article's `references` list (Step 3B) are both present; every KE and KER has a `quality` object whose two values are each `true`, `false`, or `"unknown"`, every `true` or `false` has a matching verbatim quote in `quality.quotes`, and `quotes` is empty when both values are `"unknown"`; every quote (the `evidence` quote, each `additional_evidence` entry, each `quality.quotes` entry, and in Full mode each `special_circumstances` / `confounders` entry and the `developmental_window`) has its `reference_ids` set (Step 3C) — `[]` is fine, missing is not, and every `ref_id` named actually exists in this file's `references` list. In Full mode, also check that every `species_annotation`, `molecular_basis`, `gate_type`, `active_in`, `absent_in`, `note`, `special_circumstances`, `confounders`, `developmental_window`, and `initiating_event_class` value is backed by a verbatim quote (the KE/KER's own `evidence` or `additional_evidence` quote, or for the entries that carry their own, that entry's quote) — not a paraphrase, and not something added because it seemed biologically plausible. Also check that `has_special_circumstances` is true exactly when `special_circumstances` is non-empty, and that every `layers` array lists exactly the layers whose annotations are actually present on that node (and that nodes with none of those annotations have no `layers`).

Write `output/<aop_id>.json` now (see "Naming" in Step 2), containing `aop_id`, `extraction_mode`, `source_article`, `key_events`, `key_event_relationships`, and `references`. Do this immediately — don't wait until all articles are processed, so an interrupted run still leaves completed work on disk. In the same step, add any terms this article minted to `output/new_terms.json` (create it with this article's terms if it's the first, otherwise add to it; see Step 4 for the entry format). Append one line to `output/run_log.md`: article slug, one of processed successfully / processed — borderline on-topic (reason) / processed — borderline on-topic, no TOPIC-relevant content found (reason) / processed — on-topic, but no key events extracted / excluded — not relevant to TOPIC (reason) / failed to open / no readable text found, plus pages read. Then apply "Per-article callouts" above.

## Step 6: Repeat Steps 1-5 for the next article

Continue through the full ARTICLES list. Each new article gets checked against the original ontology file plus every term minted from earlier articles in this run, so the same concept described differently across articles converges on one ID instead of being reinvented each time.

## Step 7: Merge across articles and produce the remaining output files

Once every article has its own file (Step 5), read them all back in and produce:

- `output/new_terms.json` is already built, article by article, in Step 5. In Step 7 only check it: every term used in any per-article file is either in the ontology file or in `new_terms.json`. Don't rewrite it here. If Step 7's merge is run again later (Step 8 does this after relabeling), regenerate **only** `merged_tally.json`, because by then `new_terms.json` also holds the review decisions and `merged_into` marks from Step 8.
- `output/merged_tally.json` — built by joining the per-article files on each KE's `biological_entity_id` (not its local `KE:N` id, which only exists within one article) and each KER's source entity, target entity, and relationship terms. A `relationship` field is two tags, the source-side tag first and the target-side tag second (Step 2). Articles describe the **same** relationship only when they connect the same two key events and both tags match exactly, position by position: first tag with first tag, second tag with second tag. The tags are never treated as an unordered set, so `["activates", "inhibits"]` and `["inhibits", "activates"]` are different relationships. Because Step 4 makes later articles reuse the verbs already minted for the same concept, articles describing the same relationship should already carry the same pair. When the same two key events end up with more than one distinct pair, keep each pair as its own entry and list them in a `relationship_disagreement_flags` array (the two key events, each pair, and which articles use it). The difference may be a real disagreement (for example `["activates", "activates"]` versus `["inhibits", "inhibits"]`) or a missed reuse in Step 4 (for example `["oxidizes_to", "formed_from"]` versus `["oxidizes_to", "forms"]`). Don't try to judge which; a human decides. For each, record:
  - `article_count` and `supporting_articles`: how many articles support it, and which ones — the original tally.
  - `distinct_sources_cited` and `cited_sources`: collect every `ref_id` on every quote of every contributing article's version of this node (the `evidence` quote, each `additional_evidence` entry, each `quality.quotes` entry, and in Full mode each `special_circumstances` / `confounders` entry and the `developmental_window`), resolve them back to that article's own reference-list entries (author/year/title/journal/doi), then deduplicate across **all** contributing articles — the same primary source is often cited by more than one review in the batch, and that shouldn't inflate the count. Decide whether two entries are the same paper in this order, never on first author + year alone when titles are available (two different "Jones et al. 2012" papers must stay separate): (1) if both entries have a `doi`, same paper iff the DOIs match (case-insensitive); (2) otherwise, if both have a title and the normalized titles match (lowercased, punctuation and extra whitespace stripped): if the years also match, same paper; if the first author matches but the years differ (typically a preprint versus its published version), treat it as a **likely match** — count it once — and list it in `ambiguous_source_matches` for manual review, noting whether the journals match (if both entries have one) or differ; if the first author differs too, treat them as different papers; (3) only if a title is missing on either or both sides, fall back to first author + year, and list that pairing in an `ambiguous_source_matches` array in `merged_tally.json` (both entries, which articles they came from) so a human can confirm — don't silently merge or split it. Before writing `merged_tally.json`, re-check that every source merged via this fallback appears in `ambiguous_source_matches`; a fallback merge that isn't listed there is a mistake. Where titles differ slightly because of typos or abbreviation but author and year match, treat as different and list it in `ambiguous_source_matches` too; undercounting a shared source is the safer error than silently merging two different papers. `cited_sources` is the deduplicated list (`{ "first_author": ..., "year": ..., "title": ..., "journal": ..., "doi": ... }`); `distinct_sources_cited` is its length. This is a different number from `article_count` on purpose — a KE backed by 1 article citing 4 distinct primary sources is better evidenced than one backed by 3 articles all citing the same single source, and this makes that visible.
  - `quality`: for each criterion separately, which contributing articles gave `true`, `false`, and `"unknown"` for their own version of this node: `{ "counterfactual_evidence": { "true": [...], "false": [...], "unknown": [...] }, "disprove_attempts": { "true": [...], "false": [...], "unknown": [...] } }`. The length of each list is the count. This is not a combined value: each article's own assessment and its supporting quotes stay in its per-article file, and the two criteria are never added together.
  - In Full mode only: a `layers` field (union of every contributing article's `layers` values for this KE/KER) and a `layer_details` array, one entry per contributing article that supplied any Full-mode annotation: `{ "article_slug": "...", "species_annotation": ..., "molecular_basis": ..., "gate_type": ..., "active_in": ..., "absent_in": ..., "note": ..., "special_circumstances": ..., "confounders": ..., "developmental_window": ..., "initiating_event_class": ... }`, including only the sub-fields that article actually populated. Don't reconcile disagreements between articles here (e.g. one says a branch is species-conditional on rat/human, another gives different species) — list both entries under `layer_details` and let a human notice the discrepancy, same as `single_source_flags` below.
- Within `merged_tally.json`, a `single_source_flags` array: any key event or relationship supported by only one article where the other articles clearly do discuss that same region of the pathway (not just articles that never touched that topic at all). Don't judge whether these are real biological differences or extraction misses — just surface them.
- A separate `single_citation_flags` array: any KE/KER where `article_count` is more than 1 but `distinct_sources_cited` is only 1 — several articles all repeating the same single primary source is a materially weaker claim than the article count alone suggests, and it's a distinct condition from `single_source_flags` (which is about article coverage, not citation depth), so keep the two arrays separate rather than merging them.

`articles_included` lists the slugs of articles that have a pathway file (excluded and unreadable articles are left out; they are in `run_log.md`). Overall shape of `merged_tally.json` (merged entries have no ids of their own; a key event is identified by its `biological_entity_id`, a relationship by its `source` and `target` entities plus terms). A merged `mie` or `adverse_outcome` is `true` if any contributing article marks it true; each article's own values stay visible in `per_article`, so a disagreement can be seen. The quotes themselves stay in the per-article files and are not copied here.

```json
{
  "topic": "<TOPIC>",
  "extraction_mode": "full",
  "articles_included": ["smith_2019", "jones_2021"],
  "key_events": [
    {
      "biological_entity_id": "napqi",
      "mie": false,
      "adverse_outcome": false,
      "article_count": 2,
      "supporting_articles": ["smith_2019", "jones_2021"],
      "distinct_sources_cited": 1,
      "cited_sources": [
        { "first_author": "Chen", "year": 2008, "title": "<title>", "journal": "<journal>", "doi": null }
      ],
      "per_article": [
        { "article_slug": "smith_2019", "mie": false, "adverse_outcome": false, "source_type": "text" },
        { "article_slug": "jones_2021", "mie": false, "adverse_outcome": false, "source_type": "both" }
      ],
      "quality": {
        "counterfactual_evidence": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] },
        "disprove_attempts": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] }
      },
      "layers": [],
      "layer_details": []
    }
  ],
  "key_event_relationships": [
    {
      "source": "cyp2e1",
      "target": "napqi",
      "relationship": ["oxidizes_to", "formed_from"],
      "article_count": 2,
      "supporting_articles": ["smith_2019", "jones_2021"],
      "distinct_sources_cited": 1,
      "cited_sources": [
        { "first_author": "Chen", "year": 2008, "title": "<title>", "journal": "<journal>", "doi": null }
      ],
      "quality": {
        "counterfactual_evidence": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] },
        "disprove_attempts": { "true": ["smith_2019"], "false": [], "unknown": ["jones_2021"] }
      },
      "layers": [],
      "layer_details": []
    }
  ],
  "single_source_flags": [
    { "kind": "key_event", "item": "gsh_depletion", "supported_by": "smith_2019" }
  ],
  "single_citation_flags": [
    { "kind": "relationship", "item": { "source": "cyp2e1", "target": "napqi", "relationship": ["oxidizes_to", "formed_from"] }, "article_count": 2, "only_source": { "first_author": "Chen", "year": 2008, "title": "<title>" } }
  ],
  "relationship_disagreement_flags": [
    {
      "source": "napqi",
      "target": "gsh_depletion",
      "groups": [
        { "relationship": ["depletes", "depletes"], "articles": ["smith_2019"] },
        { "relationship": ["spares", "spares"], "articles": ["jones_2021"] }
      ]
    }
  ],
  "ambiguous_source_matches": [
    {
      "source_a": { "first_author": "Jones", "year": 2012, "title": null, "from_article": "smith_2019" },
      "source_b": { "first_author": "Jones", "year": 2012, "title": "<title>", "from_article": "jones_2021" },
      "reason": "title missing on one side; matched on first author and year"
    }
  ]
}
```

## Step 8: End-of-run summary and interactive checkpoints

Runs after Step 7, once every article's file and `merged_tally.json` are written. 8a only adds what's said to the user. The two optional review checkpoints (8b and 8c) can change term labels inside the per-article files and then regenerate `merged_tally.json`, and nothing else (see "What relabeling may and may not do"). To keep that safe: before the first relabel of the session, copy every per-article pathway file into `output/pre_relabel_backup/`; make each relabel a targeted replacement of just the term text, never by re-writing a whole JSON file from memory, which risks altering quotes; and regenerate `merged_tally.json` only after the relabeling is finished. If the session is interrupted partway, the per-article files are the source of truth, so just regenerate the tally from them. The ontology file itself is never modified at any point in Step 8; every new or adopted term lives in `output/new_terms.json`, for a human to add to the ontology later.

### 8a. Summary (always print)

- Counts: total key events and total relationships in the merged tally, and how many relationships have `article_count` of 2 or more. Also the batch counts (articles processed / excluded as off-topic / failed to read) and new terms minted. In Full mode, also how many key events/relationships carry each kind of Full-mode annotation.
- A named recap of every article that triggered a callout during parsing (failed / excluded off-topic / borderline / borderline with zero key events / on-topic with zero key events): article name plus its one-line reason, e.g. "1 article flagged: smith_2019 — borderline on-topic (reason: ...)". If none, say none.
- The possible-duplicate term pairs, listed **by name only** (e.g. "mitochondrial membrane rupture" vs. "mitochondrial swelling") — no reasons here; the reason is first shown in 8b. This is how the user learns the pairs exist even if they skip the review.
- The relationship disagreements, listed by the two key events only (e.g. "napqi to gsh_depletion"), so the user knows they exist even if they skip the review in 8c. If none, leave this line out.
- Do **not** include single-source or single-citation counts or flags anywhere in this summary — those stay in the JSON only.

### 8b. Possible-duplicate review (interactive)

Ask: "Would you like to review the possible duplicate terms now?"

- **No** — move on; the pairs stay flagged in `new_terms.json` for later.
- **Yes** — go through the pairs one at a time. For each, show both terms and the one-line reason they were flagged, and let the user choose **merged** or **kept separate**. If merged, ask which of the two is the canonical term. If one of the two is already in the ontology file, it must be the canonical one — the ontology file is never relabeled.

Record every decision, merges and keep-separates alike, in a `resolved_duplicates` array in `output/new_terms.json` (one entry per pair): `term_a`, `term_b`, `original_reason` (the one-line flag reason), `decision` (`"merged"` or `"kept_separate"`), `canonical_term` (merges only), `decided_by`, `decided_at`.

- `decided_by`: ask the user once, at the first decision, for the name to record, and reuse it for the rest of the session. Don't infer it from the environment or guess.
- `decided_at`: the date of the decision, ISO 8601 (`YYYY-MM-DD`), taken from the current date the session reports, not estimated. The lockdown workspace blocks shell commands, so there's no system clock to read a time from; record the date only.
- A `kept_separate` entry is logged exactly like a merge. It documents that a person reviewed the pair and chose not to merge it.
- Before applying a merge, check every per-article file for a relationship that connects the two terms, either directly (one as source, the other as target) or through a chain of other key events. If there is one, tell the user which article and which relationship or chain it is, explain that merging would turn it into a loop (a term leading to itself), and ask whether to merge anyway or keep the pair separate. Don't remove the relationship on your own. Relationships to *other* key events need no check: they point at key events by internal id, so they follow the relabeled term automatically.
- On a merge, relabel the non-canonical term to the canonical one in every per-article pathway file in `output/` where it appears (`biological_entity_id` for entity terms, the `relationship` array for relationship types, in whichever position the term appears; the array always keeps exactly two entries, so if it then lists the same term twice, that's fine and both stay). Do not touch `evidence`, `additional_evidence`, `reference_ids`, the `references` list, or any other field. The supporting quotes stay exactly as extracted and attributed to their own article. Mark the non-canonical entry in `new_terms.json` with `"status": "merged_into"` and `"merged_into": "<canonical>"`; don't delete it. Point any other entry's `possible_duplicate_of` that named the merged-away term at the canonical term instead. The `resolved_duplicates` and `resolved_relationship_disagreements` records are history, so they keep the names exactly as they were when the decision was made.
- When anything was merged, regenerate `merged_tally.json` only, by re-running the merge in Step 7 (`new_terms.json` is left alone), so the tally reflects the standardized labels.

### 8c. Relationship-disagreement review (interactive)

After the duplicate review (whether or not the user went through it), if `merged_tally.json` has any `relationship_disagreement_flags`, ask: "Would you like to review relationship disagreements?" If there are none, skip this step without asking.

- **No**: move on. The flags stay in `merged_tally.json` for later.
- **Yes**: go through the flags one at a time. For each, show the two key events, every pair of tags used between them, and which articles use each pair. Ask whether the pairs mean the **same** thing (a wording difference, for example `["oxidizes_to", "formed_from"]` versus `["oxidizes_to", "forms"]`) or something **different** (for example `["activates", "activates"]` versus `["inhibits", "inhibits"]`). Don't suggest an answer; the decision is the user's. If there are more than two pairs, ask which of them mean the same thing; any pairs left over are treated as different.
- If the user says **same**, ask which pair to keep. Then, in each article that used one of the other pairs, change the `relationship` array on that one relationship (the one between those two key events) to the kept pair. Change nothing else: not other relationships that use the same verbs, and not `evidence`, `additional_evidence`, `reference_ids`, `quality`, or the `references` list. Use the same backup and targeted-replacement rules as 8b.
- If the user says **different**, change nothing in the article files.

Record every decision, same and different alike, in a `resolved_relationship_disagreements` array in `output/new_terms.json`: `source` and `target` (the two key events), `pairs` (each pair as it was, with the articles that used it), `decision` (`"same_meaning"` or `"different"`), `kept_relationship` (same-meaning decisions only), `decided_by`, `decided_at` (same rules as 8b). A `"different"` entry matters as much as a same-meaning one: it records that a person looked at the disagreement and confirmed it.

When anything was changed, regenerate `merged_tally.json` only, as in 8b, so the combined relationship counts its articles together and the flag goes away.

After the relationship-disagreement review (whether or not the user went through it), the run is done. There is no check against outside ontologies: new terms stay exactly as minted from the articles, in `new_terms.json`, for a human to review and add to the PathWise ontology.

### What relabeling may and may not do

Relabeling changes only the term label a key event or relationship is filed under (or, in 8c, the tag pair on one relationship). It never adds, removes, or reconnects key events or relationships, and never touches `evidence`, `additional_evidence`, `reference_ids`, or the `references` list. It can still have a consequence: if two nodes in one article end up with the same label after a merge or adoption, both nodes stay in that article's file, and Step 7 counts the article once for that term (`article_count` counts distinct articles). Say so if it happens, so the user can look at that article's file.

## What each output file is, in plain language

A run leaves several files in `output/`. Their names don't say much on their own — make sure the user handing this off knows what's in each one and what they'd actually use it for.

**`<aop_id>.json`** (one per article, e.g. `cyp2e1@hepatocyte_necrosis_smith_2019.json`)
The single-article extraction: this article's key events, its key event relationships, its own bibliographic details, and a short list of just the sources actually cited inside that evidence (not the article's full bibliography — see Step 3B), each one assigned a `ref_id`. Every key event and relationship carries `reference_ids` naming the specific `ref_id`(s) that back each of its quotes (Step 3C) — so a claim can be traced to its exact citation, not just "somewhere in this article's bibliography." That reference list sits at the end of the file, after the pathway content, so opening the file shows the actual extraction first. Written the moment that article finishes, so if the run stops partway through, whichever of these already exist are complete and safe to use — nothing partial. Open one of these to sanity-check that a specific article was read correctly, independent of anything else in the batch.

**`run_log.md`**
A one-line-per-article log: which articles were processed, which were processed as borderline on-topic (with the reason), which were excluded as off-topic (Step 1b, with the reason), which yielded no TOPIC-relevant content, which failed to open or had no readable text, how many pages were read. First stop if something seems off — e.g. if an article expected to contribute is missing from the tally, this file says whether it was excluded, came up empty, or failed outright, rather than just contributing nothing with no explanation.

**`new_terms.json`**
Every term (biological entity or relationship type) that didn't already exist in the ontology file and had to be minted during this run, plus which article(s) prompted it. Review this before adding anything permanently to the ontology — these are new, unreviewed additions. Anything carrying `possible_duplicate_of` is a term the run wasn't confident was new — a prompt for a human to decide whether it should actually merge into the existing term it resembles. If the user went through the end-of-run reviews (Step 8), this file also holds the record of those decisions: `resolved_duplicates` (each pair, the original reason, merged or kept separate, which term was kept, who decided, when), `resolved_relationship_disagreements` (each disagreement, same meaning or different, which tag pair was kept, who decided, when). Merged-away terms stay in the file, marked `merged_into`, so the full history is recoverable.

**`merged_tally.json`**
The actual deliverable. Every key event and relationship, merged across all articles that mention it, with two separate counts: `article_count` (how many articles support it) and `distinct_sources_cited` (how many distinct primary references those articles cite as evidence, deduplicated across the whole batch). A key event backed by 3 of 4 articles is a stronger claim than one backed by 1 — and one backed by 3 articles that each cite a different primary source is stronger still than one backed by 3 articles all citing the same source. This file is what makes both of those visible, which no single article's file can show on its own. In Full mode, entries also carry `layers` and `layer_details` wherever an article stated a species/circumstance qualifier, a confounder, or a developmental window.

**`single_source_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out key events or relationships that only one article supports, in a region of the pathway the other articles clearly do discuss. A deliberate "look here," not a verdict — the run doesn't judge whether that's a real point of biological disagreement between articles or a place where extraction went wrong on one side, a human makes that call.

**`ambiguous_source_matches`** (an array inside `merged_tally.json`, not its own file)
Calls out cited papers the skill had to match on first author and year alone (because a title was missing), or that look like the same paper with different years. A human confirms whether they really are the same paper, since that affects `distinct_sources_cited`.

**`relationship_disagreement_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out two articles that connect the same two key events but don't use exactly the same pair of verbs (for example "activates" versus "inhibits", or "formed_from" versus "forms"). They are kept as separate relationships, not counted together, and surfaced so a human can tell a real disagreement from a wording difference.

**`single_citation_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out key events or relationships backed by more than one article but only one distinct primary source between them — several reviews citing the same underlying study isn't the same as independent corroboration, and this is where that distinction becomes visible instead of getting flattened into a reassuring-looking article count.

**Relabeled files (only if the user merged terms or combined relationships in Step 8)**
Merging a duplicate or combining a relationship disagreement changes the label inside the per-article files and regenerates `merged_tally.json`. Quotes and references are never changed, and `new_terms.json` keeps the original names and tags, reasons, who decided, and when. A copy of the per-article files from before the first relabel is kept in `output/pre_relabel_backup/`.

## Reference pathway example

Anchors format and granularity only (Step 2). No matching source text exists for this — it's not a "paragraph in, JSON out" example. It predates the `evidence` field (won't show a filled-in quote) and doesn't show `reference_ids`, since it's plain-chain and Simplified-mode-shaped. This one is a plain linear chain — swap in a branching example if a run needs to model different topology.

```json
{
  "aop_id": "drug@limb_formation_rodents_fish_1",
  "key_events": [
    { "id": "KE:0", "biological_entity_id": "cyp3a", "mie": true, "adverse_outcome": false },
    { "id": "KE:1", "biological_entity_id": "parent_drug", "mie": false, "adverse_outcome": false },
    { "id": "KE:2", "biological_entity_id": "metabolite", "mie": false, "adverse_outcome": false },
    { "id": "KE:3", "biological_entity_id": "normal_sall4_function", "mie": false, "adverse_outcome": false },
    { "id": "KE:4", "biological_entity_id": "normal_limb_formation", "mie": false, "adverse_outcome": true }
  ],
  "key_event_relationships": [
    { "id": "KER:1", "source": "KE:1", "target": "KE:0", "relationship": ["metabolized_by", "binds_to"] },
    { "id": "KER:2", "source": "KE:0", "target": "KE:2", "relationship": ["metabolizes_into", "forms"] },
    { "id": "KER:3", "source": "KE:2", "target": "KE:3", "relationship": ["promotes", "leads_to"] },
    { "id": "KER:4", "source": "KE:3", "target": "KE:4", "relationship": ["leads_to", "results_in"] }
  ]
}
```

## Reference pathway example — Full mode, species-conditional branching

Anchors the four Full-mode annotation types (species/circumstance branching shown here; confounders, developmental windows, and initiating-event class follow the same attach-to-KE/KER, quote-backed pattern). Also predates `extraction_mode`, `source_articles`, `evidence`, and filled-in `reference_ids` in this excerpt (every node in a real file has them). Here `glucuronidation_capacity` is marked as an endpoint because nothing in this branch follows it, which is what `adverse_outcome` means in this skill — a real run's evidence would carry actual `ref_id`s, not an empty list.

```json
{
  "aop_id": "drug@hepatotoxicity_apap_1",
  "key_events": [
    { "id": "KE:0", "biological_entity_id": "cyp2e1", "mie": true, "adverse_outcome": false, "reference_ids": [] },
    { "id": "KE:1", "biological_entity_id": "parent_drug", "mie": false, "adverse_outcome": false, "reference_ids": [] },
    { "id": "KE:2", "biological_entity_id": "napqi", "mie": false, "adverse_outcome": false, "reference_ids": [] },
    {
      "id": "KE:3",
      "biological_entity_id": "glucuronidation_capacity",
      "mie": false,
      "adverse_outcome": true,
      "species_annotation": { "cat": "absent", "human": "present" },
      "molecular_basis": "ugt1a6_pseudogene_in_felids",
      "layers": ["species_conditional"],
      "reference_ids": []
    },
    { "id": "KE:4", "biological_entity_id": "gsh_depletion", "mie": false, "adverse_outcome": false, "reference_ids": [] },
    {
      "id": "KE:5",
      "biological_entity_id": "hepatocyte_necrosis",
      "mie": false,
      "adverse_outcome": true,
      "species_annotation": { "cat": "therapeutic_dose", "human": "overdose_only" },
      "layers": ["species_conditional"],
      "reference_ids": []
    }
  ],
  "key_event_relationships": [
    { "id": "KER:1", "source": "KE:1", "target": "KE:0", "relationship": ["metabolized_by", "binds_to"], "reference_ids": [] },
    { "id": "KER:2", "source": "KE:0", "target": "KE:2", "relationship": ["oxidizes_to", "forms"], "reference_ids": [] },
    {
      "id": "KER:3",
      "source": "KE:2",
      "target": "KE:3",
      "relationship": ["intercepted_by", "detoxified_by"],
      "gate_type": "species_conditional",
      "active_in": ["human"],
      "absent_in": ["cat"],
      "layers": ["species_conditional"],
      "reference_ids": []
    },
    {
      "id": "KER:4",
      "source": "KE:2",
      "target": "KE:4",
      "relationship": ["depletes", "binds_covalently"],
      "gate_type": "species_conditional",
      "active_in": ["cat"],
      "note": "engaged_only_when_KE:3_absent",
      "layers": ["species_conditional"],
      "reference_ids": []
    },
    { "id": "KER:5", "source": "KE:4", "target": "KE:5", "relationship": ["leads_to", "causes"], "reference_ids": [] }
  ]
}
```
