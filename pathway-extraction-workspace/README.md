# Pathway extraction workspace

Run the pathway-extraction skill from this folder, and only from this folder. Its settings (in `.claude/settings.json`) lock Claude down so the pathway comes from your PDFs and nothing else: no internet, no commands, no past chats or memory, and no folders outside this one.

1. Open **this folder** in Claude Code (not the PathWise folder around it).
2. Put your PDFs in `papers`. Put an ontology file here too, if you have one.
3. Start a new chat and ask, for example: "Extract the pathway for acetaminophen-induced hepatotoxicity from the PDFs in papers."

Results go into `pathwise_output/`. Don't edit or delete `.claude/settings.json` or `pathwise_output_canary.txt`, or the skill won't run. On Windows, Git for Windows (from git-scm.com) needs to be installed.

Full instructions: [the skill's README](.claude/skills/pathway-extraction/README.md).
