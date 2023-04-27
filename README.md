# Prototype tap-gpt

Hack together a Meltano based ELT+ to perform unsupervised question answering with ChatGPT.

## Get Started

Create a .env

```
    TAP_BEAUTIFULSOUP_SOURCE_NAME=matatika-docs
    TAP_BEAUTIFULSOUP_SITE_URL=find-and-update.company-information.service.gov.uk/company/03007129/filing-history/MzM2NDE1Mjc2NWFkaXF6a2N4/document?format=xhtml
    TAP_BEAUTIFULSOUP_SITE_PATH=""
    #TAP_BEAUTIFULSOUP_PARSER=lxml
    OPENAI_API_KEY=[your key]
    OPENAI_CHROMA_DIR=output/chromadb
    OPENAI_CHAT_HISTORY_DIR=output/history
```

Run the extraction

```
    rm -fR ./output/chromadb
    meltano run tap-beautifulsoup add-embeddings target-chromadb
    meltano invoke gpt:chat --questions="123456,How many employees?,What are the total assets in gbp?"
```

Expected stdout output

```
    03007129,89,"3,625,897"

```


## What does this project do?

1. `tap-beautifulsoup`
   1. Extract text content from a website using the BeautifulSoup web scraping library.
1. `map-gpt-embeddings`
   1. Split text content into smaller documents using the LangChain library.
   1. Calculate "Embeddings" for each text segment. These are calculated by making a call to the OpenAI Endpoint.
1. `target-chromadb`
   1. Store the extracted and mapped data into ChromaDB vectorstore, backed by DuckDB and Parquet.
1. `gpt:chat`
   1. Prompt for a question from the user.
   2. Use LangChain to find the document segments in ChromaDB which most closely match the prompt.
   3. Use LangChain to create a modified prompt to send to ChatGPT, prefixing all of the data we found when querying our vectorstore.
   4. Send the modified prompt to the ChatGPT API endpoints, and render the response to the user.

## Glossary of terms and tools

### Embeddings

In low-tech terms, an array of ~1,500 floats. More specifically, a numeric representation of text data with very high dimensionality. Embeddings allow similar things being mathematically adjacent to others.

### LangChain

A an open source tool which streamlines “chaining” together of multiple LLM tasks.

### OpenAI

The company which provides GPT, ChatGPT, and a number of other AI products. OpenAI also provides the Embeddings API used in map-gpt-embeddings.

### Vector Store

A specialized database for analyzing vector embeddings.

### ChromaDB

An open source and pip-installable vector store database.
