
import asyncio
from backend.ai_engine import get_ai_client
import os


async def test_grok():
    client = get_ai_client()

    model = os.getenv("AI_MODEL", "grok-4.7")

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Explain SQL injection in exactly two simple sentences."
            }
        ],
        max_tokens=150
    )

    print("\nGROK API CONNECTION SUCCESSFUL!")
    print("Model:", model)
    print("\nGrok response:")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(test_grok())
