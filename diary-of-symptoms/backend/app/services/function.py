import json
import os
from weasyprint import HTML
from dotenv import load_dotenv
from google import genai
import markdown

load_dotenv()

def build_ai_insight(symptom_entry) -> str:
    prompt = (
        f"Проанализируй состояние. Симптом: {symptom_entry.symptom}, "
        f"тяжесть: {symptom_entry.severity}/10, длительность: {symptom_entry.duration}. "
        f"Сон: {symptom_entry.sleep_hours}ч (качество: {symptom_entry.sleep_quality}/10). "
        f"Стресс: {symptom_entry.stress_level}/10. Состояние: {symptom_entry.body_state}. "
        f"Заметки: {symptom_entry.notes}. Еда: {symptom_entry.food_notes}. "
        f"Лекарства: {symptom_entry.medications_taken}. "
        "Назови возможные триггеры и дай краткие рекомендации."
        "У тебя есть лимит по слова 100 слов которые ты мне можешь сказать так что вложись максимально кратко но не меньше 50"
        "Отвечай строго в формате Markdown. Используй заголовки второго уровня (##) для разделов и маркированные списки для рекомендаций."
    )
    api_key = os.getenv("API_AI_KEY")

    try:
        # Настраиваем клиент Gemini
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={'http_options': {'timeout': 60000}}
        )
        html_output = markdown.markdown(response.text)
        return html_output
    except Exception as e:
        print(f"Ошибка ИИ: {e}")