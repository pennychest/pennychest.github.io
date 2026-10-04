"""Add the plugin READMEs to the core docs, so one MkDocs build covers both repositories.

Run from a directory holding checkouts of pennychest (as core/) and pennychest-plugins (as
plugins/). Each plugin's README becomes docs/plugins/<name>.md, the plugins repository's README
becomes docs/plugins/index.md, and a "Plugin reference" section is added to the nav.
"""

import posixpath
import re
import sys
from pathlib import Path

import yaml

PLUGINS_URL = "https://github.com/pennychest/pennychest-plugins"
LINK = re.compile(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")


def rewrite_links(text, source, pages, root):
    """Point relative links at the published page for a README, or at GitHub for anything else.

    source is the README's path in the plugins checkout at root, and pages maps those paths to
    page paths under docs/plugins/.
    """
    page_dir = posixpath.dirname(pages[source])

    def replace(match):
        target = match.group(2)
        if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith(("#", "/")):
            return match.group(0)
        path, _, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
        readme = posixpath.join(resolved, "README.md") if resolved != "README.md" else resolved
        if resolved in pages or readme in pages:
            page = pages.get(resolved) or pages[readme]
            new = posixpath.relpath(page, page_dir)
        else:
            kind = "tree" if (root / resolved).is_dir() else "blob"
            new = f"{PLUGINS_URL}/{kind}/main/{resolved}"
        return match.group(1) + new + ("#" + anchor if anchor else "") + match.group(3)

    lines, in_fence = [], False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        lines.append(line if in_fence else LINK.sub(replace, line))
    return "".join(lines)


def main(core, plugins):
    names = sorted(
        d.name for d in plugins.iterdir()
        if (d / "pyproject.toml").is_file() and (d / "README.md").is_file()
    )
    pages = {"README.md": "index.md"} | {f"{name}/README.md": f"{name}.md" for name in names}

    out = core / "docs" / "plugins"
    out.mkdir(parents=True, exist_ok=True)
    for source, page in pages.items():
        text = (plugins / source).read_text()
        (out / page).write_text(rewrite_links(text, source, pages, plugins))

    config_path = core / "mkdocs.yml"
    config = yaml.safe_load(config_path.read_text())
    section = {"Plugin reference": [f"plugins/{page}" for page in pages.values()]}
    nav = config["nav"]
    after = next((i for i, item in enumerate(nav) if "Guide" in item), len(nav) - 1)
    nav.insert(after + 1, section)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    print(f"Added {len(pages)} plugin pages: {', '.join(pages.values())}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
