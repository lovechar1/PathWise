# Pathway extraction workspace

Run the pathway-extraction skill from this folder, and only from this folder. Its settings (in `.claude/settings.json`) lock Claude down so the pathway comes from your PDFs and nothing else: no commands, no past chats or memory, no folders outside this one, and no internet except a final check of gene and protein names at HGNC and UniProt.

1. Open **this folder** in Claude Code (not a folder around it).
2. Put your PDFs in `papers`.
3. Start a new chat and ask, for example: "Extract the pathway for perfluorooctanoic acid–induced liver toxicity from the PDFs in papers."
4. Answer its questions. When it asks for the ontology file, give `pathwise_ontology_CAL.json` (the current cleaned ontology, in this folder). The gene and protein name check runs on its own at the end. The run is finished when it says complete.

If a run stops partway, open a new chat here and type "finish the PathWise run".

Results go into `pathwise_output/`. Don't edit or delete `.claude/settings.json` or `pathwise_output_canary.txt`, or the skill won't run. On Windows, Git for Windows (from git-scm.com) needs to be installed.

Full instructions: [the skill's README](.claude/skills/pathway-extraction/README.md).
