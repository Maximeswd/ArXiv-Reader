# arxiv_cli.py
import requests
import feedparser
import argparse
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.style import Style
from rich import box
import re
from util import add_to_table

# --- Setup ---
console = Console()
parser = argparse.ArgumentParser(description="Fetch and filter the latest papers directly from the arXiv API.")
parser.add_argument('-k', '--keyword', nargs='+', help='A list of keywords to search for.')
parser.add_argument('-a', '--author', nargs='+', help='A list of authors to search for.')
parser.add_argument('-c', '--category', nargs='+', default=['cs.LG', 'cs.CL', 'cs.CV', 'cs.AI', 'cs.IR'], help='arXiv CS categories to search (e.g., cs.LG cs.CV). Default is all CS.') # ['cs.*'] will fetch all CS categories.
parser.add_argument('--max', type=int, default=2000, help='Maximum number of recent papers to fetch. Default is 2000 to get all of today\'s papers.')
parser.add_argument('-w', '--whole-word', action='store_true', help='Perform a whole-word search for keywords.')
args = parser.parse_args()

def fetch_latest_papers(categories, max_results):
    """Fetches the latest papers from specified categories from the arXiv API."""
    base_url = 'http://export.arxiv.org/api/query?'
    
    # Format categories for the API query (e.g., cat:cs.LG+OR+cat:cs.CV)
    cat_query = '+OR+'.join([f'cat:{cat}' for cat in categories])
    query = f'search_query={cat_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    with console.status(f"Querying arXiv API for the latest {max_results} papers in {categories}...", spinner="dots"):
        try:
            response = requests.get(base_url + query)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            results = {'title': [], 'authors': [], 'abstract': [], 'url': []}
            for entry in feed.entries:
                results['title'].append(entry.title.replace('\n', ' ').strip())
                results['authors'].append(', '.join(author.name for author in entry.authors))
                results['abstract'].append(entry.summary.replace('\n', ' ').strip())
                results['url'].append(entry.link)
                
            return pd.DataFrame(results)
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Error fetching data from arXiv API: {e}[/bold red]")
            return pd.DataFrame()

def main():
    df = fetch_latest_papers(categories=args.category, max_results=args.max)
    if df.empty:
        return

    if args.keyword or args.author:
        keywords = args.keyword if args.keyword else []
        authors = args.author if args.author else []
    else:
        with open('keywords.txt', 'r') as file:
            keywords = [k for k in file.read().splitlines() if len(k) > 2]
        with open('authors.txt', 'r') as file:
            authors = [a for a in file.read().splitlines() if len(a) > 2]

    table = Table(box=box.HORIZONTALS, show_lines=False, show_header=False)
    keyword_style = Style(color="red", bold=True)
    table.add_column(max_width=15, justify='center', style=keyword_style)
    table.add_column()

    if not keywords and not authors:
        console.print("[bold red]No keywords or authors to search for.[/bold red]")
        return

    found_match = False
    for keyword in keywords:
        if args.whole_word:
            search_pattern = r'\b' + re.escape(keyword) + r'\b'
            match = df[df['title'].str.contains(search_pattern, case=False, na=False, regex=True) | 
                       df['abstract'].str.contains(search_pattern, case=False, na=False, regex=True)]
        else:
            match = df[df['title'].str.contains(keyword, case=False, na=False) | 
                       df['abstract'].str.contains(keyword, case=False, na=False)]
        
        if not match.empty:
            found_match = True
            table.add_row(keyword)
            table = add_to_table(match, table, keyword)
            table.add_section()

    for author in authors:
        match = df[df['authors'].str.contains(author, case=False, na=False)]
        if not match.empty:
            found_match = True
            table.add_row(author)
            table = add_to_table(match, table, author)
            table.add_section()

    if found_match:
        console.print(table)
    else:
        console.print("[yellow]No matching papers found for the given criteria.[/yellow]")

if __name__ == '__main__':
    main()