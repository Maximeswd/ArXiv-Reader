from rich.style import Style
from rich.text import Text
import re

ACTIVE_THEME = "nordic"

THEMES = {
    "vibrant": {
        "title": "purple",
        "author": "magenta",
        "link": "bright_blue",
        "abstract": "green",
    },
    "solarized": {
        "title": "yellow",
        "author": "cyan",
        "link": "blue",
        "abstract": "white",
    },
    "classic": {
        "title": "bright_white",
        "author": "green",
        "link": "bright_blue",
        "abstract": "white",
    },
    "nordic": {
        "title": "bright_cyan",
        "author": "magenta",
        "link": "blue",
        "abstract": "bright_white",
    },
}


def clean_abstract(abstract):
    if isinstance(abstract, str) and "\\\\" in abstract:
        valid = abstract.split("\\\\")[1:]
        return " ".join(valid).strip()
    return abstract.strip() if isinstance(abstract, str) else ""


def get_until(i, lines, delim, n_skip=0):
    text = lines[i][n_skip:].strip() + " "
    i += 1
    try:
        while not lines[i].startswith(delim):
            text += lines[i].strip() + " "
            i += 1
    except IndexError:
        return text
    return text


def add_to_table(df, table, keywords_to_highlight):
    try:
        colors = THEMES[ACTIVE_THEME]
    except KeyError:
        print(f"Warning: Theme '{ACTIVE_THEME}' not found. Falling back to 'vibrant'.")
        colors = THEMES["vibrant"]

    title_style = Style(color=colors["title"], bold=True)
    author_style = Style(color=colors["author"])
    link_style = Style(color=colors["link"])
    abstract_style = Style(color=colors["abstract"])
    highlight_style = "bold underline"

    for _, row in df.iterrows():
        title_text = Text(row.get("title", ""))
        authors_text = Text(row.get("authors", ""))
        abstract_text = Text(clean_abstract(row.get("abstract", "")))

        if keywords_to_highlight:
            for keyword in keywords_to_highlight:
                if isinstance(keyword, str):
                    # --- THIS IS THE CORRECTED LINE ---
                    # Added \b for word boundaries to ensure whole word matching.
                    highlight_regex = f"(?i)\\b({re.escape(keyword)})\\b"
                    # --- END OF CORRECTION ---

                    title_text.highlight_regex(highlight_regex, style=highlight_style)
                    abstract_text.highlight_regex(
                        highlight_regex, style=highlight_style
                    )
                    authors_text.highlight_regex(highlight_regex, style=highlight_style)

        table.add_row("", title_text, style=title_style)
        table.add_row("", authors_text, style=author_style)
        table.add_row("", row.get("url", ""), style=link_style)
        table.add_row("", abstract_text, style=abstract_style)
        table.add_row("")
    return table
