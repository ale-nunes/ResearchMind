"""Streamlit interface for the ResearchMind multi-agent research assistant."""

from __future__ import annotations

from typing import Literal, Protocol, cast

import streamlit as st

from researchmind.config import settings
from researchmind.graph import build_research_graph
from researchmind.llm.gemini import GeminiTextGenerator
from researchmind.schemas import ResearchState


class InvokableResearchGraph(Protocol):
    """Narrow protocol for the compiled graph's invoke method."""

    def invoke(self, input: ResearchState) -> ResearchState:
        """Run the graph and return its final state."""


st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 ResearchMind")
st.caption("Assistente de pesquisa multiagente com documentos, busca na web e fontes citadas.")

with st.sidebar:
    st.subheader("Configurações")
    research_mode_label = st.radio(
        "Fontes de pesquisa",
        options=["Documentos + web", "Somente documentos"],
        index=0,
        help=(
            "Documentos + web combina a base local com pesquisa pública. "
            "Somente documentos consulta apenas os arquivos indexados."
        ),
    )
    st.caption("A chave do Gemini é lida de `.env` e não deve ser inserida na interface.")
    if settings.gemini_api_key:
        st.success("Chave Gemini configurada")
    else:
        st.warning("Chave Gemini não configurada")

st.markdown("### O que você quer pesquisar?")
with st.form("research_form", clear_on_submit=False):
    question = st.text_area(
        "Pergunta de pesquisa",
        placeholder=(
            "Ex.: Quais são os principais argumentos dos documentos sobre o tema "
            "e como eles se relacionam com fontes públicas?"
        ),
        height=130,
        max_chars=4000,
    )
    submitted = st.form_submit_button("Iniciar pesquisa", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.warning("Digite uma pergunta antes de iniciar a pesquisa.")
    elif not settings.gemini_api_key:
        st.error(
            "A chave da API do Gemini não foi encontrada. Configure `GEMINI_API_KEY` "
            "no arquivo `.env` local e reinicie o Streamlit."
        )
    else:
        mode: Literal["documents_only", "documents_web"] = (
            "documents_only"
            if research_mode_label == "Somente documentos"
            else "documents_web"
        )

        try:
            with st.spinner("Pesquisando fontes, analisando evidências e redigindo o relatório..."):
                generator = GeminiTextGenerator()
                graph = cast(InvokableResearchGraph, build_research_graph(generator))
                result = graph.invoke(
                    {
                        "question": question.strip(),
                        "research_mode": mode,
                    }
                )
            st.session_state["researchmind_last_result"] = result
            st.session_state["researchmind_last_question"] = question.strip()
        except Exception as exc:
            st.error(
                "Não foi possível concluir a pesquisa. Verifique a configuração e tente novamente."
            )
            with st.expander("Detalhes técnicos para diagnóstico"):
                st.code(f"{type(exc).__name__}: {exc}", language="text")

if "researchmind_last_result" in st.session_state:
    result = st.session_state["researchmind_last_result"]
    last_question = st.session_state.get("researchmind_last_question", "")
    st.divider()
    st.subheader("Relatório")
    if last_question:
        st.markdown(f"**Pergunta:** {last_question}")
    report = result.get("report", "")
    if isinstance(report, str) and report.strip():
        st.markdown(report)
    else:
        st.warning("O fluxo terminou sem produzir um relatório.")

    with st.expander("Evidências recuperadas", expanded=False):
        evidence = result.get("evidence", [])
        if isinstance(evidence, list) and evidence:
            for index, item in enumerate(evidence, start=1):
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or item.get("source") or f"Fonte {index}")
                citation = str(item.get("citation") or item.get("url") or "")
                snippet = str(item.get("text") or item.get("snippet") or "")
                st.markdown(f"**{index}. {title}**")
                if citation:
                    st.markdown(f"Fonte: {citation}")
                if snippet:
                    st.write(snippet)
                st.divider()
        else:
            st.info("Nenhuma evidência foi recuperada para esta pesquisa.")

    errors = result.get("errors", [])
    if isinstance(errors, list) and errors:
        with st.expander("Avisos da pesquisa", expanded=False):
            for error in errors:
                st.warning(str(error))

    report_text = str(report or "")
    if report_text:
        st.download_button(
            "Baixar relatório em Markdown",
            data=report_text,
            file_name="researchmind_report.md",
            mime="text/markdown",
        )

st.divider()
st.caption(
    "ResearchMind — respostas geradas por IA podem conter erros. "
    "Confira as fontes citadas antes de usar conclusões importantes."
)
