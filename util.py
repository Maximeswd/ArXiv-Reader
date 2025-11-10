from rich.style import Style
from rich.text import Text
import re

ACTIVE_THEME = "nordic"

# Theme defs
THEMES = {
    "vibrant": {
        "title": "purple",
        "author": "magenta",
        "link": "bright_blue",
        "abstract": "green"
    },
    "solarized": {
        "title": "yellow",
        "author": "cyan",
        "link": "blue",
        "abstract": "white"
    },
    "classic": {
        "title": "bright_white",
        "author": "green",
        "link": "bright_blue",
        "abstract": "white"
    },
    "nordic": {
        "title": "bright_cyan",
        "author": "magenta",
        "link": "blue",
        "abstract": "bright_white"
    }
}

def clean_abstract(abstract):
    if isinstance(abstract, str) and "\\\\" in abstract:
        valid = abstract.split("\\\\")[1:]
        return " ".join(valid).strip()
    return abstract.strip() if isinstance(abstract, str) else ""

def get_until(i, lines, delim, n_skip=0):
    text = lines[i][n_skip:].strip() + ' '
    i += 1
    try:
        while not lines[i].startswith(delim):
            text += lines[i].strip() + ' '
            i += 1
    except IndexError:
        return text
    return text

def add_to_table(df, table, keyword):
    # Load the selected color theme
    try:
        colors = THEMES[ACTIVE_THEME]
    except KeyError:
        print(f"Warning: Theme '{ACTIVE_THEME}' not found. Falling back to 'vibrant'.")
        colors = THEMES["vibrant"]

    # Define styles based on the loaded theme
    title_style = Style(color=colors["title"], bold=True)
    author_style = Style(color=colors["author"])
    link_style = Style(color=colors["link"])
    abstract_style = Style(color=colors["abstract"])
    highlight_style = "bold underline"

    highlight_regex = f"(?i)({re.escape(keyword)})"

    for _, row in df.iterrows():
        title_str = row.get('title', '')
        authors_str = row.get('authors', '')
        url_str = row.get('url', '')
        abstract_str = clean_abstract(row.get('abstract', ''))

        title_text = Text(title_str)
        authors_text = Text(authors_str)
        abstract_text = Text(abstract_str)

        title_text.highlight_regex(highlight_regex, style=highlight_style)
        abstract_text.highlight_regex(highlight_regex, style=highlight_style)
        authors_text.highlight_regex(highlight_regex, style=highlight_style)

        table.add_row('', title_text, style=title_style)
        table.add_row('', authors_text, style=author_style)
        table.add_row('', url_str, style=link_style)
        table.add_row('', abstract_text, style=abstract_style)
        table.add_row('')
    return table
