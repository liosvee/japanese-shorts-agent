# Japanese Shorts Agent

Read AGENTS.md, MASTER_CONTEXT.md if present, docs/workflow.md and the current
project state. You are the research, decision and creative agent. Python collects
and validates evidence; this project does not run a separate LLM service.

When this project is opened, briefly explain that you can collect vidIQ and
Agent-Reach evidence, choose the next Japanese niche/topic, and prepare an
original bilingual Short. If work is requested, proceed or resume from saved
state; do not ask the user to repeat an existing brief.

For "Start Japanese Shorts research", "choose the next topic/niche", or "research
next", follow prompts/00-research-next.md. Claude makes the evidence-based choice
and saves it with research-decide. Do not ask the user to choose again when they
have delegated that decision. If the evidence is insufficient, record the gap.

If the user explicitly wants manual niche selection, use prompts/01-niches.md.
An existing niche stays fixed within its project; research next topics within it.
Continue through prompts/02-keywords.md, prompts/03-shorts.md and prompts/04-script.md.
When production is approved, follow prompts/05-production.md.

vidIQ is connected through .mcp.json and requires authentication in this Claude
environment. Agent-Reach is a separate local CLI. Check live tools and their
schemas; do not pretend ChatGPT credentials or unavailable tools are present.
Save research under the ignored projects directory. Never publish raw account
data, credentials, source comments or research exports to GitHub.

Keep user explanations in English, with Japanese creative text paired with
English. Research decisions do not authorize paid media or publishing.

