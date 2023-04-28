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

## Run the script

### Create a Companies House API key
- Go to [Create an application](https://developer.company-information.service.gov.uk/manage-applications/add) (sign up for a Companies House account if not done already)
   - 'Application name' is required
   - 'Description of application' is required
   - 'Choose an environment for your application' set to 'Live'
- Go to [View all applications](https://developer.company-information.service.gov.uk/manage-applications) and click on your newly created application name under 'Live applications'
- Under 'Keys for this application', click 'Create new key'
   - 'Key name' is required
   - 'Key description' is required
   - 'Choose an environment for your application' set to 'Live'
   - 'Select the type of API client key you want to create' set to 'REST'
- Copy the 'API key' value for the newly created application key 


Before running the script:

```sh
# ensure plugins installed
meltano install

# create/activate virtual environment
python3 -m venv/bin/activate
. venv/bin/activate

# install dependencies
pip install -r requirements.txt

# set required environment varaiables
echo 'COMPANIES_HOUSE_API_KEY=your-api-key' >> .env
echo 'OPENAI_API_KEY=your-api-key' >> .env
# export COMPANIES_HOUSE_API_KEY='your-api-key'
# export OPENAI_API_KEY='your-api-key'

```

Then:

```sh
python3 script.py $COMPANY_NUMBER

# e.g. python3 script.py 08275103

# output to a csv file
echo 'company_number,accounts_made_up_date,accounts_filing_date,total_employees,total_assets' > output/results.csv
python3 script.py $COMPANY_NUMBER >> output/results.csv
```

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
