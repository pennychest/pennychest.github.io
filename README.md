# pennychest.github.io

Builds and publishes the [PennyChest docs](https://pennychest.github.io). The content lives
elsewhere:

- [pennychest](https://github.com/pennychest/pennychest): `docs/` and `mkdocs.yml`
- [pennychest-plugins](https://github.com/pennychest/pennychest-plugins): each plugin's
  `README.md`, published under "Plugin reference"

`assemble.py` copies the plugin READMEs into the core docs and adds them to the nav, then the
[Docs workflow](.github/workflows/docs.yml) builds the site with MkDocs and deploys it to
GitHub Pages.

The site is rebuilt when either repository sends a `docs` repository dispatch (their docs
workflows do this when docs change, using the `DOCS_TOKEN` secret), on a push here, weekly, or
from the Actions tab.
