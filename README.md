# PathwayWise
Home of PathWise: the open source Adverse Outcome Pathway project.

## Using the pathway-extraction skill

To extract a pathway from PDF articles with Claude Code, use the [`pathway-extraction-workspace`](pathway-extraction-workspace) folder. Download this repository, open that folder in Claude Code, put your PDFs in its `papers` folder, and ask for the pathway. The folder comes with lockdown settings that keep Claude to your PDFs only, with no internet, past chats or other folders. See [the skill's README](skills/pathway-extraction/README.md#start-here-run-it-in-the-lockdown-workspace) for step-by-step instructions.

For maintainers: `skills/pathway-extraction` is where the skill is developed. After changing it, copy it into `pathway-extraction-workspace/.claude/skills/pathway-extraction` so the workspace runs the same version.

# Background

One challenge with the current AOP-Wiki is that it runs on a first-come-first-owned basis. That first author of an entity in the wiki becomes the owner, and must approve any and all changes. So this doesn't quite embrace the open source workflow that works best in the software development world. We want to change this to make it easier for anyone to work with AOPs.

Another challenge is that the AOP-Wiki in the past did not handle ontologies at all. So, new concepts were not aligned with an ontology, which made it difficult to know that one biological entity was the same as another. As a result, people are now going back in and trying to correct the lack of ontologies.



We will have versions of the notebook for others to use as a guide on Github.

We will also offer training on how to use it.

We will host hackathons.

We will talk about how we envision the project -- so I'll need to do a webinar.

Eventually, we will need to write code to hook all of the AOPs together and put them into a cloud-hosted Neo4J graph database. Then we will start hooking those up with commercially available assays.

We will also need a web-based GUI that people can run to overlay their data onto the AOPs, or onto the AOP network. 

Ultimately I will want to be able to come up with a batter of in vitro assays that covers a large swath of space.

Commercial vendors can pay to advertise in the system to have their assays listed at the top of our results.

example change