# Pathway Extraction

A Claude Code skill that pulls a biological pathway out of a batch of PDF articles: molecular initiating events, key events, key event relationships, and adverse outcomes. Everything it records comes from what each article's own text and figures say.

During extraction it uses the papers and nothing else. It doesn't fill gaps with general biology knowledge and it doesn't look anything up, so it can find pathways that are new or that branch differently from what's already registered elsewhere. It never checks outside ontologies either. New terms are minted from the articles and kept for you to review.

## Start here: run it in the lockdown workspace

The skill only runs inside the **lockdown workspace**, a ready-made folder in this repository called `pathway-extraction-workspace`. That folder's settings stop Claude from using anything except your PDFs. It can't use the internet, run commands, see your past chats or saved memory, or open any folder outside the workspace. That's how you know the pathway came from the papers and nothing else.

You don't have to set anything up. The settings come with the folder. If you run the skill anywhere else, it checks for the lockdown, stops, and tells you how to fix it.

1. **Download the repository.** On the PathWise GitHub page, click the green **Code** button, then **Download ZIP**. Unzip it somewhere easy to find, like your Desktop.
2. **Open the workspace folder in Claude Code.** Open the `pathway-extraction-workspace` folder that's inside the unzipped folder. In the Claude desktop app, choose that folder when you start a new Code session. In a terminal, go to that folder and run `claude`. Open the workspace folder itself, not the PathWise folder around it, or the lockdown won't apply.
3. **Put your PDFs in the `papers` folder** inside the workspace. If you have an ontology file to reuse, put it in the workspace folder too. The skill can't read files anywhere else.
4. **Start a new chat and ask for the pathway**, for example "Extract the pathway for acetaminophen-induced hepatotoxicity from the PDFs in papers." The first thing the skill does is confirm the lockdown is on, and it writes that into `output/run_log.md`.

Don't copy the skill into your own Claude skills folder (`~/.claude/skills`). From there it could run outside the lockdown. Always use it from the workspace.

### What the lockdown allows and blocks

| Allowed | Blocked |
|---|---|
| Reading and writing files in the workspace folder | Web search, web pages, and both browsers (the built-in one and Claude in Chrome) |
| The skill itself, in `.claude/skills/pathway-extraction` | Shell commands (Bash and PowerShell) |
| Helper agents, which follow the same rules | Past chats, saved memory, and old transcripts |
| | claude.ai connectors and plugin search |
| | Every folder outside the workspace |

The settings live in `pathway-extraction-workspace/.claude/settings.json`. Don't edit or delete that file. If it's missing or changed, the skill won't run.

## What you need before running it

- **Extraction Mode:** The skill asks this first. There are two options:
  - **Simplified:** the basic pathway. It records what starts the pathway, each step along the way, how the steps connect, and the final outcome, along with the quote and citations behind each one.
  - **Full:** everything in Simplified, plus extra details whenever an article mentions them. These include differences between species, factors like sex or genetics that change how strong an effect is, the stage of development when something happens, steps that only apply in special circumstances, and whether the trigger is genetic, chemical, or something else.

  You can't switch partway through. If you pick Simplified and later want the extra details, the whole batch has to be run again.
- **A topic.** The mechanism or subject to extract, for example "Acetaminophen-Induced Hepatotoxicity."
- **A topic description** (optional, recommended). One to three sentences narrowing the topic: direction of causation, organ, exposure type. Don't describe pathway steps here, only what counts as in scope.
- **A folder of PDFs.** Every article you want processed, with nothing else in the folder. Use the workspace's `papers` folder. An ordered list of file paths inside the workspace also works.
- **An ontology file** (optional). A `pathwise_ontology.json` reference dictionary of terms to reuse across runs. If you have one from an earlier run, put it in the workspace folder and point to it so terminology stays consistent. If you don't have one, the run starts empty and lists every term it needs in `new_terms.json`. The skill never creates or changes an ontology file itself.

You don't need to prepare any of this in a special format. Tell Claude Code what you want extracted and where the PDFs are, and it will ask for whatever is missing.

## How to run it

In a Claude Code session opened on the lockdown workspace (see "Start here"), ask in plain language:

```
Extract the pathway for acetaminophen-induced hepatotoxicity from the PDFs in papers,
using pathwise_ontology.json.
```

Articles are processed one at a time in a single conversation. A run can't be split across sessions, because later articles need to see the terms earlier ones introduced.

## What you get back

Everything is written to an `output/` folder:

| File | What it is |
|---|---|
| `<aop_id>.json` | One per article, named like `cyp2e1@hepatocyte_necrosis_smith_2019.json` (initiating event, `@`, adverse outcome, then the article's name). Its key events and relationships, each with the quotes that support it and the citations attached to each quote, plus the list of sources it cites. |
| `run_log.md` | First, whether the lockdown was on for this run. Then one line per article: processed, excluded as off-topic, borderline, or failed to read, with the reason and pages read. Check here first if an article seems to be missing. |
| `new_terms.json` | Every new ontology term minted this run, for your review. Nothing is added to your ontology automatically. If you do the end-of-run reviews, it also records each decision (merged, kept separate, or same or different relationship), the reason, who decided, and when. |
| `merged_tally.json` | The main result. Every key event and relationship merged across articles, with `article_count` (how many articles support it) and `distinct_sources_cited` (how many different papers those articles cite for it). It also holds the flag lists described below. In Full mode it carries the extra detail too. |

The flag lists inside `merged_tally.json` are places to look at, not verdicts:

- `single_source_flags`: supported by only one article, in an area other articles also cover.
- `single_citation_flags`: supported by several articles that all cite the same one paper.
- `relationship_disagreement_flags`: two articles connect the same two key events but don't use exactly the same pair of tags (for example "activates" and "inhibits"). This can be a real disagreement or just different wording. You can sort these out in the end-of-run review.
- `ambiguous_source_matches`: cited papers the skill had to match by author and year, or likely the same paper with different years, so you can confirm them.

## How relationships are written

Each relationship has exactly two tags, separated by a comma. The first says what happens to the first event, and the second says what that does to the second event, for example `["oxidizes_to", "formed_from"]`. The tags follow the article's own wording as closely as possible. If a relationship reads the same from both sides, or the article only describes one side, the word is repeated, for example `["binds_to", "binds_to"]`.

Once an earlier article has set the tags for a relationship, later articles describing the same thing reuse them. Two articles only count toward the same relationship when both tags match exactly, in the same order.

The two tags can point in different directions. `["activates", "inhibits"]` means the first event is activated, and that inhibits the second. If one article says A activates B and another says A inhibits B, that leads to a different outcome, so it is a different pathway. The skill keeps them as separate relationships and flags them.

## While it runs and when it finishes

While it runs, Claude tells you right away if an article fails to open, is excluded as off-topic, is borderline on-topic, or yields no key events, and gives a reason each time.

When it finishes, it prints a summary: key event and relationship totals, which articles were flagged and why, and the possible duplicate term pairs by name. It then offers two optional reviews. The first steps through the possible duplicates one at a time. The second steps through relationship disagreements, where you mark each one as the same meaning (so the articles count together) or different (kept apart). Each decision is saved with the date. It doesn't interpret the biology. That part is up to you.

## Scope

**Always included:** pathway extraction, per-article citations tied to each key event and relationship, two quality notes on each (whether the article reports a competition or specificity test for that step, and whether it reports an attempt to disprove it, such as a knockout, blocking, or rescue experiment; each is true, false, or unknown, and unknown is the usual answer), term matching against your ontology, and a tally across articles (both an article count and a count of distinct cited papers).

**Full mode only:** species-specific or conditional branching (including minor pathways that only matter under specific circumstances), confounders (sex, genetic polymorphisms, background rates, species physiology), developmental windows, and initiating-event class. These are recorded only when an article's own text states them, and each one is tagged so a future visualizer can show or hide them separately from the core chain.

**Never included:** dose or exposure study details, narrative summaries, and judgments about whether a disagreement between articles is real biology or an extraction mistake. Disagreements get flagged, not resolved. If you want any of this, ask for it directly.

## Known limitations

- The reviewer name saved with each review decision is just a name typed in at the start of the review. It isn't verified.
- Review decisions are saved with the date only, not the time. The lockdown blocks commands, so there's no clock to read a time from.
- Claude Code's sandbox, which could let commands run with no internet, doesn't work on Windows yet. So the lockdown blocks commands completely instead.
- The lockdown blocks the claude.ai Docs connector by its ID on the account it was tested with. If your account shows that connector under a different name, it may not be blocked. All other claude.ai connectors are switched off by a general setting.
- Choosing Simplified mode means any extra detail (species, confounders, special circumstances) can only be added later by running the batch again.
- None of the recent changes have been run on a real batch of PDFs yet.

## Future directions

- **One pathway per topic, not per review.** Right now each review article produces its own pathway file, and `merged_tally.json` counts what they share. The goal is a single combined pathway built from all the reviews on a topic. That needs a team decision first on how to handle conflicting information, and on what to keep when one review goes further than another.
- **Finding the reviews automatically.** The long-term aim is to give the agent a pathway idea and have it gather the freely available review articles itself, then build the combined pathway with weights or scores.
- **Scoring review article quality.** Rate each review with checklists such as AMSTAR, PRISMA, or SANRA, depending on the article type. The result could be an overall score or a short written assessment.
- **Improving the evidence behind each step.** The quality fields mostly come back "unknown," because reviews rarely describe the tests behind a claim. Contributors with access to the cited studies could fill these in later, and the criteria will be refined over time.
- **A new pathway naming convention.** Pathways are named after the initiating event and the adverse outcome. This is expected to change so the name no longer uses the adverse outcome.
- **Visualizing the extra detail in RiskLytx.** Show the Full-mode layers (species differences, confounders, developmental windows) so they can be turned on and off. Also show the evidence behind each key event and relationship: the quality fields, the supporting quotes, and how many articles and cited papers back it.

## Full details

See [SKILL.md](SKILL.md) and [references/procedure.md](references/procedure.md) for the full procedure, including the exact JSON layout, the term-matching rules, and the checks run on each article.
