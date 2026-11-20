import asyncio
import os
import sys

# Ensure backend directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from app.agents.idea_agent import IdeaAgent


async def main():
    agent = IdeaAgent()

    idea_data = {
        "title": "AI Platform for Local Farmers",
        "description": (
            "An AI platform that helps farmers choose crops, "
            "detect crop diseases, predict yields, and understand market prices."
        ),
        "target_market": "Small and medium-scale farmers in India",
    }

    result = await agent.execute(idea_data)

    print("\n===== IDEA VALIDATION RESULT =====")
    for key, value in result.items():
        print(f"\n{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())