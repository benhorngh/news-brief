import logging

import anthropic

from workflow.settings import settings

client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)


def summarize(transcript: str) -> list[str]:
    logging.info("Generating headlines from transcript")
    lang = settings.AUDIO_LANGUAGE
    prompt = f"""I have a transcript of news in {lang}.
For each news story, please summarize it in 1-2 sentences.
Provide ONLY the summaries, each on a new line, without any prefixes, numbers, or additional text.
Filter out sports news, gossip and weather.
Order by the most important news
""".replace(
        "\n", " "
    )
    prompt += f"""Here's the text:

{transcript}

Please provide the summaries in {lang}."""
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    response = message.content[0].text.split("\n")
    print(response)
    return response
