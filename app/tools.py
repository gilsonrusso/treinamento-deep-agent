import json
import re
from typing import Any
import arxiv
from langchain.tools import tool

from app.core.logger import logger


@tool
def search_arxiv_articles(
    query: str,
    max_results: int = 5,
) -> str:
    """
    Pesquisa artigos científicos no repositório oficial do arXiv.

    Use para localizar trabalhos acadêmicos, preprints e pesquisas científicas
    em inteligência artificial, computação, matemática, física e áreas afins.

    Retorna título, autores, data de publicação, categoria primária, resumo,
    link do arXiv e URL direta para o PDF.
    """
    if not query or not query.strip():
        return "A consulta de pesquisa não pode estar vazia."

    max_results = max(1, min(max_results, 10))

    try:
        logger.info(f"Consultando arXiv para: [cyan]{query}[/cyan] (max: {max_results})")
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=3.0,
            num_retries=3,
        )

        search = arxiv.Search(
            query=query.strip(),
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []

        for index, paper in enumerate(client.results(search), start=1):
            summary = paper.summary or "Não disponível"
            summary = re.sub(r"\s+", " ", summary).strip()

            results.append({
                "index": index,
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else "N/A",
                "primary_category": paper.primary_category or "N/A",
                "arxiv_url": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "doi": paper.doi or "N/A",
                "summary": summary[:1500],
            })

        if not results:
            return f"Nenhum artigo encontrado no arXiv para a consulta: '{query}'."

        return json.dumps(results, ensure_ascii=False, indent=2)

    except Exception as error:
        logger.error(f"Erro ao consultar arXiv: {error}")
        return f"Erro ao consultar arXiv: {error}"


# Alias de compatibilidade
search_scientific_articles = search_arxiv_articles

__all__ = ["search_arxiv_articles", "search_scientific_articles"]
