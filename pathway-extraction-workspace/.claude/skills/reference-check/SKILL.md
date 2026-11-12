---
name: reference-check
version: 1.4.0
description: Final step of a PathWise pathway-extraction run. Checks the gene and protein names in a finished run's key events against HGNC and UniProt, finds the official symbol when a paper used an informal name (Claude suggests, the database confirms), renames the gene part to that symbol, records HGNC and UniProt ids, and marks the run complete. Use only when the pathway-extraction skill hands over (run status "awaiting reference check") or when the user asks to finish a PathWise run. Never use it for anything else, and never during extraction.
compatibility: Runs inside the PathWise lockdown workspace. Needs internet access to rest.genenames.org and rest.uniprot.org (the lockdown allows only name lookups there, only from the main conversation).
---

# PathWise reference check

The pathway is already final. This check changes only the gene or protein part of key event names, nothing else, and never adds, removes or reconnects anything. Its job is to make every gene part the official HGNC symbol, including when the papers used an informal name. It doesn't use the databases to judge the biology, and it never changes a gene part's `form` (gene, protein or unspecified), which comes from the papers.

**Make a best guess; don't hand the user a review list.** Settle every gene part yourself when the papers' wording and the database records point to an answer, even if it takes some thought. Ask the user only about the few that are truly unclear: after weighing the label, definition, synonyms and quote, two or more official symbols still fit equally well. Everything you decide is recorded with its reason in `reference_check.json`, so it can be checked later if needed.

## 1. Find the run

Use the output folder the extraction skill named. Otherwise look for `pathwise_output*/run_log.md` files whose status line is `run status: awaiting reference check`. If a run log instead says `in progress`, `merging` or `reviewing`, the run itself isn't finished: start the `pathway-extraction` skill to resume it (it comes back here at the end). If there is no unfinished run, tell the user so, and stop. If there are several, ask which one.

## 2. List what to look up

Read the run's `merged_tally.json`. For each key event, read its `biological_entity_id` and `gene_parts` (each entry has a `symbol` and a `form`).
- `gene_parts` is `[]`: no lookup. Record it as `"no_gene"`. This covers events like `liver_weight` and written-out families or complexes.
- Otherwise look up each symbol once, even if several key events share it (`ppara` in both `ppara` and `ppara_activation`).
- An entry that is a plain string instead of `{ "symbol", "form" }` comes from a run made before `form` existed: use the string as the symbol and treat the form as `"unspecified"`.

If a run has no `gene_parts` fields at all (made before this field existed), tell the user that the check can't tell which part of each name is a gene, and stop without changing the status.

For each symbol, also gather **what the papers meant**, for step 3e and 3f: the term's `label`, `definition` and `synonyms` (from `new_terms.json`, or from the ontology file for an ontology term), and one evidence quote from an article file that uses it.

## 3. Find the official symbol for each gene part

All lookups use WebFetch with the prompt "Return the response text exactly as received, with no summary or commentary." Use only these addresses; the lockdown refuses anything else. Write symbols in upper case in the address, and encode a space as `%20` and a double quote as `%22`.

**a. Database version, once:** `https://rest.genenames.org/info`. Record `lastModified`.

**b. Exact symbol:** `https://rest.genenames.org/fetch/symbol/<SYMBOL>`. `numFound` is 1: the symbol is official (**confirmed**, `found_by: "exact"`). Record `hgnc_id`, the official `symbol` (its capitalization is the label), `name`, `locus_type` and `uniprot_ids`, and go to 3g. Otherwise continue.

**c. Previous and alias symbols:** search `https://rest.genenames.org/search/prev_symbol/<X>` and then `https://rest.genenames.org/search/alias_symbol/<X>`, for the gene part and for each synonym that looks like a symbol (the papers' own spellings such as `PGC-1alpha` or `NR1C1`, with a Greek letter written as its English word). Every symbol these return is a candidate. (Tested: `PGC-1alpha` is an HGNC alias of `PPARGC1A`.)

**d. Name search**, when 3c gave no candidates or more than one:
- HGNC by name: `https://rest.genenames.org/search/name/%22<written-out name>%22`, using the written-out name from the label or definition (`peroxisome proliferator activated receptor alpha`).
- UniProt by protein name, for the written-out name and for each synonym: `https://rest.uniprot.org/uniprotkb/search?query=protein_name:%22<name>%22+AND+organism_id:9606+AND+reviewed:true&fields=accession,id,gene_primary,protein_name&format=tsv`.

These searches are loose (a search for "PPAR-alpha" also returns CHD9 and HELZ2, whose long protein names happen to mention it), so every symbol they return is only a candidate.

**e. Suggest.** Add your own suggestion: the official HGNC symbol you believe the papers meant, from the label, synonyms, definition and quote (`pparalpha` or `ppar_alpha` → `PPARA`; `pgc1alpha` → `PPARGC1A`; `hif_1alpha` → `HIF1A`). Using your own knowledge is allowed here, unlike during extraction, because nothing is accepted until the database confirms it in 3f. If you can't tell which gene the papers meant (for example the papers' wording fits several family members), suggest each of them.

**f. Confirm.** Fetch each distinct candidate (at most five) with `https://rest.genenames.org/fetch/symbol/<CANDIDATE>`. A candidate is **confirmed** only when the HGNC record exists and its official `name`, a `prev_name`, a `prev_symbol` or an `alias_symbol` matches what the papers meant. Example: `PPARA` is confirmed for `pparalpha` because its official name is "peroxisome proliferator activated receptor alpha", which is what the papers' "PPARα" stands for; `PPARAL` is not, because it is a different gene. Judge by the names only. For each candidate, write a one-line `match_reason` saying which name matched or why none did.
- Exactly one confirmed candidate: **rename** to it. Record `found_by` (`"previous_symbol"`, `"alias_symbol"`, `"name_search"` or `"suggested"`, whichever first produced it) and the record's ids as in 3b.
- Several confirmed: think it through and **pick the best fit**, then rename to it. Use the papers' wording: the full name or Greek letter they spell out, the family member their definition or quote describes, the tissue or function they mention. Example: papers writing "PPAR" for the receptor that fibrates activate in liver mean `PPARA`, not `PPARG` or `PPARD`. Record the others in `chosen_over`, and say in `match_reason` why the chosen one fits better. Only when two or more still fit equally well (the papers truly don't say which family member) is it **unclear**.
- None confirmed: **not found**. Keep the name as it is and record the candidates you tried. This is usually something that isn't a single human gene (a family, a complex, a non-human gene with no human equivalent), so don't ask the user about it.

**g. UniProt ids, in batches of up to 20 symbols** (every confirmed or renamed official symbol):
`https://rest.uniprot.org/uniprotkb/search?query=(gene_exact:<A>+OR+gene_exact:<B>)+AND+organism_id:9606+AND+reviewed:true&fields=accession,id,gene_primary,gene_synonym,protein_name&format=tsv`
For each, find the row whose `Gene Names (primary)` matches it. Record `Entry` as the UniProt accession (for example `P11388`) and `Entry Name` (for example `TOP2A_HUMAN`). The accession goes into the data, never into the name. A symbol with no row (for example a non-coding RNA gene) gets `"uniprot_accession": null`.

Human entries (`organism_id:9606`) are used because PathWise names genes by their HGNC (human) symbols, whatever species the evidence came from. The species of each key event stays as the articles reported it.

**Form check.** If a gene part's form is `"protein"` but its HGNC `locus_type` isn't `gene with protein product` (for example a microRNA or other non-coding RNA gene), add it to the list for the user in step 6, as "the paper describes a protein, but HGNC lists this gene as non-coding". Don't change anything.

## 4. Decide each gene part

- **confirmed**: already the official symbol. Nothing changes.
- **rename**: one confirmed official symbol differs from the one used. Replace only the gene part inside each key event that uses it (`ppar_alpha_activation` → `ppara_activation`; HGNC lists `TOP2` as the previous symbol of `TOP2A`, so `inhibition_of_top2` → `inhibition_of_top2a`; the rest of the name stays). The old symbol becomes a synonym. Renames, including best-fit picks, are applied without asking.
- **not found**: nothing changes, and the user isn't asked.
- **unclear** (two or more candidates fit equally well): nothing changes yet; ask the user in step 6.

## 5. Save the results before changing anything

Write `<output folder>/reference_check.json`:

```json
{
  "checked_at": "<date and time>",
  "hgnc_last_modified": "<from /info>",
  "uniprot_release": "not available through the allowed lookups; see checked_at",
  "gene_parts": [
    { "gene_part": "top2a", "forms": ["protein"], "result": "confirmed", "found_by": "exact", "official_symbol": "TOP2A", "official_name": "DNA topoisomerase II alpha", "hgnc_id": "HGNC:11989", "locus_type": "gene with protein product", "uniprot_accession": "P11388", "uniprot_entry_name": "TOP2A_HUMAN", "key_events": ["top2a"] },
    { "gene_part": "pparalpha", "forms": ["protein"], "result": "rename", "found_by": "suggested", "official_symbol": "PPARA", "official_name": "peroxisome proliferator activated receptor alpha", "hgnc_id": "HGNC:9232", "locus_type": "gene with protein product", "uniprot_accession": "Q07869", "uniprot_entry_name": "PPARA_HUMAN", "match_reason": "HGNC official name matches the papers' PPARα; PPARAL is a different gene", "key_events": ["pparalpha_activation"], "renamed_to": ["ppara_activation"] },
    { "gene_part": "ppar", "forms": ["protein"], "result": "rename", "found_by": "suggested", "official_symbol": "PPARA", "chosen_over": ["PPARG", "PPARD"], "match_reason": "papers describe the fibrate-activated receptor in liver, which is PPARα", "official_name": "peroxisome proliferator activated receptor alpha", "hgnc_id": "HGNC:9232", "locus_type": "gene with protein product", "uniprot_accession": "Q07869", "uniprot_entry_name": "PPARA_HUMAN", "key_events": ["ppar_activation"], "renamed_to": ["ppara_activation"] },
    { "gene_part": "<y>", "forms": ["gene"], "result": "not found", "candidates": [ { "symbol": "<SYMBOL>", "match_reason": "different gene" } ], "key_events": ["..."] },
    { "gene_part": "<x>", "forms": ["unspecified"], "result": "unclear", "candidates": [ { "symbol": "<SYMBOL1>", "match_reason": "..." }, { "symbol": "<SYMBOL2>", "match_reason": "..." } ], "key_events": ["..."], "decision": null }
  ],
  "form_warnings": [],
  "no_gene": ["liver_weight"]
}
```

`forms` lists the forms the merged tally gives that symbol across its key events. If the chat is interrupted after this file exists, start again from step 6 using it, and don't repeat the lookups.

## 6. Apply renames and ask about the rest

1. **Renames.** Follow the relabeling rules in the pathway-extraction skill ("What relabeling may and may not do" in its `references/procedure.md`): a targeted replacement of the term text in each article's working file, never the `original/` copies, never quotes or references. Update the `symbol` in `gene_parts` to the new symbol and leave its `form` alone. In `new_terms.json` set the new `label` (official capitalization) and add the old symbol to `synonyms`.
   - If a rename makes a key event identical to another key event that already exists (for example `ppar_alpha` becoming `ppara` when `ppara` is already there), they are the same event, so merge them into one. First run the loop check from Step 8b of the procedure (a relationship connecting the two, directly or through a chain). If there is one, don't merge: ask the user, as in Step 8b, and record the answer in `decision`. A merge keeps each article's own form; the tally shows `"mixed"` if they differ. Record merges in the entry as `"merged_with": ["ppara"]`.
2. **Ask only about the truly unclear ones.** If there are any, ask with the AskUserQuestion tool (a pop-up with buttons, never a question typed in chat): one question per gene part, naming its key events, with one button per candidate symbol (its official name in the button's description), plus "Keep as written" and "Decide later". Up to four questions per pop-up; show another pop-up for the rest. The loop question for a merge (step 6.1) is a pop-up too: "Merge anyway" / "Keep separate". Only if AskUserQuestion isn't available, ask in chat with numbered choices. Record each answer in the entry's `decision` and apply picks as renames. If nothing is unclear, ask nothing. Don't list renames, best-fit picks, not-found names or form warnings for review; they're summarized in step 7 and recorded in `reference_check.json`.
3. When anything changed, regenerate `merged_tally.json` only, by re-running the merge in Step 7 of the procedure.

## 7. Finish

Add each key event's ids to `merged_tally.json`: a `gene_refs` list on every key event with gene parts, one entry per gene part with its form, `[{ "symbol": "top2a", "form": "protein", "hgnc_id": "HGNC:11989", "uniprot_accession": "P11388" }]`. Then change the run log's status line to `run status: complete` and add a line `reference check: <checked_at>, HGNC <hgnc_last_modified>`.

Tell the user in two or three plain lines: how many gene and protein names were checked, how many were already official, how many were renamed (and how many of those were best-fit picks or merges), how many weren't found and were kept as written, any form warnings in a few words, and that the run is complete. Point to `reference_check.json` for the details. Don't list each rename.

If a lookup fails because there's no internet, stop. Leave the status at `awaiting reference check` and tell the user, as an instruction: "This run isn't finished. The gene and protein name check couldn't reach HGNC or UniProt. Once you're online, open a new chat in this folder and type: finish the PathWise run."
