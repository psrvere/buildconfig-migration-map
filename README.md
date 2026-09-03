# BuildConfig to Shipwright migration map

One page for the product manager and the team: what the crane migration
plugin does today, which features each phase delivered, what is open, and the
gaps the Jira epics hide. Published with GitHub Pages from this repository.

- Site: https://psrvere.github.io/buildconfig-migration-map/
- Plugin: https://github.com/migtools/crane-plugin-buildconfig-to-shipwright
- Epics: BUILD-1334, BUILD-1848, BUILD-1655, BUILD-2254, BUILD-2394 on Red Hat Jira

## Updating the page

The page is generated. Edit the data, rebuild, commit the result.

```
python3 build.py      # writes index.html from data/*.tsv
```

| File | What it holds |
|---|---|
| `data/stories.tsv` | one row per story: key, phase, feature, type, Jira status and resolution, title, PR numbers, note, story points, and a short title used in the pending column while the story is open |
| `data/features.tsv` | the fifteen features: id, short name, name, layer, what the user gets as pipe-separated bullets, an optional status override, an optional note under the status |
| `data/layers.tsv` | the seven layers the features sit in |
| `build.py` | the prose sections, the two SVG figures, the sources list, and the story-table filters |
| `assets/base.css` | the shared dark stylesheet from the create-html skill, inlined at build time |
| `index.html` | the generated page, committed so Pages can serve it |

`build.py` needs Python 3 and nothing else. Change the `SNAPSHOT` date in it
when you refresh the Jira statuses.

## Conventions

- Feature ids F1 to F15 are stable. Add a feature at the end, never renumber.
- A story's state comes from Jira: `Closed` with resolution `Done` is done,
  `Closed` with any other resolution is closed without work, `Review`,
  `In Progress` and `Waiting` are active, anything else is open.
- A feature's status is derived from its stories. Shipped: every story
  done, nothing open. In progress: something done or active and something
  still open, or an open PR (set `status_override` for PR-only work). Todo:
  stories filed, none done or started. Won't do: every story closed without
  work. Refinement: no story filed yet.
- Prose follows the create-html writing rules: no em dashes, one idea per
  sentence, every factual claim cites a source in the list at the end.
