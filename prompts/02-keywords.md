# Keywords after user selection

1. Record the user's exact niche using `python -m jp_shorts select PROJECT ID`.
2. Build 15–30 natural Japanese seed queries and English translations. Include
   realistic kana/kanji alternatives where appropriate. Do not mechanically
   translate English keyword lists and assume Japanese demand.
3. If a real keyword analytics tool is connected in Claude Code, inspect its
   current schema and market coverage, then use it. Otherwise request a provider
   export. This repository has a CSV importer, not a vidIQ or Google Ads adapter.
   Do not invent a vidIQ endpoint or imply a ChatGPT connection transfers here.
4. Normalise the supplied data to templates/keywords.csv. Keep source URLs,
   provider, dates, market and measurement period. If a provider does not support
   Japan, do not relabel worldwide data JP. Search volumes are estimates unless
   the provider establishes otherwise. Record missing values as empty.
5. Run `python -m jp_shorts keywords PROJECT CSV`. Show grouped rankings with
   English meanings. A relative-interest index is not monthly search volume.
6. Prefer the highest-volume relevant Japanese YouTube/JP keyword in one
   comparable group, after checking suitability for a Short. Explain if a lower
   volume keyword is chosen for relevance. Select it with choose-keyword and
   its zero-based group index. Do not claim "most searched on YouTube" beyond
   the measured provider/sample. If estimates are missing, explicitly label the
   choice qualitative. Obtain user acceptance of qualitative research if that
   substitutes for the requested traffic analysis.
7. Continue to prompts/03-shorts.md without another selection gate.
