# Extraction Procedure — Main Skill

This is the specification for the main skill: starting a run, launching the paper agents, merging, the tally and the reviews. **Paper agents follow [article_agent.md](article_agent.md) instead**, which defines everything about one article's extraction: the naming rules, the fields on each key event and relationship, quality assessments, Full-mode fields, and the per-article file. Read article_agent.md too before Step 6, because merging and the tally work on the fields it defines.

Every choice the user makes in this procedure (resuming a run, a new folder name, the reviews in Step 8, the loop check) is asked as a pop-up with buttons using the AskUserQuestion tool; typed answers are asked as plain questions in chat, as described in "How to ask questions" in SKILL.md. When a review has more items than one pop-up holds, show the short list in chat first, then ask in pop-ups, up to four items per pop-up.

## Scope

Always in scope, in both extraction modes: one pathway file per article (key events, relationships, the stressor, MIE and adverse-outcome flags, level and species, quality assessments, disproved steps, verbatim quotes and the citations behind each quote), terminology alignment across the batch, and a final tally of how many articles *and* how many distinct cited sources support each key event and relationship.

Always out of scope, by deliberate design choice: dose or exposure numbers, narrative summaries, ratings of evidence strength, and any automated judgment about whether a disagreement between articles is real biology or an extraction error — flag it, don't resolve it. Don't add any of this on your own initiative; ask the user first if they want scope expanded.

### Extraction mode: Simplified vs. Full

Ask which mode the user wants first, before any other input, and tell them the choice is final for the run: it changes what the paper agents look for while reading, so switching later means re-reading every PDF. **Simplified** records the core pathway. **Full** also records, when an article states them, conditional branching (species, circumstance, genotype), confounders, developmental windows, initiating-event class, and the record-keeping fields (`measured_by`, `applicability_stated_by_paper`, `concordance`, `response_shape`, `time_scale`). The exact fields are in "Full mode only" in article_agent.md.

## How a run is organized

A run has two roles. The **main skill** is the conversation the user is talking to. It collects the inputs, launches helper agents, runs the merge, writes the run-level files, and talks to the user. **Helper agents** are fresh Claude instances launched with the Agent tool, each doing one job.

**Phase 1: extract each article independently.** Each article gets its own *article agent* (or paper agent), launched with identical instructions. It reads only its one PDF, article_agent.md, and (in `full` ontology matching mode) the ontology file. It writes its own result files into its own folder, `pathwise_output/articles/<pdf name>/`, and replies with a short status. It never sees another article or another agent's result, so the order articles are processed in can't change what any of them produces. Run as many at once as the session allows, in batches if needed (for example 5 at a time). Batching changes nothing (see "Isolation").

**Phase 2: merge across articles (Step 6).** Only once every article agent has finished: merge terms that share an id, cluster the remaining terms that mean the same thing with two independent *clustering agents*, check new terms against the whole ontology, and relabel.

**Phase 3: tally and review (Steps 7-8).** Build `merged_tally.json`, print the summary, and offer the reviews.

### Isolation

The workspace's lockdown settings include a hook that Claude Code runs before every file operation. For helper agents it:
- refuses to read anything whose path contains `pathwise_output` (the run folder and the `pathwise_output_canary.txt` check file);
- allows writing only to paths inside a `pathwise_output…/articles/` folder (it can't tell one article's folder from another's, so keeping each agent in its own folder relies on the prompt);
- refuses every other file tool (editing, searching, listing).

The main skill isn't affected. So each article agent saves its own results the moment it finishes, which protects them if a run stops partway, and still no helper agent can read any result. On top of that:
- Launch every helper agent fresh (the default Agent tool, never a fork of this conversation).
- Never put anything from one article (its terms, quotes, results or slug) into another agent's prompt.
- Give each article agent its own output folder, and never the same folder twice.
- Clustering agents never write files. They return their answer, and the main skill writes it.

The run folder's name must start with `pathwise_output` (for example `pathwise_output_2`), or the hook won't protect it.

### Starting a run (main skill, once)

Do this right after the lockdown checks, **before asking for any input**. Check whether `pathwise_output/` already exists and has files in it, and read its `run_log.md` status line. Read the rest of that log only if the user chooses to resume; otherwise never show, suggest or reuse anything from it (SKILL.md, "Required inputs").
- **`run status: in progress`**: a previous run stopped partway. Ask in a pop-up whether to **resume** it ("Resume the earlier run" / "Start a new run"), saying when it started and how many articles finished, but not its inputs. On resume, reuse the inputs recorded in its run log and don't ask for them again; if the log lacks an input this version of the skill requires (an older run), ask for just that input. Resuming keeps the articles that already have a line in the run log (matched by the PDF file name in each line), except lines saying `flagged by model safeguards`, and launches article agents only for the rest, flagged ones included. The user may have switched model to get past a safeguard flag, so a different model on resume is expected, not a reason to start over. If every article already has a line, go straight to Step 6. If Step 6 had started (`clusters.json` exists, or the run log says `merging`), first restore each article's working file from its untouched copy in `articles/<pdf name>/original/`, then restart Step 6.
- **`run status: reviewing`**: the tally is built and the user stopped partway through the reviews. Offer to **continue the reviews** (or start a new run): skip to Step 8, and only offer the checkpoints (8b-8e) that still have undecided items. Every decision already made is saved in `new_terms.json` and `clusters.json`.
- **`run status: awaiting reference check`**: the reviews are done but the reference check didn't finish. Don't ask; go straight to Step 9.
- **Otherwise** (`complete`), or the user chose to start a new run: the old folder stays as it is; never overwrite it without an explicit yes. Pick the first unused name of the form `pathwise_output_2`, `pathwise_output_3`, … and ask in a pop-up: "Save this run in `pathwise_output_2`" / "Use a different name" (the name must start with `pathwise_output`). Then ask for every input from scratch.

Wherever this document says `pathwise_output/`, it means whichever folder was chosen.

If ARTICLES names a folder, list every PDF in it now, in file-name order. Create `pathwise_output/run_log.md` with the lockdown check result as its first line (see "Before anything else" in SKILL.md), then the lockdown evidence and the `model:` line (see SKILL.md), then `run started: <YYYY-MM-DD>` (today's date as the session reports it, never estimated; on resume add `resumed: <YYYY-MM-DD>` and keep the first), `run by: <name>` (RUN BY, exactly as typed), then `run status: in progress`, the extraction mode, TOPIC, TOPIC DESCRIPTION, a `## How the articles were chosen` section holding ARTICLE SELECTION exactly as the user typed it (it's required, so it's never empty), the ontology file path, the ontology matching mode (below), and the full article list. Change the status line to `run status: merging` when Step 6 starts, to `run status: reviewing` once Step 7 has written `merged_tally.json`, to `run status: awaiting reference check` when Step 8 finishes (all reviews done or declined), and to `run status: complete` only when the reference check (Step 9) finishes. Nothing else may set `complete`.

**Ontology matching mode.** Helper agents can read files but not search them, so how article agents use the ontology depends on its size:
- **`full`** (600 terms or fewer in the whole file, roughly 150 KB): each article agent reads the ontology file and matches its terms against it, as a first pass.
- **`deferred`** (more than 600 terms): the file would cost each agent too much to read, so article agents skip it and mint every term provisionally. All matching then happens in Step 6c-2, where this conversation searches the file.

Count the terms with the Grep tool in count mode, searching for `"id":` in the ontology file; don't read the whole file to find out. Either way, Step 6c-2 checks every newly minted term against the whole ontology, so a term an article agent missed is still caught. If the run has no ontology file, the mode is `full`, article agents get `none: treat every term as new`, and Step 6c-2 is skipped. Record the mode and the term count in the run log.

### Launching article agents

Give every article agent the same prompt, filling in only the bracketed values. The output folder is `pathwise_output/articles/<pdf name>/`, where the PDF's file name (without `.pdf`) is lowercased with every character other than a-z and 0-9 turned into `_`.

> You are extracting one article for the PathWise pathway-extraction skill. Read `.claude/skills/pathway-extraction/references/article_agent.md` and follow it exactly, for this one article only.
> - PDF: [path]
> - EXTRACTION MODE: [Simplified or Full]
> - TOPIC: [topic]
> - TOPIC DESCRIPTION: [description]
> - ONTOLOGY FILE: [path, or "none: treat every term as new"]
> - ONTOLOGY MATCHING MODE: [full or deferred]
> - OUTPUT FOLDER: [pathwise_output/articles/<pdf name>/]
>
> Don't read any other file. In deferred mode, don't read the ontology file either. Write files only into your OUTPUT FOLDER.

Every input is settled at the start, and article agents can't ask the user anything, so never launch one with an input still open.

### When an article agent finishes

**If the model's safeguards flagged the agent.** Sometimes an agent returns an error instead of a reply, saying the model's safeguards flagged the request (for example "API Error: Opus 5.5's safeguards flagged this session … Details: `[bio]`"). This is the model's own content check, not the lockdown and not a problem with the article. Then:
- Don't relaunch the article on the same model, and never reword the prompt to try to get past the check: it would be flagged again, and getting around it isn't allowed.
- Append `<pdf_file> — flagged by model safeguards: "<the error message, word for word, first 200 characters>"` to `run_log.md`. A flagged article has no slug yet, so use its PDF name. This line doesn't count as finished: resuming redoes every flagged article.
- Tell the user straight away, quoting the error.
- If the first batch of agents is all flagged, don't launch the rest. Keep `run status: in progress` and tell the user, in plain words: "The model's safety check stopped these articles. Start a new chat in this workspace, choose a different model in the model menu (for example Sonnet 5.5), and ask for the pathway again with the same inputs. The skill will offer to resume and will redo only the flagged articles." If only some are flagged, finish the others first, then say the same thing about the flagged ones, and don't start Step 6 until they're done or the user says to go on without them (then log them as `left out by user after safeguard flag`).

Otherwise its reply is a short JSON status (see "Write your files and reply" in article_agent.md). The main skill immediately:
1. Checks the reply is that JSON, and uses the Glob tool to check that every file in `files_written` exists in the agent's output folder. If the reply or a file is missing, relaunch that article once with the same prompt but a fresh output folder (`<pdf name>_r2`), because an agent can't overwrite files it can't read; note the first folder as abandoned in the run log and ignore it from then on. If it fails again, log the article as `failed to process` with the reason.
2. Appends the article's line to `run_log.md`: `<article_slug> (<pdf_file>) — <status> (reason: <reason>) — <pages_read> pages read — <key_events> key events`.
3. Passes the `callout` to the user straight away, in a sentence or two. Don't hold it for the end of the run.

Never rewrite or retype an agent's files. They're already saved, with the quotes exactly as the agent copied them.

Article agents run in parallel, so callouts arrive in the order the agents finish. That's fine.

**Two articles with the same slug.** Once every agent has finished, check the slugs in the run log. If two articles share one, the article first in file-name order keeps it, and the other gets a `_b` suffix (then `_c`, and so on). In that article's files, including its `original/` copies, use the Edit tool to change the slug in `source_article.article_slug`, `source_articles`, `prompted_by` and `article_slug` values to the suffixed one. Leave `aop_id` and the file name as they are, so they keep matching each other (files can't be renamed without a shell); note the change in the run log.

## Step 6: Merge terms across articles (main skill)

Starts only once every article agent has returned and its result is written. Every article was extracted on its own, so the same concept will often carry different names in different articles (`glutathione_loss` in one, `glutathione_depletion` in another). This step finds those and gives each concept one name. Key events are done first, and relationships second, because two relationships can only be compared once the key events at both ends have been settled.

The article agents already saved an untouched copy of each pathway file (and any `disproved_steps.json`) in `articles/<pdf name>/original/`. Never edit those copies; they are the backup. Every relabel in this step follows the same rules as Step 8 (see "What relabeling may and may not do"): a targeted replacement of just the term text, never rewriting a whole file from memory, and never touching quotes or references.

### 6a. Merge by id

Read every article's pathway file (`articles/<pdf name>/<aop_id>.json`, not the `original/` copy) and any `disproved_steps.json` written by an article with no key events. Gather every entity term used across them (including the terms in `disproved_steps`), with the articles that use it. Terms with the same id are already the same term: two articles that both reused `cyp2e1` from the ontology, or both happened to mint `glutathione_depletion`, need no decision. Also treat two ids as the same when they're identical after lowercasing and treating spaces, hyphens, and underscores alike (`Glutathione-depletion` and `glutathione_depletion`). Nothing else is merged in this sub-step: not plurals, not abbreviations, not synonyms. Those go to clustering.

### 6b. Cluster key events (two clustering agents)

Build the **key-event term list**: one entry per distinct entity term left after 6a, each with its id, its definition (from the ontology, or from the `new_terms.json` the article agents wrote to their folders), its synonyms, whether it's in the ontology file, the articles that use it, the `level` each of those articles gave it, and one evidence quote from each of those articles. Number the entries (`T1`, `T2`, ...).

Launch two clustering agents, fresh and at the same time, with identical prompts. Neither sees the other's answer. Each gets the term list, the rules in "When two terms are the same concept" below, and this instruction:

> Group the terms that name the same biological concept. Return one JSON object in a fenced code block: `{ "groups": [ { "members": ["T3", "T8"], "reason": "<one line>", "confidence": "high" | "medium" | "low" } ], "broader_narrower": [ { "broader": "T2", "narrower": "T5", "kind": "detail" | "condition", "reason": "<one line>" } ] }`. List only groups of two or more terms. Leave out any term that has no match. Separately, in `broader_narrower`, list pairs where one term is a more specific version of the other: `"detail"` when the narrower one adds a site, actor or other detail (`necrosis` and `hepatocyte_necrosis`), `"condition"` when it adds a timing or intensity condition (`ahr_activation` and `sustained_ahr_activation`). These pairs are never groups. Each term's level is context only: a different or unknown level never decides a grouping on its own. Judge only from the names, definitions, and quotes given. Don't use outside sources or general knowledge of how this pathway usually goes, and don't read any files.

Then compare the two answers, pair by pair. Each group of n terms stands for every pair inside it (n × (n − 1) ÷ 2 pairs; a group of 3 terms is 3 pairs).
- **Agreed pair:** both agents put the two terms in the same group. Merge it automatically.
- **Disputed pair:** only one agent put them together. Don't merge it. List it in `disputed_pairs` in `clusters.json`; it goes to the review in 8b.
- **Neither:** the terms stay separate.

The final clusters are the groups of terms joined by agreed pairs (if T1–T2 and T2–T3 are both agreed, T1, T2 and T3 form one cluster).

When writing disputed pairs and broader/narrower pairs into `clusters.json` (6e), use term ids, not `T` numbers, and replace each term with its cluster's main term once 6c and 6c-2 have chosen it, since the other members no longer appear in the per-article files. Drop a pair whose two terms end up in the same cluster.

**Broader/narrower suggestions.** Compare the two agents' `broader_narrower` lists the same way: a pair counts as agreed when both agents list the same two terms with the same one as broader. Nothing is merged or relabeled because of these, and they never change a per-article file or the tally. They're saved in `clusters.json` as `broader_narrower_candidates`, each with `agreed_by` (`"both"`, `"agent_a"` or `"agent_b"`), for the review in 8e. A person confirms or rejects them; confirmed links are kept for a future step that combines pathways across papers. `"condition"` pairs also mean some papers state a timing or intensity condition that others don't, which may be a real disagreement or just less detail, so Step 8a lists them by name.

**Loop check:** before merging a cluster, check every per-article file for a relationship that connects two of the cluster's terms, directly or through a chain of other key events. Merging those would make a term lead to itself. Don't merge that cluster automatically; move its pairs to `disputed_pairs` with the reason `would create a loop in <article_slug>`. Loops an article itself states (its `feedback_loops`) are real findings and stay as they are; this check only stops a merge from creating a loop that no article stated. Because stated loops mean a chain can come back to where it started, visit each key event at most once when following chains.

### When two terms are the same concept

> **Provisional.** These rules are a starting point, to be replaced by the PathWise ontology rules once they're agreed. Keep them in this one section, so updating them doesn't touch anything else.

- Two terms are the same concept when they name the same biological entity or event at the same level of detail, as set by the naming rules in article_agent.md. Different spellings, abbreviations, and word order of the same thing count as the same (`ahr_activation` and `aryl_hydrocarbon_receptor_activation`).
- Greek letters written different ways are the same: the symbol, the English word, and the single Latin letter used in an HGNC symbol (`pparα`, `ppar_alpha` and `ppara`). Keep the form the Greek letter rule in article_agent.md asks for: the HGNC symbol for a gene or protein, the English word for anything else.
- A broader term and a narrower one aren't the same (`liver_injury` and `centrilobular_necrosis`; `necrosis` and `hepatocyte_necrosis`). A term with a site and the same term without one is a broader/narrower pair, not a group. Neither are a molecule and an event involving it (`acetaldehyde` and `acetaldehyde_formation`), or opposite changes (`bile_acid_accumulation` and `bile_acid_depletion`).
- A term with a timing or intensity condition and the same term without it aren't the same (`sustained_ahr_activation` and `ahr_activation`). That's a broader/narrower pair of kind `"condition"`.
- Different quantities of the same thing aren't the same: an amount, a production or synthesis rate, and a ratio (`bile_acids`, `bile_acid_synthesis`, `conjugated_to_unconjugated_bile_acid_ratio`) stay separate.
- An `_unspecified` term and a specific one aren't the same (`uptake_unspecified` and `slco1b1_uptake`), even if a quote hints they mean the same thing. A person decides that in the review.
- Species never decides a grouping: the same event reported in mouse and in human is one concept. Level of organization is context only, never a reason on its own.
- An undefined abbreviation alone is never enough to group two terms, because the same abbreviation can mean different things in different papers.
- When unsure, don't group them. A missed merge shows up in the tally and the review; a wrong merge hides a real difference.

### 6c. Choose each cluster's main term

> **Provisional.** Replace with the PathWise ontology rules for preferred terms once they're agreed.

For each cluster, pick the main term in this order:
1. A term already in the ontology file. If the cluster has two of them, don't merge it automatically; move its pairs to `disputed_pairs` with the reason `two existing ontology terms`, because the ontology file is never relabeled.
2. A term that follows a standard naming source from "Step 4: Final terms" in article_agent.md (an HGNC gene symbol, a PubChem name, or a standard clinical term).
3. The term used by the most articles.
4. The most precise wording under the granularity rule and the naming rules in article_agent.md (`aryl_hydrocarbon_receptor_activation` over `ahr_on`).
5. If it's still a tie, the term that comes first alphabetically. Mark the cluster `main_term_tie: true`, so the review in 8d shows it.

Relabel every other member to the main term in every per-article file (`biological_entity_id`, and the `term`, `source_term` and `target_term` fields in `disproved_steps`; nothing else). Every later entity relabel (6c-2, 8b, 8d) changes these same fields. The merged key event keeps the main term's `label` and `definition`; the other members become its synonyms (terms only, without their definitions).

### 6c-2. Check new terms against the whole ontology

Clustering only sees terms used in this run. A newly minted term can still duplicate an ontology term that no article in this run happened to use (for example `glutathione_depletion` minted while the ontology already has it under different wording), and in deferred ontology matching mode, article agents didn't check the ontology at all. This step catches those. It's kept light: it runs once per **new main term** (the main term of every cluster made only of newly minted terms, plus every newly minted term that wasn't clustered), never once per synonym, and only for terms that have candidates.

1. **Find candidates (this conversation, not an agent).** Helper agents can't search files, so this conversation does it. For each new main term, use the Grep tool on the ontology file to search for each meaningful word in its id and label and for each of its synonyms and abbreviations (`glutathione`, `depletion`, `GSH`), case-insensitive. Do this in one Grep call per new term, joining the words with `|` (`glutathione|depletion|GSH`), in content mode with two lines of context before each match, so a match on a `label` or `definition` line still shows the term's `id`. Collect the matching ontology terms (id, label, definition), up to the 10 closest per new term. If a search finds nothing, that term has no candidates and needs no further check.
2. **Judge (two clustering agents).** If any term has candidates, launch two fresh agents at the same time with identical prompts. Each gets the list of new main terms that have candidates (each with its definition, synonyms and one evidence quote), the candidates for each, the rules in "When two terms are the same concept", and this instruction:

> For each new term, say which candidate ontology term, if any, names exactly the same concept at the same level of detail. Return one JSON object in a fenced code block: `{ "matches": [ { "new_term": "<id>", "ontology_term": "<id>", "reason": "<one line>", "confidence": "high" | "medium" | "low" } ] }`. List only real matches; a broader or narrower candidate is not a match. Judge only from what's given. Don't use outside sources and don't read any files.

3. **Apply.** A match both agents give is applied automatically: relabel the new term (and every member of its cluster) to the ontology id in every per-article file, and note it for 6f, where its `new_terms.json` entry is marked `"merged_by": "ontology_check"` and the new wording is added to `ontology_synonyms_to_add`, so a person can add it to the ontology and future runs match it straight away. A match only one agent gives is not applied; it goes in `disputed_pairs` with `"kind": "ontology_match"`, for the review in 8b. Run the loop check from 6b before applying any match. Count the agreement the same way as 6b and save it in `clustering/agreement.json` under `ontology_check`, with both raw answers saved as `clustering/ontology_check_agent_a.json` and `_agent_b.json`. Record every applied match in the `ontology_matches` list in `clusters.json` (6e), so Step 7 can show it as a synonym and 8d can undo it.

4. **Relationship verbs (deferred mode only).** In deferred mode, article agents didn't see the ontology's relationship verbs. Read the ontology's relationship-type category (it's short) and check every distinct tag used in the per-article files. A tag that is already an ontology verb needs nothing. For the rest, give both judging agents the tags (each with one evidence quote) and the list of ontology verbs, and ask which verb, if any, means the same thing (in the same prompt as step 2 when that runs, or in a launch of their own), returning `{ "verb_matches": [ { "tag": "<tag>", "ontology_verb": "<id>", "reason": "<one line>" } ] }` in a fenced code block. Save the agreement under `relationship_verbs` in `clustering/agreement.json`. A verb both agents give replaces the tag in every per-article file (the `relationship` array only); a tag with no agreed match becomes a new relationship verb in `new_terms.json` (with `id`, `label`, `definition` and `direction`, written by this conversation from the quotes) and is listed in 8a. Record both in `ontology_matches` with `"kind": "relationship_verb"`.

### 6d. Cluster relationships (two clustering agents)

After the key-event relabel, find every pair of key events that's connected by relationships with more than one distinct tag pair across articles (for example `n_acetyl_p_benzoquinone_imine` to `glutathione` as `["increases", "decreases"]` in one article and `["increases", "degrades"]` in another). Leave out tag pairs that differ from the others only where they have `unknown`; those are a detail difference, not a wording question (Step 7). Each such pair of key events is one **relationship group**, numbered `R1`, `R2`, and so on. Give each group's tag pairs, the articles that use each pair, and one evidence quote for each.

Launch two clustering agents, fresh and at the same time, with identical prompts:

> For each relationship group, sort its tag pairs into sets that mean the same thing. Return one JSON object in a fenced code block: `{ "groups": [ { "group": "R1", "same_meaning_sets": [ { "pairs": [["increases", "decreases"], ["increases", "degrades"]], "reason": "<one line>", "confidence": "high" | "medium" | "low" } ] } ] }`. List only sets of two or more pairs. Pairs that describe opposite effects (`activates` and `inhibits`, `increases` and `decreases`) are never the same meaning. The order of the two tags matters: `["activates", "inhibits"]` and `["inhibits", "activates"]` are different. Judge only from the tags and quotes given, and don't read any files.

Compare the two answers pair by pair, as in 6b. Merge agreed pairs. For each merged set, keep the tag pair used by the most articles; if that's a tie, keep the pair whose tags are both already in the ontology file, and otherwise the first alphabetically. Change the `relationship` array on that one relationship (the one between those two key events) in each article that used another pair from the set. Change nothing else: not other relationships that use the same verbs, and not `evidence`, `additional_evidence`, `reference_ids`, `quality`, or the `references` list. Disputed pairs aren't merged. Step 7 lists them in `relationship_disagreement_flags` for the review in 8c.

### 6e. Write the clustering record and the agreement numbers

Write `pathwise_output/clusters.json`:

```json
{
  "key_event_clusters": [
    {
      "main_term": "glutathione_depletion",
      "main_term_rule": "most articles",
      "main_term_tie": false,
      "members": [
        { "term": "glutathione_depletion", "in_ontology": false, "articles": ["smith_2019", "lee_2020"] },
        { "term": "glutathione_loss", "in_ontology": false, "articles": ["jones_2021"] }
      ],
      "reasons": { "agent_a": "<one line>", "agent_b": "<one line>" }
    }
  ],
  "relationship_clusters": [
    {
      "source": "n_acetyl_p_benzoquinone_imine",
      "target": "glutathione",
      "kept_relationship": ["increases", "decreases"],
      "merged_pairs": [ { "relationship": ["increases", "degrades"], "articles": ["jones_2021"] } ],
      "reasons": { "agent_a": "<one line>", "agent_b": "<one line>" }
    }
  ],
  "disputed_pairs": [
    { "kind": "key_event", "terms": ["n_acetyl_p_benzoquinone_imine_formation", "n_acetyl_p_benzoquinone_imine_production"], "proposed_by": "agent_a", "reason": "<the proposing agent's reason, or why it wasn't merged automatically>" },
    { "kind": "ontology_match", "terms": ["glutathione_reduction", "glutathione_depletion"], "proposed_by": "agent_b", "reason": "<the proposing agent's reason>" }
  ],
  "ontology_matches": [
    { "kind": "key_event", "new_term": "glutathione_loss", "cluster_members": ["glutathione_loss"], "ontology_term": "glutathione_depletion", "articles": ["lee_2020"], "reasons": { "agent_a": "<one line>", "agent_b": "<one line>" } },
    { "kind": "relationship_verb", "new_term": "lowers", "ontology_term": "decreases", "articles": ["lee_2020"], "reasons": { "agent_a": "<one line>", "agent_b": "<one line>" } }
  ],
  "broader_narrower_candidates": [
    { "broader": "necrosis", "narrower": "hepatocyte_necrosis", "kind": "detail", "agreed_by": "both", "reasons": { "agent_a": "<one line>", "agent_b": "<one line>" } },
    { "broader": "c_jun_n_terminal_kinase_activation", "narrower": "sustained_c_jun_n_terminal_kinase_activation", "kind": "condition", "agreed_by": "agent_a", "reasons": { "agent_a": "<one line>" } }
  ]
}
```

In an `ontology_match` pair, the second term is the ontology term.

Write `pathwise_output/clustering/agreement.json` with the agreement numbers, separately for key events, broader/narrower suggestions, the ontology check (6c-2, when it ran), relationship verbs (6c-2 step 4, deferred mode only) and relationships:
- `agreed_pairs`, `only_agent_a`, `only_agent_b`: each the full list of pairs, so anyone can recount the numbers.
- `agreed_count`, `only_agent_a_count`, `only_agent_b_count`: the lengths of those lists.
- `agreement_percent`: `agreed_count ÷ (agreed_count + only_agent_a_count + only_agent_b_count) × 100`, rounded to a whole number. If both agents proposed nothing, write `null` and say so; it isn't 0% or 100%.

Also save each agent's raw answer, as returned, to `pathwise_output/clustering/key_events_agent_a.json`, `key_events_agent_b.json`, `relationships_agent_a.json`, and `relationships_agent_b.json`.

Shell commands are blocked, so these numbers are counted, not calculated by code. Count from the lists you've written into the file, and check that each count matches its list's length before saving.

### 6f. Build `new_terms.json`

Combine every article's `pathwise_output/articles/<pdf name>/new_terms.json` into `pathwise_output/new_terms.json`: one entry per distinct new term, with `prompted_by` listing every article that minted it. When several articles minted the same id, keep the `label` and `definition` of the first of them in filename order, and combine their `synonyms`. In deferred mode, also add the new relationship verbs from 6c-2 step 4, with `prompted_by` listing the articles that use each. For a term that was clustered into a different main term, keep its entry and mark it `"status": "merged_into"`, `"merged_into": "<main term>"`, and `"merged_by": "clustering"`; for a term matched to an ontology term in 6c-2, use `"merged_by": "ontology_check"`. Its other fields stay as minted, so the history is visible. Give each main term's entry a `synonyms` list: the synonyms its articles gave it plus the terms merged into it, as terms only (no definitions). The main term keeps its own `label` and `definition`. Add an `ontology_synonyms_to_add` list: for each 6c-2 match, and for each new term clustered into an ontology main term in 6c, the ontology term and the new wording to add to it as a synonym. If a merged-away entry carries `possible_duplicate_of`, copy that flag and its `reason` to its main term's entry, unless the main term is that ontology term already. The per-article `new_terms.json` files aren't changed.

Also combine every article's `pathwise_output/articles/<pdf name>/undefined_abbreviations.json` into `pathwise_output/undefined_abbreviations.json`, one entry per abbreviation with every article and term it appeared in, after relabeling. This file isn't mentioned in the summary; it's there to be gathered for a later step that fills in definitions.

## Step 7: Merge across articles and produce the remaining output files

Once Step 6 has finished relabeling, read every per-article file back in and produce:

- `pathwise_output/new_terms.json` is already built, in Step 6f. In Step 7 only check it: every term used in any per-article file is either in the ontology file or in `new_terms.json`. Don't rewrite it here. If Step 7's merge is run again later (Step 8 does this after relabeling), regenerate **only** `merged_tally.json`, because by then `new_terms.json` also holds the review decisions and `merged_into` marks from Step 8.
- `pathwise_output/merged_tally.json` — built by joining the per-article files on each KE's `biological_entity_id` (not its local `KE:N` id, which only exists within one article) and each KER's source entity, target entity, and relationship terms. A `relationship` field is two tags, the source-side tag first and the target-side tag second (see "Relationships" in article_agent.md). Articles describe the **same** relationship only when they connect the same two key events and both tags match exactly, position by position: first tag with first tag, second tag with second tag. The tags are never treated as an unordered set, so `["activates", "inhibits"]` and `["inhibits", "activates"]` are different relationships. Because Step 6d has already merged the tag pairs both clustering agents agreed mean the same thing, articles describing the same relationship should mostly carry the same pair by now. When the same two key events end up with more than one distinct pair, keep each pair as its own entry. If the pairs differ only where one of them has `unknown` (for example `["unknown", "unknown"]` against `["increases", "decreases"]`, or `["increases", "unknown"]` against `["increases", "decreases"]`), list them in a `detail_difference_flags` array instead (the two key events, each pair, and which articles use it): one article said less, which isn't a disagreement. Otherwise list them in a `relationship_disagreement_flags` array, in the same shape. The difference may be a real disagreement (for example `["activates", "activates"]` versus `["inhibits", "inhibits"]`) or a same-meaning pair the clustering agents disagreed on in Step 6d (for example `["upregulates", "increases"]` versus `["upregulates", "synthesizes"]`). Don't try to judge which; a human decides. For each, record:
  - `synonyms`: for a key event, every other term that Step 6 (or a Step 8 review) merged into it, each with the articles that used it, from `clusters.json` (its `key_event_clusters` and `ontology_matches`): `[{ "term": "glutathione_loss", "articles": ["jones_2021"] }]`. For a relationship, the other tag pairs merged into its pair, in the same shape (`"relationship"` instead of `"term"`). `[]` when nothing was merged in. This puts the article's own wording right next to the key event, so nobody has to open `clusters.json` to see it.
  - `article_count` and `supporting_articles`: how many articles support it, and which ones — the original tally. One quote supporting several steps (a chain split into separate key events) counts once for each step; that's correct, not double counting, because counts are per step.
  - `per_article`: each contributing article's own values. For a key event: `stressor` (when true), `mie`, `adverse_outcome`, `source_type`, `level`, `species`, and `ontology_match` when present. For a relationship: `species` and `adjacency`. Different levels or species across articles are listed, not reconciled.
  - `distinct_sources_cited` and `cited_sources`: collect every `ref_id` on every quote of every contributing article's version of this node (every quote listed in "Step 3C" of article_agent.md), resolve them back to that article's own reference-list entries (author/year/title/journal/doi), then deduplicate across **all** contributing articles — the same primary source is often cited by more than one review in the batch, and that shouldn't inflate the count. Decide whether two entries are the same paper in this order, never on first author + year alone when titles are available (two different "Jones et al. 2012" papers must stay separate): (1) if both entries have a `doi`, same paper iff the DOIs match (case-insensitive); (2) otherwise, if both have a title and the normalized titles match (lowercased, punctuation and extra whitespace stripped): if the years also match, same paper; if the first author matches but the years differ (typically a preprint versus its published version), treat it as a **likely match** — count it once — and list it in `ambiguous_source_matches` for manual review, noting whether the journals match (if both entries have one) or differ; if the first author differs too, treat them as different papers; (3) only if a title is missing on either or both sides, fall back to first author + year, and list that pairing in an `ambiguous_source_matches` array in `merged_tally.json` (both entries, which articles they came from) so a human can confirm — don't silently merge or split it. Before writing `merged_tally.json`, re-check that every source merged via this fallback appears in `ambiguous_source_matches`; a fallback merge that isn't listed there is a mistake. Where titles differ slightly because of typos or abbreviation but author and year match, treat as different and list it in `ambiguous_source_matches` too; undercounting a shared source is the safer error than silently merging two different papers. `cited_sources` is the deduplicated list (`{ "first_author": ..., "year": ..., "title": ..., "journal": ..., "doi": ..., "cited_for": [...] }`); `distinct_sources_cited` is its length. `cited_for` lists which kinds of quote cited that source, using the field names (`"evidence"`, `"additional_evidence"`, `"disprove_attempts_supported"`, `"disprove_attempts_contradicted"`, `"disprove_attempts"` (a quote with no outcome, such as one saying no test was done), `"counterfactual_evidence"`, `"mechanism_stated"`, `"inconsistencies"`, `"method_flag"`, and in Full mode `"concordance"`, `"time_scale"`, `"response_shape"`, `"measured_by"`, `"applicability_stated_by_paper"`, `"confounders"`, `"special_circumstances"`, `"developmental_window"`), so a study cited only for an inconsistency or a failed test isn't mistaken for support. This is a different number from `article_count` on purpose — a KE backed by 1 article citing 4 distinct primary sources is better evidenced than one backed by 3 articles all citing the same single source, and this makes that visible.
  - `quality`: for each criterion separately, which contributing articles gave `true`, `false`, and `"unknown"` for their own version of this node: `{ "counterfactual_evidence": { "true": [...], "false": [...], "unknown": [...] }, "disprove_attempts": { "true": [...], "false": [...], "unknown": [...] } }`, plus `mechanism_stated` in the same shape for a relationship. Also `disprove_outcomes`: which articles reported a `supported` result and which a `contradicted` one (`{ "supported": [...], "contradicted": [...] }`; an article can be in both). The length of each list is the count. This is not a combined value: each article's own assessment and its supporting quotes stay in its per-article file, and the criteria are never added together.
  - `inconsistencies` (relationships): the articles that reported an inconsistency for it, `[]` when none.
  - In Full mode only: a `layers` field (union of every contributing article's `layers` values for this KE/KER) and a `layer_details` array, one entry per contributing article that supplied any Full-mode annotation: `{ "article_slug": "...", "species_annotation": ..., "molecular_basis": ..., "gate_type": ..., "active_in": ..., "absent_in": ..., "note": ..., "special_circumstances": ..., "confounders": ..., "developmental_window": ..., "initiating_event_class": ..., "measured_by": ..., "applicability_stated_by_paper": ..., "concordance": ..., "response_shape": ..., "time_scale": ... }`, including only the sub-fields that article actually populated (values only; the quotes stay in the per-article files). Don't reconcile disagreements between articles here (e.g. one says a branch is species-conditional on rat/human, another gives different species) — list both entries under `layer_details` and let a human notice the discrepancy, same as `single_source_flags` below.
- Within `merged_tally.json`, a `single_source_flags` array: every key event or relationship supported by only one article (`article_count` of 1), with no other condition. Don't judge whether these are real biological differences or extraction misses — just surface them.
- A `feedback_loops` array, built from every article's `feedback_loops` after Step 6's relabeling. Describe each loop by the `biological_entity_id`s of its key events, in order, and by its closing relationship (`source`, `target`, `relationship`, as entities and tags). Articles describe the same loop when their loops go through the same key events in the same cyclic order, whichever key event they start from (A→B→C→A is the same loop as B→C→A→B). The steps' relationship tags don't have to match; those are tallied as relationships. A `"feedforward"` entry is matched only to other feedforward entries with the same key events in the same order. For each loop, record `type`, `key_events` (in the order of the first article that describes it), `closing_relationship`, `article_count`, `supporting_articles`, and `effect` as the articles that said each value: `{ "amplifies": [...], "dampens": [...], "unstated": [...] }`. If articles disagree on the effect, keep both lists; don't pick one. A loop whose steps are only partly shared by another article's loop is a different loop.
- An `unspecified_terms` array: every key event whose term ends in `_unspecified` (or uses the ontology's own marker for this), with the articles that use it: `[{ "term": "uptake_unspecified", "articles": ["smith_2019"] }]`. These are kept on purpose; the list shows the user where the literature was vague.
- A separate `single_citation_flags` array: any KE/KER where `article_count` is more than 1 but `distinct_sources_cited` is only 1 — several articles all repeating the same single primary source is a materially weaker claim than the article count alone suggests, and it's a distinct condition from `single_source_flags` (which is about article coverage, not citation depth), so keep the two arrays separate rather than merging them.
- A `conflicting_evidence_flags` array: every key event or relationship in the pathway where any article reports a `contradicted` disprove result, with the articles that reported `contradicted` and any that reported `supported`. A step an article still asserts while also reporting a test against it is conflicting evidence, even if no test supports it. This is the one quality result the user is told about (Step 8a).
- A `disproved_step_flags` array: every entry in any article's `disproved_steps` (after relabeling), including articles that had no key events and wrote only a `disproved_steps.json`, with the article that disproved it, and the articles that support the same key event or relationship in their pathway, if any. A disproved relationship has no tag pair, so match it on its source and target terms only: any relationship between the same two key events counts as supporting it. A step one article disproves and another supports is a disagreement in the literature, kept for a person to judge.
- A `species_mismatch_flags` array: every relationship where any article's relationship `species` names a species that isn't in both of its key events' `species` for that same article. `"unspecified"` never counts as a mismatch. This is a fixed comparison, with no judgment about biology.
- An `experimental_method_flags` array: every key event carrying a `method_flag` in any article, with those articles.
- A `condition_flags` array: the `"condition"` pairs from `broader_narrower_candidates` in `clusters.json` (a term with a timing or intensity condition, and the same term without it), with the articles that use each side.

`articles_included` lists the slugs of articles that have a pathway file (excluded and unreadable articles are left out; they are in `run_log.md`). `run_by` and `run_started` are copied from `run_log.md`; `tally_built_on` is the date this file was last written (it's rewritten after review changes), from the date the session reports. `models` records which Claude models did the work: `main` is the `model:` line from `run_log.md` (every line, if the run was resumed), and `article_agents` lists each distinct `extracted_by_model` value from the pathway files with the articles that model extracted, so a batch that mixed models shows it. Overall shape of `merged_tally.json` (merged entries have no ids of their own; a key event is identified by its `biological_entity_id`, a relationship by its `source` and `target` entities plus terms). A merged `stressor`, `mie` or `adverse_outcome` is `true` if any contributing article marks it true; a merged `gene_parts` has one entry per symbol used by any contributing article, and its `form` is that form when every article that gives the symbol agrees, otherwise `"mixed"` (for example one article reports `acox1` mRNA and another ACOX1 activity; each `per_article` entry for a key event with gene parts includes that article's own `gene_parts`, so the difference stays visible); if `reference_check.json` exists, each key event also gets its `gene_refs` from it (see Step 9); each article's own values stay visible in `per_article`, so a disagreement can be seen. The quotes themselves stay in the per-article files and are not copied here.

```json
{
  "topic": "<TOPIC>",
  "extraction_mode": "full",
  "run_by": "<RUN BY>",
  "run_started": "2026-11-12",
  "tally_built_on": "2026-11-12",
  "models": {
    "main": ["Claude Opus 5.5 (claude-opus-5-5)"],
    "article_agents": [{ "model": "Claude Opus 5.5 (claude-opus-5-5)", "articles": ["smith_2019", "jones_2021"] }]
  },
  "articles_included": ["smith_2019", "jones_2021"],
  "key_events": [
    {
      "biological_entity_id": "n_acetyl_p_benzoquinone_imine",
      "gene_parts": [],
      "mie": false,
      "adverse_outcome": false,
      "synonyms": [ { "term": "napqi", "articles": ["jones_2021"] } ],
      "article_count": 2,
      "supporting_articles": ["smith_2019", "jones_2021"],
      "distinct_sources_cited": 1,
      "cited_sources": [
        { "first_author": "Chen", "year": 2008, "title": "<title>", "journal": "<journal>", "doi": null, "cited_for": ["evidence"] }
      ],
      "per_article": [
        { "article_slug": "smith_2019", "mie": false, "adverse_outcome": false, "source_type": "text", "level": "molecular", "species": ["mouse"] },
        { "article_slug": "jones_2021", "mie": false, "adverse_outcome": false, "source_type": "both", "level": "molecular", "species": ["unspecified"], "ontology_match": "wording" }
      ],
      "quality": {
        "counterfactual_evidence": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] },
        "disprove_attempts": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] },
        "disprove_outcomes": { "supported": [], "contradicted": [] }
      },
      "layers": [],
      "layer_details": []
    }
  ],
  "key_event_relationships": [
    {
      "source": "cyp2e1",
      "target": "n_acetyl_p_benzoquinone_imine",
      "relationship": ["upregulates", "increases"],
      "synonyms": [ { "relationship": ["upregulates", "synthesizes"], "articles": ["jones_2021"] } ],
      "article_count": 2,
      "supporting_articles": ["smith_2019", "jones_2021"],
      "distinct_sources_cited": 2,
      "cited_sources": [
        { "first_author": "Chen", "year": 2008, "title": "<title>", "journal": "<journal>", "doi": null, "cited_for": ["evidence", "disprove_attempts_supported"] },
        { "first_author": "Park", "year": 2015, "title": "<title>", "journal": "<journal>", "doi": null, "cited_for": ["disprove_attempts_contradicted"] }
      ],
      "per_article": [
        { "article_slug": "smith_2019", "species": ["mouse"], "adjacency": "adjacent" },
        { "article_slug": "jones_2021", "species": ["unspecified"], "adjacency": "adjacent" }
      ],
      "quality": {
        "counterfactual_evidence": { "true": [], "false": [], "unknown": ["smith_2019", "jones_2021"] },
        "disprove_attempts": { "true": ["smith_2019"], "false": [], "unknown": ["jones_2021"] },
        "mechanism_stated": { "true": ["jones_2021"], "false": [], "unknown": ["smith_2019"] },
        "disprove_outcomes": { "supported": ["smith_2019"], "contradicted": ["smith_2019"] }
      },
      "inconsistencies": [],
      "layers": [],
      "layer_details": []
    }
  ],
  "single_source_flags": [
    { "kind": "key_event", "item": "glutathione_depletion", "supported_by": "smith_2019" }
  ],
  "conflicting_evidence_flags": [
    { "kind": "relationship", "item": { "source": "cyp2e1", "target": "n_acetyl_p_benzoquinone_imine", "relationship": ["upregulates", "increases"] }, "supported": ["smith_2019"], "contradicted": ["smith_2019"] }
  ],
  "disproved_step_flags": [
    { "kind": "relationship", "item": { "source": "glutathione_depletion", "target": "hepatocyte_apoptosis" }, "disproved_by": ["lee_2020"], "supported_by": ["smith_2019"] }
  ],
  "species_mismatch_flags": [
    { "item": { "source": "cyp2e1", "target": "n_acetyl_p_benzoquinone_imine", "relationship": ["upregulates", "increases"] }, "article_slug": "lee_2020", "relationship_species": ["rat"], "source_species": ["human"], "target_species": ["human"] }
  ],
  "experimental_method_flags": [
    { "term": "mitochondrial_permeability_transition", "articles": ["jones_2021"] }
  ],
  "condition_flags": [
    { "broader": "c_jun_n_terminal_kinase_activation", "broader_articles": ["jones_2021"], "narrower": "sustained_c_jun_n_terminal_kinase_activation", "narrower_articles": ["smith_2019"] }
  ],
  "feedback_loops": [
    {
      "type": "feedback",
      "key_events": ["reactive_oxygen_species_production", "mitochondrial_dysfunction"],
      "closing_relationship": { "source": "mitochondrial_dysfunction", "target": "reactive_oxygen_species_production", "relationship": ["increases", "increases"] },
      "article_count": 2,
      "supporting_articles": ["smith_2019", "jones_2021"],
      "effect": { "amplifies": ["smith_2019"], "dampens": [], "unstated": ["jones_2021"] }
    }
  ],
  "unspecified_terms": [
    { "term": "uptake_unspecified", "articles": ["smith_2019"] }
  ],
  "single_citation_flags": [
    { "kind": "key_event", "item": "n_acetyl_p_benzoquinone_imine", "article_count": 2, "only_source": { "first_author": "Chen", "year": 2008, "title": "<title>" } }
  ],
  "relationship_disagreement_flags": [
    {
      "source": "n_acetyl_p_benzoquinone_imine",
      "target": "glutathione",
      "groups": [
        { "relationship": ["increases", "decreases"], "articles": ["smith_2019"] },
        { "relationship": ["increases", "increases"], "articles": ["jones_2021"] }
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

Runs after Step 7, once every article's file and `merged_tally.json` are written. 8a only adds what's said to the user. Of the four optional review checkpoints, 8e only records decisions; the other three (8b, 8c and 8d) can change term labels inside the per-article files, update `clusters.json`, and then regenerate `merged_tally.json`, and nothing else (see "What relabeling may and may not do"). To keep that safe: each article's `original/` copy holds its file as the article agent wrote it, so never edit those copies; make each relabel a targeted replacement of just the term text, never by re-writing a whole JSON file from memory, which risks altering quotes; and regenerate `merged_tally.json` only after the relabeling is finished. If the session is interrupted partway, the per-article files are the source of truth, so just regenerate the tally from them. The ontology file itself is never modified at any point in Step 8; every new or adopted term lives in `pathwise_output/new_terms.json`, for a human to add to the ontology later.

### 8a. Summary (always print)

- Counts: total key events and total relationships in the merged tally, and how many relationships have `article_count` of 2 or more. Also the batch counts (articles processed / excluded as off-topic / failed to read) and new terms minted. In Full mode, also how many key events/relationships carry each kind of Full-mode annotation.
- A named recap of every article that triggered a callout during parsing (failed / excluded off-topic / borderline / borderline with zero key events / on-topic with zero key events): article name plus its one-line reason, e.g. "1 article flagged: smith_2019 — borderline on-topic (reason: ...)". If none, say none.
- Clustering: how many key-event clusters and relationship merges Step 6 made automatically, and how much the two clustering agents agreed, as the `agreement_percent` for key events and for relationships from `clustering/agreement.json` (e.g. "Key events: 14 clusters, the two clustering agents agreed on 82% of proposed merges"). If an agreement number is `null`, say that neither agent proposed any merges.
- The possible-duplicate term pairs (the `disputed_pairs` from `clusters.json`, plus any term an article agent flagged with `possible_duplicate_of`), listed **by name only** (e.g. "mitochondrial membrane rupture" vs. "mitochondrial swelling") — no reasons here; the reason is first shown in 8b. This is how the user learns the pairs exist even if they skip the review.
- The ontology check (6c-2): how many new terms were matched to existing ontology terms automatically, and the agreement number, if it ran.
- The feedback loops (and any feedforward entries) from `merged_tally.json`, by their key events with the article count (e.g. "1 feedback loop: reactive_oxygen_species_production → mitochondrial_dysfunction → back to reactive_oxygen_species_production (2 articles)"). If any loop's articles disagree on whether it amplifies or dampens, say so. If none, leave this line out.
- The unspecified key events from `unspecified_terms`, by name with their articles (e.g. "2 key events are unspecified because the article didn't say more: uptake_unspecified (smith_2019), binding_unspecified (lee_2020)"). This tells the user where the pathway is less certain. If none, leave this line out.
- The detail differences from `detail_difference_flags` (one article gave `unknown` where another gave a specific verb), as a count only. They aren't disagreements and aren't reviewed in 8c.
- The relationship disagreements, listed by the two key events only (e.g. "n_acetyl_p_benzoquinone_imine to glutathione"), so the user knows they exist even if they skip the review in 8c. If none, leave this line out.
- **Conflicting evidence**, from `conflicting_evidence_flags`: each key event or relationship that an article reports a contradicting test for, with the articles that reported tests against it and any that reported tests for it. Say plainly that the evidence conflicts. If none, leave this line out.
- **Disproved steps**, from `disproved_step_flags`: each step an article says was disproved, by name, with the article, and whether another article supports it. If none, leave this line out.
- The timing or intensity conditions, from `condition_flags`, by name (e.g. "sustained_c_jun_n_terminal_kinase_activation (smith_2019) vs c_jun_n_terminal_kinase_activation (jones_2021)"), so the user knows some papers state a condition others don't. If none, leave this line out.
- Species mismatches and methods the articles call experimental, from `species_mismatch_flags` and `experimental_method_flags`, by name only. If none, leave these out.
- Any new relationship verbs minted this run, by name, since each one makes runs a little less repeatable. If none, leave this line out.
- Do **not** include single-source or single-citation counts or flags anywhere in this summary — those stay in the JSON only. Don't mention undefined abbreviations either; they stay in `undefined_abbreviations.json`.

### 8b. Possible-duplicate review (interactive)

Ask: "Would you like to review the possible duplicate terms now?"

- **No** — move on; the pairs stay flagged for later (disputed pairs in `clusters.json`, `possible_duplicate_of` flags in `new_terms.json`).
- **Yes** — go through the pairs one at a time. Skip a `possible_duplicate_of` flag on an entry already marked `merged_into` (6f moved it to the main term). For each, show both terms and the one-line reason they were flagged (for a disputed pair, which clustering agent proposed it and why, or why it wasn't merged automatically), and let the user choose **merged** or **kept separate**. If merged, ask which of the two is the canonical term. If one of the two is already in the ontology file, it must be the canonical one — the ontology file is never relabeled.

Record every decision, merges and keep-separates alike, in a `resolved_duplicates` array in `pathwise_output/new_terms.json` (one entry per pair): `term_a`, `term_b`, `original_reason` (the one-line flag reason), `decision` (`"merged"` or `"kept_separate"`), `canonical_term` (merges only), `decided_by`, `decided_at`.

- `decided_by`: the RUN BY name the user gave at the start (in `run_log.md`). Only if it's missing (an older run), ask once, at the first decision, and reuse it. Don't infer it from the environment or guess.
- `decided_at`: the date of the decision, ISO 8601 (`YYYY-MM-DD`), taken from the current date the session reports, not estimated. The lockdown workspace blocks shell commands, so there's no system clock to read a time from; record the date only.
- A `kept_separate` entry is logged exactly like a merge. It documents that a person reviewed the pair and chose not to merge it.
- Before applying a merge, check every per-article file for a relationship that connects the two terms, either directly (one as source, the other as target) or through a chain of other key events. If there is one, tell the user which article and which relationship or chain it is, explain that merging would turn it into a loop (a term leading to itself) that the article didn't describe, and ask whether to merge anyway or keep the pair separate. Don't remove the relationship on your own. The question is only about a loop the merge would create; loops the article already states in `feedback_loops` stay as they are. Relationships to *other* key events need no check: they point at key events by internal id, so they follow the relabeled term automatically.
- On a merge, relabel the non-canonical term to the canonical one in every per-article pathway file in `pathwise_output/` where it appears (`biological_entity_id` and the `disproved_steps` term fields for entity terms, as in 6c; the `relationship` array for relationship types, in whichever position the term appears; the array always keeps exactly two entries, so if it then lists the same term twice, that's fine and both stay). Do not touch `evidence`, `additional_evidence`, `reference_ids`, the `references` list, or any other field. The supporting quotes stay exactly as extracted and attributed to their own article. Mark the non-canonical entry in `new_terms.json` with `"status": "merged_into"` and `"merged_into": "<canonical>"`; don't delete it. Point any other entry's `possible_duplicate_of` that named the merged-away term at the canonical term instead. When the canonical term is an ontology term (including every `ontology_match` pair), also add the merged-away wording to `ontology_synonyms_to_add`. The `resolved_duplicates` and `resolved_relationship_disagreements` records are history, so they keep the names exactly as they were when the decision was made.
- After each decision on a disputed pair, update `clusters.json`: add `"resolution": "merged"` or `"kept_separate"` to that entry in `disputed_pairs`, and on a merge, add the term to the matching cluster in `key_event_clusters` (or start a new cluster), and replace the merged-away term with the canonical one in the other `disputed_pairs` and `broader_narrower_candidates` entries (dropping any pair that then names the same term twice). Leave `clustering/agreement.json` unchanged; it records what the two agents did, not what was decided later.
- When anything was merged, regenerate `merged_tally.json` only, by re-running the merge in Step 7 (`new_terms.json` is left alone), so the tally reflects the standardized labels.

### 8c. Relationship-disagreement review (interactive)

After the duplicate review (whether or not the user went through it), if `merged_tally.json` has any `relationship_disagreement_flags`, ask: "Would you like to review relationship disagreements?" If there are none, skip this step without asking.

- **No**: move on. The flags stay in `merged_tally.json` for later.
- **Yes**: go through the flags one at a time. For each, show the two key events, every pair of tags used between them, and which articles use each pair. Ask whether the pairs mean the **same** thing (a wording difference, for example `["upregulates", "increases"]` versus `["upregulates", "synthesizes"]`) or something **different** (for example `["activates", "activates"]` versus `["inhibits", "inhibits"]`). Don't suggest an answer; the decision is the user's. If there are more than two pairs, ask which of them mean the same thing; any pairs left over are treated as different.
- If the user says **same**, ask which pair to keep. Then, in each article that used one of the other pairs, change the `relationship` array on that one relationship (the one between those two key events) to the kept pair. Change nothing else: not other relationships that use the same verbs, and not `evidence`, `additional_evidence`, `reference_ids`, `quality`, or the `references` list. Use the same backup and targeted-replacement rules as 8b. Also add the merged pairs to `relationship_clusters` in `clusters.json` (to that pair's entry, or a new one), so Step 7 lists them as the relationship's `synonyms`.
- If the user says **different**, change nothing in the article files.

Record every decision, same and different alike, in a `resolved_relationship_disagreements` array in `pathwise_output/new_terms.json`: `source` and `target` (the two key events), `pairs` (each pair as it was, with the articles that used it), `decision` (`"same_meaning"` or `"different"`), `kept_relationship` (same-meaning decisions only), `decided_by`, `decided_at` (same rules as 8b). A `"different"` entry matters as much as a same-meaning one: it records that a person looked at the disagreement and confirmed it.

When anything was changed, regenerate `merged_tally.json` only, as in 8b, so the combined relationship counts its articles together and the flag goes away.

### 8d. Cluster review (interactive)

After the relationship-disagreement review (whether or not the user went through it), if Step 6 made any clusters or ontology matches, ask: "Would you like to review the clusters and ontology matches that were made automatically?" If there were none, skip this step without asking.

- **No**: move on. The clusters stay as they are, and `clusters.json` keeps the full record for later.
- **Yes**: show a compact list of every key-event cluster, one line each: the main term, then the other members, with the number of articles for each (e.g. "glutathione_depletion ← glutathione_loss (1 article), glutathione_reduction (1 article)"). Mark any cluster with `main_term_tie: true`. Then list the relationship merges the same way. Ask which ones the user wants to change. Don't step through every cluster one at a time unless the user asks to.

For each cluster the user picks, offer:
- **Split**: move one or more members out of the cluster. Each one goes back to its own name in the per-article files that used it.
- **Change the main term**: pick another member as the main term. If a member is already in the ontology file, it must stay the main term, because the ontology file is never relabeled.
- **Undo a relationship merge**: put an article's original tag pair back on that relationship.
- **Undo an ontology match** (from `ontology_matches`): put the new term or tag back in the per-article files that used it; it returns to `new_terms.json` as a new term.

Show the ontology matches from 6c-2 in the same compact list, after the relationship merges.

Apply each change with the same backup, targeted-replacement and loop-check rules as 8b. The original names are in each article's `original/` copy. Update `clusters.json` and `new_terms.json` (`merged_into`, `synonyms`) to match, and record every change in a `resolved_clusters` array in `new_terms.json`: `cluster_main_term` (as it was), `change` (`"split"`, `"changed_main_term"`, `"undid_relationship_merge"`, or `"undid_ontology_match"`), `details` (which terms or tag pairs moved, and the new main term), `decided_by`, `decided_at` (same rules as 8b). Then regenerate `merged_tally.json` only, as in 8b.

### 8e. Broader/narrower review (interactive)

After the cluster review (whether or not the user went through it), if `clusters.json` has any `broader_narrower_candidates`, ask: "Would you like to review the suggested broader/narrower links between terms?" If there are none, skip this step without asking.

- **No**: the run is done. The suggestions stay in `clusters.json` for later.
- **Yes**: show a compact list, one line each: the broader term, the narrower term, the kind (`detail` or `condition`), and whether both clustering agents suggested it (e.g. "necrosis → hepatocyte_necrosis (detail, both agents)"). List both-agent suggestions first. Ask which ones the user confirms and which they reject; any not mentioned stay unreviewed.

Nothing in the per-article files or the tally changes: the two terms stay separate either way. Record each decision in a `resolved_broader_narrower` array in `new_terms.json`: `broader`, `narrower`, `kind`, `decision` (`"confirmed"` or `"rejected"`), `decided_by`, `decided_at` (same rules as 8b), and add `"resolution"` to the matching entry in `clusters.json`. Confirmed links are kept for a future step that combines pathways across papers.

The reviews are then done: change the run log's status line to `run status: awaiting reference check` and go straight on to Step 9 without asking. If the session ends before this, the status stays `reviewing`, and the next chat offers to continue the reviews (see "Starting a run"). Up to this point no outside database has been used: every term comes from the articles, the ontology file, and the merges in Steps 6 and 8.

## Step 9: Reference check (required)

Gene and protein names are checked against HGNC and UniProt by the separate `reference-check` skill in this workspace. This is the only step that uses the internet, and the lockdown allows only HGNC and UniProt name lookups, only from this conversation or a `web-fetch` helper agent it launches for the lookups, never from any other helper agent. Don't look anything up before this step.

Start it yourself, without asking the user: use the Skill tool to run `reference-check` on this run's output folder. If the Skill tool isn't available, read `.claude/skills/reference-check/SKILL.md` and follow it. Only the reference check may set `run status: complete`.

If the check can't finish (for example, no internet), leave the status at `awaiting reference check` and tell the user, as an instruction rather than an option: "This run isn't finished. The gene and protein name check couldn't reach HGNC or UniProt. Once you're online, open a new chat in this folder and type: finish the PathWise run. It will pick up from here." The next chat resumes at this step (see "Starting a run").

### What relabeling may and may not do

This applies to every relabel, in Step 6 and in Step 8 alike. Relabeling changes only the term label a key event or relationship is filed under (and the key event's `gene_parts` to match: set the symbols to the main term's gene parts, keeping this article's own `form` for any symbol it already had and `"unspecified"` for a symbol it didn't; for an ontology term no article used, keep only the old entries whose symbol still appears in the new id; Step 9 changes the symbol, never the form, when it renames a gene) (or, in 6d, 8c and 8d, the tag pair on one relationship). It never adds, removes, or reconnects key events or relationships, and never touches `evidence`, `additional_evidence`, `reference_ids`, or the `references` list. It can still have a consequence: if two nodes in one article end up with the same label after a merge or adoption, both nodes stay in that article's file, and Step 7 counts the article once for that term (`article_count` counts distinct articles). Say so if it happens, so the user can look at that article's file.

## What each output file is, in plain language

A run leaves several files in `pathwise_output/`. Their names don't say much on their own — make sure the user handing this off knows what's in each one and what they'd actually use it for.

**`articles/<pdf name>/<aop_id>.json`** (one per article with at least one key event, e.g. `articles/smith_2019_review/cyp2e1@hepatocyte_necrosis_smith_2019.json`)
The single-article extraction: this article's key events, its key event relationships, its own bibliographic details, and a short list of just the sources actually cited inside that evidence (not the article's full bibliography), each one assigned a `ref_id`. An article with no key events has no pathway file; if it reported disproved steps, they're in its `disproved_steps.json`. Each article's folder also holds its own `new_terms.json` and `undefined_abbreviations.json`, and an `original/` copy of the pathway file. Every key event and relationship carries `reference_ids` naming the specific `ref_id`(s) that back each of its quotes (Step 3C in article_agent.md) — so a claim can be traced to its exact citation, not just "somewhere in this article's bibliography." That reference list sits at the end of the file, after the pathway content, so opening the file shows the actual extraction first. Written the moment that article finishes, so if the run stops partway through, whichever of these already exist are complete and safe to use — nothing partial. Open one of these to sanity-check that a specific article was read correctly, independent of anything else in the batch. Each article was extracted by its own helper agent that never saw the other articles. Step 6 may since have relabeled terms in it; the file exactly as its agent wrote it is in that article's `original/` folder.

**`run_log.md`**
Starts with whether the lockdown was on and the lockdown evidence (each check and its exact result), the run status (`in progress`, `merging`, `reviewing`, `awaiting reference check` or `complete`), and the run's inputs. Then a one-line-per-article log: which articles were processed, which were processed as borderline on-topic (with the reason), which were excluded as off-topic (with the reason), which yielded no TOPIC-relevant content, which failed to open or had no readable text, how many pages were read. First stop if something seems off — e.g. if an article expected to contribute is missing from the tally, this file says whether it was excluded, came up empty, or failed outright, rather than just contributing nothing with no explanation.

**`new_terms.json`**
Every term (biological entity or relationship type) that didn't already exist in the ontology file and had to be minted during this run, plus which article(s) prompted it. Review this before adding anything permanently to the ontology — these are new, unreviewed additions. Anything carrying `possible_duplicate_of` is a term the run wasn't confident was new — a prompt for a human to decide whether it should actually merge into the existing term it resembles. If the user went through the end-of-run reviews (Step 8), this file also holds the record of those decisions: `resolved_duplicates` (each pair, the original reason, merged or kept separate, which term was kept, who decided, when), `resolved_relationship_disagreements` (each disagreement, same meaning or different, which tag pair was kept, who decided, when), `resolved_clusters` (each change made to an automatic cluster in 8d, who decided, when), and `resolved_broader_narrower` (each suggested broader/narrower link confirmed or rejected in 8e). Merged-away terms stay in the file, marked `merged_into` (with `merged_by: "clustering"` or `"ontology_check"` when Step 6 merged them), and each main term lists its `synonyms`, so the full history is recoverable. Each new term has an `id`, a `label` and a short `definition` (or `null` when the article gave too little to define it). `ontology_synonyms_to_add` lists new wordings matched to existing ontology terms, ready to add to the ontology so later runs match them straight away. Each article's own `new_terms.json`, in its `articles/` folder, keeps the list exactly as its agent wrote it.

**`undefined_abbreviations.json`**
Every abbreviation an article used without spelling it out, with the articles and terms it appeared in. It isn't mentioned in the summary; it's there to be gathered for a later step that can fill in definitions.

**`clusters.json`**
The synonym record from Step 6: every key-event cluster (the main term, why it was chosen, and every term merged into it, with the articles that used each), every relationship merge, the disputed pairs that weren't merged because only one clustering agent proposed them (including possible matches to existing ontology terms), and the suggested broader/narrower links between terms. This is where to look to see which terms were treated as the same, and why. It's also what the reviews in 8d and 8e work from.

**`clustering/agreement.json`** and the agents' raw answers in `clustering/`
How much the two clustering agents agreed, separately for key events, broader/narrower suggestions, the ontology check and relationships: the pairs both proposed, the pairs only one proposed, and the agreement percentage, with the full lists so the numbers can be recounted. The raw answer files are exactly what each clustering agent returned.

**`merged_tally.json`**
The actual deliverable. Every key event and relationship, merged across all articles that mention it, with two separate counts: `article_count` (how many articles support it) and `distinct_sources_cited` (how many distinct primary references those articles cite as evidence, deduplicated across the whole batch). A key event backed by 3 of 4 articles is a stronger claim than one backed by 1 — and one backed by 3 articles that each cite a different primary source is stronger still than one backed by 3 articles all citing the same source. This file is what makes both of those visible, which no single article's file can show on its own. Each entry also shows every article's own level and species for it, and which kinds of quote cited each source. In Full mode, entries also carry `layers` and `layer_details` wherever an article stated a species/circumstance qualifier, a confounder, a developmental window, or one of the record-keeping fields.

**`conflicting_evidence_flags`, `disproved_step_flags`, `species_mismatch_flags`, `experimental_method_flags` and `condition_flags`** (arrays inside `merged_tally.json`)
Steps an article still includes while reporting a test that came out against them; steps an article says were disproved (and whether another article supports them); relationships shown in a species their key events weren't reported in; key events whose method an article calls experimental; and terms some papers give a timing or intensity condition that others don't. All are a "look here" for a person, not a verdict.

**`single_source_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out every key event or relationship that only one article supports. A deliberate "look here," not a verdict — the run doesn't judge whether that's a real point of biological disagreement between articles or a place where extraction went wrong on one side, a human makes that call.

**`ambiguous_source_matches`** (an array inside `merged_tally.json`, not its own file)
Calls out cited papers the skill had to match on first author and year alone (because a title was missing), or that look like the same paper with different years. A human confirms whether they really are the same paper, since that affects `distinct_sources_cited`.

**`relationship_disagreement_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out two articles that connect the same two key events but don't use exactly the same pair of verbs (for example "activates" versus "inhibits", or "decreases" versus "degrades"). They are kept as separate relationships, not counted together, and surfaced so a human can tell a real disagreement from a wording difference.

**`single_citation_flags`** (an array inside `merged_tally.json`, not its own file)
Calls out key events or relationships backed by more than one article but only one distinct primary source between them — several reviews citing the same underlying study isn't the same as independent corroboration, and this is where that distinction becomes visible instead of getting flattened into a reassuring-looking article count.

**Relabeled files**
Step 6's clustering, and any merge, combined relationship, or cluster change in Step 8, changes the labels inside the per-article files and regenerates `merged_tally.json`. Quotes and references are never changed, and `clusters.json` and `new_terms.json` keep the original names and tags, reasons, who decided, and when. The per-article files exactly as their agents wrote them are kept in each article's `original/` folder.
