# Profile README setup

This folder contains the profile README and the original SVG artwork it references.

## Install

Copy these files into the root of the `Mithil-7/Mithil-7` profile repository:

```text
README.md
assets/
scripts/build_art.py
```

Python's standard library is enough to rebuild the artwork:

```bash
python scripts/build_art.py
```

## Contribution data

`assets/contributions.svg` and `assets/signal-field.svg` are a dated public snapshot read on **2026-09-28**. The snapshot showed **538 contributions in the last year**. GitHub does not provide the complete contribution calendar through the unauthenticated REST repositories endpoint, so the artwork intentionally avoids pretending to be a live API feed.

To refresh it, open `https://github.com/users/Mithil-7/contributions`, update the data in `contribution_art()` in `scripts/build_art.py`, and run the build script again. For a continuously live calendar, replace the two local images with your preferred GitHub contribution service after checking its availability and rate limits.

## Notes

- The project cards and hero are generated locally and do not copy the attached reference's assets or layout.
- Forks are intentionally excluded from the featured-project section.
- Research targets and prototypes are labelled as such; no unpublished result is presented as a verified publication or benchmark.
- The `skillicons.dev` strip is remote. Remove it if you want a fully self-contained profile README.
