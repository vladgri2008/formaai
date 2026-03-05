import requests

# ВСТАВЬТЕ НОВЫЙ КЛЮЧ СЮДА
API_KEY = "sk-or-v1-..."  # замените на новый ключ

print("🔍 Тестируем OpenRouter ключ...")

# Простой тестовый запрос
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "google/gemini-3.1-flash-lite-preview",
        "messages": [{"role": "user", "content": "скажи привет"}],
        "max_tokens": 10
    }
)

print(f"Статус: {response.status_code}")

if response.status_code == 200:
    print("✅ Ключ работает!")
    result = response.json()
    print(f"Ответ: {result['choices'][0]['message']['content']}")
else:
    print("❌ Ошибка:")
    print(response.text)