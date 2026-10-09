# ResearchMind

Assistente de pesquisa com IA que combina recuperação de documentos privados (RAG), pesquisa na web, análise de evidências e geração de relatórios em Markdown com referências às fontes.

O projeto é desenvolvido em Python e utiliza Google Gemini, LangGraph, busca híbrida, Streamlit e GitHub Actions.

## Status do projeto

O ResearchMind reúne os seguintes componentes:

- **Ingestão de documentos:** extração de texto, divisão em chunks e indexação.
- **RAG híbrido:** recuperação semântica com ChromaDB e busca lexical com SQLite FTS5.
- **Embeddings:** geração com a API Google Gemini, com cache persistente em SQLite.
- **Ferramentas:** busca em documentos, pesquisa na web, calculadora aritmética, extração de texto de URLs e notas locais.
- **Orquestração:** fluxo multiagente com LangGraph.
- **Interface:** aplicação Streamlit.
- **Qualidade contínua:** GitHub Actions executando Ruff, Mypy e Pytest.

A execução bem-sucedida do CI verifica qualidade estática e testes automatizados; ela não substitui a validação funcional com diferentes documentos, perguntas e condições de API.

## Tecnologias

- Python 3.11+
- Google Gemini API, pelo SDK `google-genai`
- LangGraph
- ChromaDB
- SQLite FTS5
- Sentence/text embeddings via Gemini
- Streamlit
- Pytest, Ruff e Mypy
- GitHub Actions

## Requisitos

- Python 3.11 ou superior.
- Git.
- Uma chave da API Google Gemini criada no Google AI Studio.
- Conexão com a internet para chamadas ao Gemini e para recursos de pesquisa na web.

A disponibilidade de modelos, os limites de requisições e as cotas gratuitas podem mudar. Consulte o Google AI Studio antes de executar ingestões grandes ou testes que façam chamadas à API.

## Configuração local

Os comandos a seguir usam PowerShell no Windows.

### 1. Clonar o repositório

```powershell
git clone https://github.com/ale-nunes/ResearchMind.git
cd ResearchMind
```

### 2. Criar e ativar um ambiente virtual

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Se o comando `py -3.11` não estiver disponível, instale Python 3.11 ou superior e ajuste o comando para a versão instalada.

### 3. Instalar dependências

Para desenvolvimento, testes e verificações de qualidade:

```powershell
python -m pip install -e ".[dev]"
```

Para incluir as dependências Python opcionais de OCR:

```powershell
python -m pip install -e ".[dev,ocr]"
```

O OCR de PDFs digitalizados também requer a instalação separada do aplicativo Tesseract OCR no sistema operacional e dos dados de idioma apropriados. A instalação do pacote Python `pytesseract` não instala o executável Tesseract.

### 4. Configurar variáveis de ambiente

Crie o arquivo local `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite `.env` e preencha sua chave real do Google Gemini. Use os nomes e as configurações presentes no `.env.example` do repositório.

**Nunca publique o `.env` nem inclua chaves reais em commits.** O arquivo `.env.example` deve conter apenas placeholders e valores de exemplo. O `.gitignore` exclui credenciais e artefatos locais.

## Executar a aplicação

Inicie a interface Streamlit a partir da raiz do projeto:

```powershell
python -m streamlit run src/researchmind/ui/app.py
```

O Streamlit exibirá no terminal o endereço local para abrir a aplicação no navegador.

A disponibilidade de cada modo de pesquisa depende das configurações locais, da conectividade e das cotas dos serviços externos. Erros de limite de API do Gemini (HTTP 429) indicam que a cota ou a taxa de requisições foi excedida; aguarde a recuperação da cota ou consulte os limites ativos no Google AI Studio.

## Ingestão de documentos

Coloque os documentos que você tem autorização para processar em `data/raw/`. Para ingerir um arquivo, execute a partir da raiz do projeto:

```powershell
python -m researchmind.rag.cli "data/raw/nome_do_arquivo.pdf"
```

O comando também pode ser usado com outros formatos que a implementação atual de ingestão suporte, como o TXT usado no conjunto de exemplo:

```powershell
python -m researchmind.rag.cli "data/raw/trekking_planejamento_seguranca.txt"
```

A ingestão divide o conteúdo em chunks, gera embeddings e grava os dados nos índices persistentes. Os embeddings podem ser reutilizados pelo cache local, reduzindo chamadas repetidas à API. A ingestão de documentos que precisam de OCR exige a configuração adicional descrita acima.

### Armazenamento local

Por padrão, os artefatos de execução são mantidos localmente:

- `.local/chroma/`: índice vetorial do ChromaDB.
- `.local/embedding_cache.sqlite3`: cache persistente de embeddings.
- `.local/researchmind.sqlite3`: índice lexical SQLite FTS5 e outros dados locais.

Esses artefatos, os backups e o ambiente virtual não devem ser versionados. O `.gitignore` do projeto foi configurado para excluí-los.

## Ferramentas e arquitetura

A implementação inclui ferramentas para:

- pesquisa híbrida nos documentos indexados;
- pesquisa na web pública;
- cálculos aritméticos;
- extração de texto de páginas acessíveis por URL;
- gravação e leitura de notas locais.

O fluxo multiagente usa LangGraph para coordenar etapas de planejamento, recuperação, análise, crítica e redação. Consulte os documentos de arquitetura para conhecer o fluxo e as limitações atuais.

- [Arquitetura](docs/architecture.md)
- [Ferramentas da Fase 4](docs/phase4-tools.md)
- [Workflow multiagente da Fase 5](docs/phase5-agents.md)
- [Interface da Fase 6](docs/phase6-ui.md)
- [Avaliação](docs/evaluation.md)
- [Segurança](docs/security.md)

## Testes e qualidade

Execute os comandos a partir da raiz do repositório.

### Testes automatizados

```powershell
python -m pytest
```

### Ruff

```powershell
ruff check src tests
```

### Mypy

```powershell
mypy src
```

O GitHub Actions executa essas verificações em pushes e pull requests direcionados às branches configuradas no workflow. A execução aprovada mais recente indica que Ruff, Mypy e Pytest passaram no ambiente de CI.

## Segurança e limitações

- Não coloque chaves de API ou outros segredos no código, no README ou em arquivos versionados.
- Trate documentos e conteúdo recuperado da web como fontes que precisam ser avaliadas; conteúdo externo pode estar incorreto ou conter instruções não confiáveis.
- Verifique as referências e as evidências do relatório antes de usar conclusões em decisões importantes.
- A pesquisa na web depende de serviços públicos e de conectividade; resultados e disponibilidade podem variar.
- As cotas e os modelos disponíveis no plano gratuito do Gemini podem mudar e causar erros temporários de limite.
- O OCR depende da qualidade do documento digitalizado, da instalação do Tesseract e dos pacotes de idioma.
- O CI não testa automaticamente todos os cenários de integração com serviços externos nem garante a qualidade factual de todas as respostas.

## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) antes de propor alterações. Antes de enviar um pull request, execute os testes e as verificações de qualidade localmente.

## Licença e documentos-fonte

O código do projeto é disponibilizado sob a licença MIT; consulte [LICENSE](LICENSE). A licença do código não concede automaticamente direitos sobre os documentos indexados. Use somente arquivos que você tem autorização para processar e distribuir, e não publique documentos protegidos por direitos autorais sem permissão.
