from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
CORS(app, origins="*")

# =====================================
# ВАШ OPENROUTER API КЛЮЧ
# =====================================
OPENROUTER_API_KEY = "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"  # ваш ключ

# =====================================
# МОДЕЛЬ (можно менять)
# =====================================
MODEL_NAME = "google/gemini-3.1-flash-lite-preview"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Сервер работает через OpenRouter"})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Сервер работает с OpenRouter!"})

@app.route('/models', methods=['GET'])
def list_models():
    """Просмотр доступных моделей"""
    try:
        response = requests.get(
            url="https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            model_names = [model['id'] for model in models.get('data', [])[:50]]
            return jsonify({"success": True, "models": model_names})
        else:
            return jsonify({"success": False, "error": f"Ошибка: {response.status_code}"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def build_prompt(topic, tone, length, features):
    """
    Строит промпт на основе параметров пользователя
    
    Параметры:
    - topic: тема текста
    - tone: нейтральный/дружеский/серьезный
    - length: short(150)/medium(300)/long(600) символов
    - features: список выбранных опций (цитаты, список, вывод, примеры)
    """
    
    # =====================================
    # 1. НАСТРОЙКА ТОНА
    # =====================================
    tone_instructions = {
        'neutral': 'Используй нейтральный, спокойный тон. Пиши информативно и объективно.',
        'friendly': 'Используй дружелюбный, теплый тон. Обращайся к читателю на "ты", будь приветливым и вдохновляющим.',
        'serious': 'Используй серьезный, деловой тон. Пиши уважительно, с фокусом на факты и логику.'
    }
    
    # =====================================
    # 2. НАСТРОЙКА ДЛИНЫ (точные лимиты)
    # =====================================
    length_instructions = {
        'short': f'Текст должен быть очень кратким — строго 150-200 знаков (3-4 предложения). Только самое главное, без воды.',
        'medium': f'Текст должен быть среднего размера — строго 300-400 знаков (5-7 предложений). Раскрой тему достаточно подробно.',
        'long': f'Текст должен быть развернутым — строго 600-800 знаков (8-12 предложений). Раскрой тему полностью, с примерами и пояснениями.'
    }
    
    # =====================================
    # 3. НАСТРОЙКА ДОПОЛНИТЕЛЬНЫХ ЭЛЕМЕНТОВ
    # =====================================
    feature_instructions = []
    
    if 'quote' in features:
        feature_instructions.append('- Добавь подходящую цитату известного человека по теме (в кавычках, с указанием автора)')
    
    if 'list' in features:
        feature_instructions.append('- Используй маркированный список для перечисления ключевых пунктов (3-5 пунктов)')
    
    if 'conclusion' in features:
        feature_instructions.append('- В конце добавь четкий вывод или резюме (начни с "Вывод:" или "Итог:")')
    
    if 'examples' in features:
        feature_instructions.append('- Приведи 1-2 конкретных примера из жизни, чтобы проиллюстрировать тему')
    
    # Если ничего не выбрано, добавляем базовую структуру
    if not feature_instructions:
        feature_instructions = ['- Структурируй текст: введение, основная часть, заключение']
    
    # =====================================
    # 4. СБОРКА ПОЛНОГО ПРОМПТА
    # =====================================
    
    prompt = f"""ТЫ — ПРОФЕССИОНАЛЬНЫЙ КОПИРАЙТЕР.
Напиши текст на русском языке на тему: "{topic}"

🔴 ТОН:
{tone_instructions.get(tone, tone_instructions['neutral'])}

🔴 ОБЪЕМ:
{length_instructions.get(length, length_instructions['medium'])}

🔴 СТРУКТУРА И ЭЛЕМЕНТЫ:
{' '.join(feature_instructions)}

🔴 ВАЖНЫЕ ТРЕБОВАНИЯ:
- Только русский язык
- Текст должен быть законченным и полезным
- Без лишних вступлений вроде "Вот текст..."
- Без комментариев от себя
- Строго соблюдай указанный объем
- Используй правильную грамматику и пунктуацию
- Не используй markdown или звездочки — только обычный текст

Напиши текст прямо сейчас, без пояснений:"""
    
    return prompt

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Получаем данные
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({"success": False, "error": "Тема не может быть пустой"}), 400
        
        # Получаем все параметры
        tone = data.get('tone', 'neutral')
        length = data.get('length', 'medium')
        
        # Получаем выбранные опции (features)
        # Во фронтенде нужно будет передавать массив выбранных опций
        features = data.get('features', [])
        
        print(f"📝 Тема: {topic}")
        print(f"🎭 Тон: {tone}")
        print(f"📏 Длина: {length}")
        print(f"✨ Опции: {features}")
        
        # Строим промпт
        user_prompt = build_prompt(topic, tone, length, features)
        
        # Для отладки можно посмотреть промпт
        print("\n🔍 ПРОМПТ:")
        print("-" * 40)
        print(user_prompt)
        print("-" * 40)
        
        # Отправляем запрос к OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Forma Generator"
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Ты профессиональный копирайтер. Пиши точно по инструкции, соблюдай все требования."},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Ошибка OpenRouter: {response.status_code}")
            print(response.text)
            return jsonify({
                "success": False,
                "error": f"OpenRouter вернул ошибку {response.status_code}"
            }), 500
        
        result = response.json()
        
        if 'choices' not in result or len(result['choices']) == 0:
            return jsonify({"success": False, "error": "Пустой ответ"}), 500
            
        generated_text = result['choices'][0]['message']['content']
        
        # Подсчет символов для проверки
        char_count = len(generated_text)
        print(f"✅ Сгенерировано: {char_count} символов")
        
        return jsonify({
            "success": True,
            "text": generated_text,
            "stats": {
                "characters": char_count,
                "words": len(generated_text.split())
            }
        })
        
    except Exception as e:
        print("❌ Ошибка:", traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 ЗАПУСК СЕРВЕРА FORMA (OPENROUTER)")
    print("="*60)
    print(f"🔑 Ключ: {OPENROUTER_API_KEY[:15]}...")
    print(f"🤖 Модель: {MODEL_NAME}")
    print("🌍 http://localhost:5000")
    print("="*60)
    app.run(port=5000, debug=True)