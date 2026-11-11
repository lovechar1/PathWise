---
name: reference-check
version: 1.4.0
description: Final step of a PathWise pathway-extraction run. Checks the gene and protein names in a finished run's key events against HGNC and UniProt, renames a gene part to its official symbol when there is one clear answer, records HGNC and UniProt ids, and marks the run complete. Use only when the pathway-extraction skill hands over (run status "awaiting reference check") or when the user asks to finish a PathWise run. Never use it for anything else, and never during extraction.
compatibility: Runs inside the PathWise lockdown workspace. Needs internet access to rest.genenames.org and rest.uniprot.org (the lockdown allows only name lookups there, only from the main conversation).
---

# PathWise reference check

The pathway is already final. This check changes only the gene or protein part of key event names, nothing else, and never adds, removes or reconnects anything. It doesn't use the databases to judge the biology.

## 1. Find the run

Use the output folder the extraction skill named. Otherwise look for `pathwise_output*/run_log.md` files whose status line is `run status: awaiting reference check`. If a run log instead says `in progress`, `merging` or `reviewing`, the run itself isn't finished: start the `pathway-extraction` skill to resume it (it comes back here at the end). If there is no unfinished run, tell the user so, and stop. If there are several, ask which one.

## 2. List what to look up

Read the run's `merged_tally.json`. For each key event, read its `biological_entity_id` and `gene_parts`.
- `gene_parts` is `[]`: no lookup. Record it as `"no_gene"`. This covers events like `liver_weight` and written-out families or complexes.
- Otherwise look up each gene part once, even if several key events share it (`ppara` in both `ppara` and `ppara_activation`).

If a run has no `gene_parts` fields at all (made before this field existed), tell the user that the check can't tell which part of each name is a gene, and stop without changing the status.

## 3. Look up each gene part

All lookups use WebFetch with the prompt "Return the response text exactly as received, with no summary or commentary." Use only these addresses; the lockdown refuses anything else. Write symbols in upper case in the address.

1. **Database version, once:** `https://rest.genenames.org/info`. Record `lastModified`.
2. **HGNC, per gene part:** `https://rest.genenames.org/fetch/symbol/<SYMBOL>`.
   - `numFound` is 1: the symbol is official. Record `hgnc_id`, the official `symbol` (its capitalization is the label) and `uniprot_ids`.
   - `numFound` is 0: try `https://rest.genenames.org/search/prev_symbol/<SYMBOL>`, then `https://rest.genenames.org/search/alias_symbol/<SYMBOL>`. Exactly one result: that result's symbol is the official one; fetch it as above. Several results: **unclear**. None: go to UniProt.
3. **UniProt, in batches of up to 20 symbols** (all the HGNC-confirmed ones, plus any HGNC didn't find):
   `https://rest.uniprot.org/uniprotkb/search?query=(gene_exact:<A>+OR+gene_exact:<B>)+AND+organism_id:9606+AND+reviewed:true&fields=accession,id,gene_primary,gene_synonym,protein_name&format=tsv`
   - For a confirmed symbol: find the row whose `Gene Names (primary)` matches it. Record `Entry` as the UniProt accession (for example `P11388`) and `Entry Name` (for example `TOP2A_HUMAN`). The accession goes into the data, never into the name.
   - For a symbol HGNC didn't find: if exactly one row lists it as a synonym, that row's primary gene name is the official one; fetch it from HGNC as in 2. Otherwise it's **not found**.

Human entries (`organism_id:9606`) are used because PathWise names genes by their HGNC (human) symbols, whatever species the evidence came from. The species of each key event stays as the articles reported it.

## 4. Decide each gene part

- **confirmed**: already the official symbol. Nothing changes.
- **rename**: one clear official symbol differs from the one used. Replace only the gene part inside each key event that uses it (HGNC lists `TOP2` as the previous symbol of `TOP2A`, so `inhibition_of_top2` → `inhibition_of_top2a`; the rest of the name stays). The old symbol becomes a synonym.
- **unclear** (several possible matches) or **not found**: nothing changes yet; ask the user in step 6.

## 5. Save the results before changing anything

Write `<output folder>/reference_check.json`:

```json
{
  "checked_at": "<date and time>",
  "hgnc_last_modified": "<from /info>",
  "uniprot_release": "not available through the allowed lookups; see checked_at",
  "gene_parts": [
    { "gene_part": "top2a", "result": "confirmed", "official_symbol": "TOP2A", "hgnc_id": "HGNC:11989", "uniprot_accession": "P11388", "uniprot_entry_name": "TOP2A_HUMAN", "key_events": ["top2a"] },
    { "gene_part": "<old>", "result": "rename", "official_symbol": "<NEW>", "hgnc_id": "...", "uniprot_accession": "...", "uniprot_entry_name": "...", "key_events": ["..."], "renamed_to": ["..."] },
    { "gene_part": "<x>", "result": "unclear", "candidates": ["<SYMBOL1>", "<SYMBOL2>"], "key_events": ["..."], "decision": null }
  ],
  "no_gene": ["liver_weight"]
}
```

If the chat is interrupted after this file exists, start again from step 6 using it, and don't repeat the lookups.

## 6. Apply renames and ask about the rest

1. **Renames.** Follow the relabeling rules in the pathway-extraction skill ("What relabeling may and may not do" in its `references/procedure.md`): a targeted replacement of the term text in each article's working file, never the `original/` copies, never quotes or references. Update `gene_parts` to the new symbol, and in `new_terms.json` set the new `label` (official capitalization) and add the old symbol to `synonyms`.
   - If a rename would make a key event identical to another key event that already exists (for example `ppar_alpha` becoming `ppara` when `ppara` is already there), don't apply it on your own. Ask: "`ppar_alpha` and `ppara` are the same gene (HGNC:<id>). Merge them into `ppara`?" Before merging, run the loop check from Step 6b of the procedure. If the user says no, leave both and record `"decision": "kept separate"`.
2. **Unclear and not found.** Show them in one short list, each with its key events and candidates, and ask the user to pick a symbol, keep the name as it is, or leave it for later. Record each answer in the entry's `decision`. Apply picks as renames.
3. When anything changed, regenerate `merged_tally.json` only, by re-running the merge in Step 7 of the procedure.

## 7. Finish

Add each key event's ids to `merged_tally.json`: a `gene_refs` list on every key event with gene parts, `[{ "symbol": "top2a", "hgnc_id": "HGNC:11989", "uniprot_accession": "P11388" }]`. Then change the run log's status line to `run status: complete` and add a line `reference check: <checked_at>, HGNC <hgnc_last_modified>`.

Tell the user in two or three plain lines: how many gene and protein names were checked, how many were confirmed, renamed or left for them, and that the run is complete.

If a lookup fails because there's no internet, stop. Leave the status at `awaiting reference check` and tell the user, as an instruction: "This run isn't finished. The gene and protein name check couldn't reach HGNC or UniProt. Once you're online, open a new chat in this folder and type: finish the PathWise run."
