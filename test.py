import os

from dotenv import load_dotenv
from tavily import TavilyClient


def main():
    print("Step 1: Script Started")
    print("Step 2: Imports Successful")

    load_dotenv()
    print("Step 3: .env Loaded")

    api_key = os.getenv("TAVILY_API_KEY")
    print("API KEY =", api_key)

    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing!")

    client = TavilyClient(api_key=api_key)
    print("Step 4: Client Created")

    response = client.search(
        query="AI startup validation",
        max_results=3,
    )

    print("Step 5: Search Completed")
    print(response)


if __name__ == "__main__":
    main()
