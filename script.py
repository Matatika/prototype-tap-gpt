import csv
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def print_stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def exit_with_message(message: str):
    print_stderr(message)
    sys.exit(1)


def run_command(command: str, **kwargs):
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        text=True,
        **kwargs,
    )

    if process.returncode == 0:
        return process

    exit_with_message(f"Command '{command}' exited with code {process.returncode}")


if __name__ == "__main__":

    try:
        company_number = sys.argv[1]
    except IndexError:
        exit_with_message("No company number specified")

    filing_history_url = f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"
    params = {
        "category": "accounts",
        "items_per_page": 100,
    }
    auth = HTTPBasicAuth(
        username=os.environ["COMPANIES_HOUSE_API_KEY"],
        password="",  # no password required, empty string as `None` not handled as expected
    )

    response = requests.get(filing_history_url, params, auth=auth)
    response.raise_for_status()

    filing_history_data = response.json()

    if filing_history_data["total_count"] == 0:
        exit_with_message(f"No company found for company number '{company_number}'")

    company_info_url = "https://find-and-update.company-information.service.gov.uk"
    accounts_data: list[str] = []

    for item in filing_history_data["items"]:
        links: dict = item["links"]
        self_link = item["links"]["self"]
        document_metadata_url: str | None = links.get("document_metadata")

        # no document metadata link means no available documents
        if not document_metadata_url:
            continue

        # use backend document api
        document_metadata_url = (
            "https://document-api.company-information.service.gov.uk"
            + urlparse(document_metadata_url).path
        )

        # add document link if it exists in xhtml format
        response = requests.get(document_metadata_url, auth=auth)
        response.raise_for_status()

        document_data = response.json()
        resources: dict = document_data["resources"]

        made_up_date = document_data["significant_date"]
        filing_date = document_data["created_at"]

        if resources.get("application/xhtml+xml"):
            accounts_data.append(
                (
                    company_number,
                    made_up_date,
                    filing_date,
                    f"{company_info_url}{self_link}/document?format=xhtml",
                )
            )

    for data in accounts_data:
        # destructure document_url from rest of data to be written to csv
        *csv_data, document_url = data

        # regenerate db for each set of data
        shutil.rmtree(os.environ["OPENAI_CHROMA_DIR"], ignore_errors=True)

        # dynamic tap environent per invocation for each set of data
        env = {
            **os.environ,
            "TAP_BEAUTIFULSOUP_SOURCE_NAME": company_number,
            "TAP_BEAUTIFULSOUP_SITE_URL": document_url.lstrip(
                "https://"
            ),  # scheme messes up glob match with tap-beautifulsoup, so remove
            "TAP_BEAUTIFULSOUP_SITE_PATH": "",  # match anything (in this case, the only file)
        }

        # scrape document text, add embeddings and store in local vector db
        run_command(
            "meltano run tap-beautifulsoup add-embeddings target-chromadb",
            env=env,
        )

        # ask questions
        input = [
            *csv_data,
            "What is the total number of employees?",
            "What are the total assets in GBP?",
        ]

        print_stderr(f"Questions: {', '.join(input)}'")

        process = run_command(
            f"meltano invoke gpt:chat --questions '{','.join(input)}'"
        )

        print(process.stdout.strip())
