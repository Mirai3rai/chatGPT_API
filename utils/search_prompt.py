import re
from typing import List
from datetime import datetime
from .search_abc import SearchResult

def remove_commands(query: str) -> str:
    query = re.sub(r'\/page:(\S+)\s+', '', query)
    query = re.sub(r'\/site:(\S+)\s+', '', query)
    return query


def compile_prompt(results: List[SearchResult], query: str) -> str:
    default_prompt = "Web search results:\n\n{web_results}\nCurrent date: {current_date}\n\nInstructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using [[number](URL)] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.\nQuery: {query}"
    formatted_results = format_web_results(results)
    current_date = datetime.now().strftime("%m/%d/%Y")
    return replace_variables(
        default_prompt,
        {
            '{web_results}': formatted_results,
            '{query}': remove_commands(query),
            '{current_date}': current_date,
        },
    )


def format_web_results(results: List[SearchResult]) -> str:
    return (
        "".join(
            f'[{counter}] \"{result.body}\"\nURL: {result.url}\n\n'
            for counter, result in enumerate(results, start=1)
        )
        if results
        else "No results found.\n"
    )


def replace_variables(prompt: str, variables: dict) -> str:
    new_prompt = prompt
    for key, value in variables.items():
        try:
            new_prompt = new_prompt.replace(key, value)
        except Exception as error:
            print("Search prompt error: ", error)
    return new_prompt