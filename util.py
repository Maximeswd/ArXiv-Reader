from rich.style import Style
from rich.highlighter import RegexHighlighter
import re

class KeywordHighlighter(RegexHighlighter):
    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword
        self.highlights = f'(?i)({self.keyword})'
        self.base_style = "bold underline"

    def highlight(self, text):
        text.highlight_regex(re_highlight=self.highlights, style=self.base_style)

def clean_abstract(abstract):
    if isinstance(abstract, str) and "\\\\" in abstract:
        valid = abstract.split("\\\\")[1:]
        return " ".join(valid)
    return abstract if isinstance(abstract, str) else ""

def add_to_table(df, table, keyword):
    title_style = Style(color="bright_blue", bold=True)
    highlighter = KeywordHighlighter(keyword)
    for _, row in df.iterrows():
        table.add_row('', highlighter(row['title']), style=title_style)
        table.add_row('', highlighter(row['authors']), style='purple')
        table.add_row('', row['url'], style='cyan')
        cleaned_abstract = clean_abstract(row.get('abstract', ''))
        table.add_row('', highlighter(cleaned_abstract), style='green')
        table.add_row('')
    return table

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