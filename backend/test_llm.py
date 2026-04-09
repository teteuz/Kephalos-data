import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.env', override=True)

api_key = os.environ.get('LLM_API_KEY')
base_url = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
model = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')

print(f'Using model: {model}')
print(f'Base URL: {base_url}')

if not api_key:
    print('No API key found')
    exit(1)

client = OpenAI(api_key=api_key, base_url=base_url)

prompt = '''Based on the following simulation requirement, generate the time simulation configuration.

Test simulation for social media analysis

## Task
Please output a JSON object for time configuration.

### Return JSON only (no markdown)

Example:
{
    "total_simulation_hours": 72,
    "minutes_per_round": 60,
    "agents_per_hour_min": 5,
    "agents_per_hour_max": 50,
    "peak_hours": [19, 20, 21, 22],
    "off_peak_hours": [0, 1, 2, 3, 4, 5],
    "morning_hours": [6, 7, 8],
    "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "reasoning": "Explain the rationale for this time configuration."
}'''

system_prompt = 'You are a social media simulation expert. Return pure JSON only. IMPORTANT: Respond in English only, no Chinese characters.'

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