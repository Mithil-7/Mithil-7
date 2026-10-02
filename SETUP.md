# Setup

This package is designed for the profile repository:

`https://github.com/Mithil-7/Mithil-7`

## 1. Copy the files

Copy the contents of this folder into the **root** of that repository:

```text
README.md
SETUP.md
assets/
  cube-hero.svg
  work-tree.svg
  contributions-3d.svg
  project-traffic.svg
  project-crafthaat.svg
  project-openenv.svg
  project-deep-learning.svg
  project-efsat.svg
  project-gsoc.svg
data/
  contributions.json
scripts/
  build_profile_art.py
  update_contributions.py
.github/
  workflows/
    update-contributions.yml
interactive-lab.html
```

The `README.md` must be in the root of `Mithil-7/Mithil-7`, otherwise GitHub will not display it as your profile README.

## 2. Publish the playable cube

GitHub profile READMEs can display SVG animation, but GitHub does not execute JavaScript inside a README. The playable cube and hoverable work tree therefore live in `interactive-lab.html`.

To make the link live at `https://mithil-7.github.io/interactive-lab.html`:

1. Copy `interactive-lab.html` into the root of your `Mithil-7/Mithil-7.github.io` repository.
2. Commit and push it.
3. Keep the link near the top of `README.md`.

The page is self-contained and has no dependencies. It supports drag-to-rotate viewing, U/D/L/R/F/B face turns, prime turns, scrambling, undo, reset, and reversing the recorded session moves. It also contains the hoverable branching work tree and complete skill index.

## 3. Enable daily graph updates

1. Open the repository on GitHub.
2. Go to **Settings → Actions → General**.
3. Under **Workflow permissions**, select **Read and write permissions**.
4. Save the setting.
5. Open **Actions → Update contribution graph**.
6. Choose **Run workflow** once to test it.

The workflow then runs once per day. It fetches the public contribution calendar through GitHub's GraphQL API, rebuilds `assets/contributions-3d.svg`, updates `data/contributions.json`, and commits only when the graph changes.

The workflow uses GitHub's temporary `GITHUB_TOKEN`; no personal access token is required.

## 4. Rebuild the decorative artwork locally

From the profile repository root:

```bash
python scripts/build_profile_art.py
```

This regenerates the Rubik's cube hero and project cards. It uses only Python's standard library.

## 5. Update the contribution graph locally

With a GitHub token available as an environment variable:

```bash
# PowerShell
$env:GITHUB_TOKEN = "your-token"
python scripts/update_contributions.py --login Mithil-7

# macOS / Linux
GITHUB_TOKEN=your-token python scripts/update_contributions.py --login Mithil-7
```

The token needs permission to read the public profile data. Never commit the token or put it in `README.md`.

## Animation notes

- `cube-hero.svg` is the README-safe preview. The actual playable cube is in `interactive-lab.html`, where the cube state and layer turns are implemented in JavaScript.
- `work-tree.svg` is the README-safe static branch graph. The interactive page adds hover highlighting across each branch.
- The project cards use small SVG motion accents.
- `contributions-3d.svg` animates each contribution column into the 3D field when it loads.
- There are no gradients, JavaScript, external image services, or streak-card dependencies.
- GitHub and browser reduced-motion settings may suppress SVG animation; the static artwork remains visible.
