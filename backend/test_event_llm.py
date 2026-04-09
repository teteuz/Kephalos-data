import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.env', override=True)

api_key = os.environ.get('LLM_API_KEY')
base_url = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
model = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')

print(f'Using model: {model}')

if not api_key:
    print('No API key found')
    exit(1)

client = OpenAI(api_key=api_key, base_url=base_url)

# Test event config prompt
prompt = '''Based on the following simulation requirement, generate the event configuration.

Simulation requirement: Test simulation for social media analysis

Test context here

## Available entity types and examples
- Official: government_official_1, ministry_spokesperson
- MediaOutlet: news_agency, television_network
- Student: university_student, graduate_student

## Task
Please output event configuration JSON:
- Extract hot topic keywords
- Describe narrative direction
- Design initial posts with content and poster_type (poster_type must match available entity type)

Important: poster_type must exactly match an available entity type.
Example: official statements by Official/University, news by MediaOutlet, student views by Student.

Return JSON only (no markdown):
{
    "hot_topics": ["topic1", "topic2", ...],
    "narrative_direction": "<description>",
    "initial_posts": [
        {"content": "post content", "poster_type": "entity type from available types"},
        ...
    ],
    "reasoning": "<short explanation>"
}'''

system_prompt = 'You are an opinion trend analysis expert. Return pure JSON only. IMPORTANT: Respond in English only, no Chinese characters.'

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        response_format={'type': 'json_object'},
        temperature=0.7
    )

    content = response.choices[0].message.content
    print('Raw LLM response:')
    print(repr(content))
    print()
    print('Parsed JSON:')
    parsed = json.loads(content)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))

except Exception as e:
    print(f'Error: {e}')