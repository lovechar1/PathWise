# Pathway Extraction

A Claude Code skill that pulls a biological pathway out of a batch of PDF articles: molecular initiating events, key events, key event relationships, and adverse outcomes. Everything it records comes from what each article's own text and figures say.

During extraction it uses the papers and nothing else. It doesn't fill gaps with general biology knowledge and it doesn't look anything up, so it can find pathways that are new or that branch differently from what's already registered elsewhere. New terms are minted from the articles and kept for you to review. Only at the very end, once the pathway is final, does a required check compare gene and protein names with the official HGNC and UniProt databases.

## Start here

### Before your first run

- **Claude Code**, installed and signed in. Either the Claude desktop app (its Code tab) or the terminal version works.
- **On Windows: Git for Windows** (free, from git-scm.com). The lockdown needs it to keep the helper agents apart. If it's missing, the skill tells you at the start and won't run.
- **Internet** at the end of the run, for the gene and protein name check. Nothing else in the run uses it.

### Run a pathway extraction

1. **Download the workspace.** Go to the latest PathWise release (https://github.com/raptorpharmtox/PathWise/releases/latest) and download `pathway-extraction-workspace.zip`. Unzip it somewhere easy to find, like your Desktop. You get one folder, `pathway-extraction-workspace`, with everything the skill needs, including the PathWise ontology.
2. **Open that folder in Claude Code.** In the desktop app, start a new Code session and choose the `pathway-extraction-workspace` folder. In a terminal, go into the folder and type `claude`. Open this folder itself, not a folder around it, or the safety settings won't apply.
3. **Add your papers.** Put your PDFs in the `papers` folder inside the workspace. The skill can't read files anywhere else.
4. **Ask for the pathway.** For example: "Extract the pathway for perfluorooctanoic acid–induced liver toxicity from the PDFs in papers." Add "use full mode" if you want species differences, confounders and timing too.
5. **Answer its questions.** It first checks its safety settings, then asks for anything it needs (the mode, a short topic description, how you chose the articles). At the end it asks you to settle any merges its two clustering agents disagreed on.
6. **Let the name check finish.** The gene and protein name check starts on its own. When it says the run is complete, your results are in the `pathwise_output` folder.

If a run stops partway (you close the chat, or the internet is down at the end), open a new chat in the same folder and type "finish the PathWise run". It picks up where it stopped.

**Please don't:** edit `.claude/settings.json`, delete `pathwise_output_canary.txt`, or copy the skill into your own Claude skills folder (`~/.claude/skills`). From there it would run without the safety settings.

### What the lockdown allows and blocks

| Allowed | Blocked |
|---|---|
| Reading and writing files in the workspace folder | Web search, every other website, and both browsers (the built-in one and Claude in Chrome) |
| The skills in `.claude/skills` (`pathway-extraction` and `reference-check`) | Shell commands (Bash and PowerShell) |
| Helper agents, which follow the same rules, can read files, and can write only their own result files | Past chats, saved memory, and old transcripts |
| The main conversation looking up gene and protein **names** at HGNC and UniProt, for the final check | Helper agents using the internet at all, or seeing the run's results, including each other's |
| | UniProt descriptions of what a protein does (only name fields can be requested) |
| | claude.ai connectors and plugin search |
| | Every folder outside the workspace |

The settings live in `.claude/settings.json` in the workspace. If that file is missing or changed, the skill won't run.

## What you need before running it

- **Extraction Mode:** The skill asks this first. There are two options:
  - **Simplified:** the basic pathway. It records what starts the pathway, each step along the way, how the steps connect, and the final outcome, along with the quote and citations behind each one.
  - **Full:** everything in Simplified, plus extra details whenever an article mentions them. These include differences between species, factors like sex, age, diet or genetics that change how strong an effect is, the stage of development when something happens, steps that only apply in special circumstances, and whether the trigger is genetic, chemical, or something else. It also records, when the article says so, how a key event was measured, where the article says it likely applies, whether the dose, timing and share of subjects line up from one step to the next, the shape of the response, and how long one step takes to lead to the next. These are for the record only and never decide what goes in the pathway.

  You can't switch partway through. If you pick Simplified and later want the extra details, the whole batch has to be run again.
- **A topic.** The mechanism or subject to extract, for example "Acetaminophen-Induced Hepatotoxicity."
- **A topic description** (optional, recommended). One to three sentences narrowing the topic: direction of causation, organ, exposure type. Don't describe pathway steps here, only what counts as in scope.
- **How the articles were chosen** (optional). In your own words, for example "PubMed search: acetaminophen hepatotoxicity review, 2015–2025, free full text." It's saved in `run_log.md` as a record of how the evidence was collected.
- **A folder of PDFs.** Every article you want processed, with nothing else in the folder. Use the workspace's `papers` folder. An ordered list of file paths inside the workspace also works.
- **An ontology file** (optional). A `pathwise_ontology.json` reference dictionary of terms to reuse across runs. If you have one from an earlier run, put it in the workspace folder and point to it so terminology stays consistent. If you don't have one, the run starts empty and lists every term it needs in `new_terms.json`. The skill never creates or changes an ontology file itself.

You don't need to prepare any of this in a special format. Tell Claude Code what you want extracted and where the PDFs are, and it will ask for whatever is missing.

## How to run it

In a Claude Code session opened on the lockdown workspace (see "Start here"), ask in plain language:

```
Extract the pathway for acetaminophen-induced hepatotoxicity from the PDFs in papers,
using pathwise_ontology.json.
```

## How a run works

1. **Each paper is read on its own.** The skill gives every paper to its own helper agent, a fresh copy of Claude with identical instructions. Several run at the same time, in batches if there are many papers. Each agent follows its own short set of instructions and sees only its own PDF and your ontology file. It can't see the other papers or what the other agents found, and the lockdown enforces that, so the order papers run in can't change the results. Each agent saves its own result files into a folder for its paper.
2. **Results are saved as each paper finishes.** If a run stops partway, start a new chat in the workspace and ask again. The skill offers to resume, and only redoes the papers that didn't finish. If it stopped during the end-of-run reviews, it offers to pick the reviews up where you left off.
3. **Matching terms are merged.** Different papers often use different names for the same thing, like "GSH depletion" and "glutathione depletion". Once every paper is done, terms with the same ontology ID are merged first. Then two separate clustering agents each group the remaining terms that mean the same thing, without seeing each other's answer. Terms both agents group together are merged automatically, and terms only one agent grouped are left for you to decide. Key events are done first, then relationships. The agents also suggest broader/narrower pairs, like "necrosis" and "hepatocyte necrosis", which are never merged but are kept for you to confirm.
4. **New terms are checked against your whole ontology.** Each paper's agent checks your ontology first, but a new term can still duplicate an ontology term that no paper in the run used. So after clustering, the skill searches your ontology file for each new term's likely matches, and two agents judge them. Matches both agents agree on use your existing term automatically, and the new wording is listed so you can add it as a synonym. This works with ontologies of thousands of terms: above 600 terms, the paper agents skip the ontology and this step does all the matching.
5. **The pathway is built** from the merged terms, and every cluster, every main-term choice, and how much the two clustering agents agreed are saved so you can check them afterwards.
6. **Gene and protein names are checked.** After the reviews, the separate `reference-check` skill starts on its own. It looks up the gene or protein part of each key event name at HGNC and UniProt, and leaves the rest of the name alone (in `glucuronidation_by_ugt1a1`, only `ugt1a1` is checked). Key events with no gene or protein in them are skipped. A name with one clear official symbol is renamed, with the old one kept as a synonym; anything unclear is shown to you. Each checked key event gets its HGNC id and UniProt accession (for example `P11388`) as data, never in the name. The run is marked complete only when this check finishes.

The rules for deciding when two terms mean the same thing, and which name a cluster keeps, are provisional. They'll be replaced by the PathWise ontology rules once those are agreed.

## What you get back

Everything is written to a `pathwise_output/` folder in the workspace:

| File | What it is |
|---|---|
| `articles/<pdf name>/` | One folder per article. The pathway file is named like `cyp2e1@hepatocyte_necrosis_smith_2019.json` (initiating event, `@`, adverse outcome, then the article's name): its key events and relationships, each with the quotes that support it and the citations attached to each quote, plus the list of sources it cites. An article with no key events has no pathway file (you're told about it during the run). The folder also holds the article's own new terms, any undefined abbreviations, and an untouched `original/` copy. |
| `run_log.md` | First, whether the lockdown was on for this run. Then one line per article: processed, excluded as off-topic, borderline, or failed to read, with the reason and pages read. Check here first if an article seems to be missing. |
| `reference_check.json` | The final gene and protein name check: when it ran, the HGNC version, and for each gene or protein in a key event name whether it was confirmed, renamed or left for you, with its HGNC id and UniProt accession. |
| `new_terms.json` | Every new ontology term minted this run, for your review, with the synonyms merged into each one. Nothing is added to your ontology automatically. If you do the end-of-run reviews, it also records each decision (merged, kept separate, same or different relationship, or a change to a cluster), the reason, who decided, and when. |
| `clusters.json` | The synonym list: which terms were merged as the same thing, the name each cluster kept and why, the pairs left for you to decide, and the suggested broader/narrower links. |
| `undefined_abbreviations.json` | Abbreviations the papers never spelled out, gathered for a later step that fills in definitions. Not shown in the summary. |
| `clustering/agreement.json` | How much the two clustering agents agreed, separately for key events, relationships, broader/narrower suggestions and the check against your ontology, with the full list of term pairs behind each number so you can recount them. The folder also holds each agent's raw answer. |
| `merged_tally.json` | The main result. Every key event and relationship merged across articles, with its `synonyms` (the other names articles used for it), `article_count` (how many articles support it) and `distinct_sources_cited` (how many different papers those articles cite for it). It also holds the flag lists described below. In Full mode it carries the extra detail too. |

The flag lists inside `merged_tally.json` are places to look at, not verdicts:

- `single_source_flags`: supported by only one article.
- `single_citation_flags`: supported by several articles that all cite the same one paper.
- `relationship_disagreement_flags`: two articles connect the same two key events but don't use exactly the same pair of tags (for example "activates" and "inhibits"). This can be a real disagreement or just different wording. You can sort these out in the end-of-run review.
- `unspecified_terms`: key events ending in `_unspecified` (for example `uptake_unspecified`), where the name doesn't say what to measure and the paper never said which site, actor, cell type or substrate. A general term that's still measurable, like `necrosis`, isn't marked. They're kept, and listed so you can see where the literature was vague.
- `conflicting_evidence_flags`: steps a paper still includes even though it reports a knockout, blocking or similar test that came out against them.
- `disproved_step_flags`: steps a paper says were disproved (they're kept out of that paper's pathway), and whether another paper supports them.
- `species_mismatch_flags`: relationships shown in a species their key events weren't reported in.
- `experimental_method_flags`: key events whose method the paper itself calls experimental or unvalidated.
- `condition_flags`: terms where some papers state a timing or intensity condition (like "sustained") and others don't.
- `feedback_loops`: each loop papers described, how many papers describe it, and whether they say it amplifies or dampens. Papers can disagree on that, and both answers are kept.
- `ambiguous_source_matches`: cited papers the skill had to match by author and year, or likely the same paper with different years, so you can confirm them.

## How key events are named

Every key event name has to make clear what someone would measure to see it. Beyond that, key events are as specific as each paper is, within reason: the most specific actor, site or substrate the paper states goes in the name. If a paper says GSH synthesis fell, the key event is `glutathione_synthesis`, and the enzyme too if the paper names it. If it only reports the glutathione level or a ratio, that's what is recorded, without guessing the cause.

- **Abbreviations:** genes and proteins use their official HGNC symbol (`ugt1a6`, shown as `UGT1A6`). Everything else is written out (`glutathione_synthesis`, not `gsh_synthesis`), with abbreviations like GSH kept as synonyms so papers that use them still match. An abbreviation a paper never spells out is kept as written and listed in `undefined_abbreviations.json`.
- **What stays in the name:** the site, when the paper states it (`hepatocyte_necrosis`). A direction word only when it's part of the meaning (`glutathione_depletion`); otherwise the direction goes in the relationship ("decreases"). A timing word like "sustained" only when the paper says the timing is necessary for the event to happen.
- **What never goes in the name:** species (it's a separate field, so the same event merges across species), sex, life stage, words like "insufficient," another key event, and the chemical that starts the pathway ("cisplatin-induced glutathione depletion" becomes `glutathione_depletion`).
- **Vague terms:** a general term that's still measurable, like `necrosis`, is fine. A term that doesn't say what to measure, like a bare "uptake," is kept with `_unspecified` on the end and listed at the end of the run.
- Each new term gets an id, a display label and a short definition (under 100 characters) written from the paper. Definitions can be left blank when the paper says too little.

## How relationships are written

Each relationship has exactly two tags, separated by a comma. The first says what happens to the first event, and the second says what that does to the second event, for example "NAPQI depletes glutathione" is `["increases", "decreases"]`. To keep runs repeatable, each tag is picked from your ontology's existing relationship verbs first, and a new verb is made only when none fits; every new verb is listed at the end of the run. When a paper says one event leads to another but not how, the tag is `causes`; when it only links them without saying which way the effect goes, it's `unknown`. A paper that says `unknown` where another gives a specific verb is flagged as a detail difference, not a disagreement. The paper's exact wording always stays in the quote. If a relationship reads the same from both sides, or the article only describes one side, the word is repeated, for example `["binds_to", "binds_to"]`.

Every relationship is one-way, from cause to effect, and every key event must be connected by at least one. A relationship can skip steps when the paper states it that way; it's marked `non_adjacent` when the paper says there are steps in between. Each relationship also records the species its evidence came from, whether the paper explains how the step works, and any inconsistency the paper reports (for example a case where the first event changed but the second didn't).

Each paper picks its own tags, so two papers may word the same relationship differently. After every paper is done, the clustering agents decide which tag pairs mean the same thing, and those are merged. Two articles only count toward the same relationship when both tags match exactly, in the same order, after that.

The two tags can point in different directions. `["activates", "inhibits"]` means the first event is activated, and that inhibits the second. If one article says A activates B and another says A inhibits B, that leads to a different outcome, so it is a different pathway. The skill keeps them as separate relationships and flags them.

## Feedback loops

When a paper describes a loop, such as ROS damaging mitochondria that then make more ROS, each step is drawn as a normal relationship, including the one back to the start. The loop is also named in a `feedback_loops` list, with a quote and whether the paper says it amplifies, dampens, or doesn't say. A loop is only recorded when the paper itself calls it a loop or feedback; arrows that happen to form a circle don't count. When a paper explicitly calls something feedforward (one event affecting a later one both directly and through a middle step), it's listed there too, marked `feedforward`. Both are drawn with ordinary arrows, so any pathway viewer can show them; the list just says which arrows to highlight. `merged_tally.json` counts how many papers describe each loop, and the end-of-run summary lists them.

When merging terms, the skill still refuses to create a loop that no paper described, for example by merging two terms that one paper shows as cause and effect.

## While it runs and when it finishes

While it runs, Claude tells you right away if an article fails to open, is excluded as off-topic, is borderline on-topic, or yields no key events, and gives a reason each time.

When it finishes, it prints a summary: key event and relationship totals, which articles were flagged and why, how many clusters were merged and how much the two clustering agents agreed, how many new terms matched existing ontology terms, any feedback loops, any unspecified key events, the possible duplicate term pairs by name, and, by name, any steps with conflicting evidence, steps a paper says were disproved, timing conditions some papers state and others don't, species mismatches, methods called experimental, and new relationship verbs. It then offers four optional reviews:
1. **Possible duplicates**, one at a time, including the pairs only one clustering agent grouped and possible matches to existing ontology terms. You choose merged or kept separate.
2. **Relationship disagreements**, where you mark each one as the same meaning (so the articles count together) or different (kept apart).
3. **The automatic clusters.** You see every cluster, relationship merge and ontology match as a short list and pick any you want to change: split a cluster apart, change which name it keeps, or undo a relationship merge or an ontology match.
4. **Broader/narrower links**, like "necrosis → hepatocyte necrosis." You confirm or reject each one. Nothing is merged either way; confirmed links are kept for combining pathways across papers later.

Each decision is saved with the date. It doesn't interpret the biology. That part is up to you.

## Scope

**Always included:** pathway extraction, per-article citations tied to each key event and relationship, quality notes on each (whether the article reports a competition or specificity test for that step, and whether it reports an attempt to disprove it, such as a knockout, blocking, or rescue experiment, with whether that test supported or contradicted the step; relationships also note whether the article explains how the step works; each is true, false, or unknown, and unknown is the usual answer), each key event's level of organization and the species its evidence came from, steps a paper says were disproved (kept apart from the pathway), reported inconsistencies, term matching against your ontology, and a tally across articles (both an article count and a count of distinct cited papers, with which kind of quote cited each paper).

**Full mode only:** species-specific or conditional branching (including minor pathways that only matter under specific circumstances), confounders (sex, age, diet, disease state, genetic polymorphisms, background rates, species physiology), developmental windows, initiating-event class, and the record-keeping details (how a key event was measured, where the paper says it likely applies, dose/timing/incidence patterns, response shape, and time between steps). These are recorded only when an article's own text states them. The branching, confounders and developmental windows are tagged so a future visualizer can show or hide them separately from the core chain.

**Never included:** dose or exposure study details, numbers, narrative summaries, ratings of how strong the evidence is, and judgments about whether a disagreement between articles is real biology or an extraction mistake. Disagreements get flagged, not resolved. If you want any of this, ask for it directly.

## Known limitations

- The reviewer name saved with each review decision is just a name typed in at the start of the review. It isn't verified.
- Review decisions are saved with the date only, not the time. The lockdown blocks commands, so there's no clock to read a time from.
- Claude Code's sandbox, which could let commands run with no internet, doesn't work on Windows yet. So the lockdown blocks commands completely instead.
- The lockdown blocks the claude.ai Docs connector by its ID on the account it was tested with. If your account shows that connector under a different name, it may not be blocked. All other claude.ai connectors are switched off by a general setting.
- Choosing Simplified mode means any extra detail (species, confounders, special circumstances) can only be added later by running the batch again.
- The clustering agreement numbers are counted by Claude, not calculated by code, because commands are blocked. That's why the full pair lists are saved with them, so they can be checked.
- The rules for when two terms are the same, and for which name a cluster keeps, are provisional until the PathWise ontology rules are agreed.
- The parallel extraction and clustering haven't been run on a real batch of PDFs yet.
- Gene and protein names are checked against HGNC and UniProt only at the end of a run, by name. Definitions still come from the articles; UniProt descriptions of what a protein does are deliberately not read. The UniProt version isn't recorded, only the date of the check (HGNC's version is).
- The 1,000-term cutoff for when the paper agents stop reading the ontology is an estimate, to check with a test run as the ontology grows.
- Matching new terms to your ontology searches by shared words, so a synonym that shares no words with the ontology term (like "GSH" and "glutathione") is only found if that abbreviation is stored as a synonym in the ontology.

## Future directions

- **One pathway per topic, not per review.** Right now each review article produces its own pathway file, and `merged_tally.json` counts what they share. The goal is a single combined pathway built from all the reviews on a topic. That needs a team decision first on how to handle conflicting information, and on what to keep when one review goes further than another.
- **Finding the reviews automatically.** The long-term aim is to give the agent a pathway idea and have it gather the freely available review articles itself, then build the combined pathway with weights or scores.
- **Scoring review article quality.** Rate each review with checklists such as AMSTAR, PRISMA, or SANRA, depending on the article type. The result could be an overall score or a short written assessment.
- **Improving the evidence behind each step.** The quality fields mostly come back "unknown," because reviews rarely describe the tests behind a claim. Contributors with access to the cited studies could fill these in later, and the criteria will be refined over time.
- **A new pathway naming convention.** Pathways are named after the initiating event and the adverse outcome. This is expected to change so the name no longer uses the adverse outcome.
- **Definitions from reference data.** When an article gives no definition for a gene or protein term, use its official HGNC name or UniProt protein name (both already looked up by the final check) as the definition. Left for later.
- **Filling in definitions and abbreviations.** A follow-up skill that's allowed to use outside sources could fill in the blank definitions and the abbreviations listed in `undefined_abbreviations.json`.
- **Visualizing the extra detail in RiskLytx.** Show the Full-mode layers (species differences, confounders, developmental windows) so they can be turned on and off. Also show the evidence behind each key event and relationship: the quality fields, the supporting quotes, and how many articles and cited papers back it.

## Full details

See [SKILL.md](SKILL.md) and [references/procedure.md](references/procedure.md) for the full procedure, including the exact JSON layout, the term-matching rules, and the checks run on each article.
