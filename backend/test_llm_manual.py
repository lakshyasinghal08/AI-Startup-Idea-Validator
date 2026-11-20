import asyncio
from app.services.llm_service import LLMService


async def main():
    llm = LLMService(provider="gemini")

    # Test normal text generation
    response = await llm.generate_completion(
        system_prompt="You are a startup mentor.",
        user_prompt="Evaluate this idea in 3 sentences: AI platform for local farmers.",
    )

    print("\nTEXT RESPONSE:")
    print(response)

    # Test JSON generation
    json_response = await llm.generate_structured_json(
        system_prompt="You are a startup idea evaluator.",
        user_prompt=(
            "Evaluate an AI platform for local farmers. "
            "Return JSON with idea_summary, feasibility_score, "
            "strengths, and weaknesses."
        ),
    )

    print("\nJSON RESPONSE:")
    print(json_response)


if __name__ == "__main__":
    asyncio.run(main())