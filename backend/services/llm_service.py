import os
import random

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Simple transliteration map from Uzbek Latin to Cyrillic
_LATIN_TO_CYRILLIC = {
    'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х', 'i': 'и', 'j': 'ж', 'k': 'к',
    'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
    'v': 'в', 'x': 'х', 'y': 'й', 'z': 'з', 'sh': 'ш', 'ch': 'ч', 'ng': 'нг', "'": "ъ",
    'A': 'А', 'B': 'Б', 'D': 'Д', 'E': 'Е', 'F': 'Ф', 'G': 'Г', 'H': 'Х', 'I': 'И', 'J': 'Ж', 'K': 'К',
    'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П', 'Q': 'Қ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
    'V': 'В', 'X': 'Х', 'Y': 'Й', 'Z': 'З', 'Sh': 'Ш', 'Ch': 'Ч', 'Ng': 'НГ'
}

def transliterate_to_cyrillic(text: str) -> str:
    """Very basic transliteration from Latin Uzbek to Cyrillic.
    Handles digraphs 'sh', 'ch', 'ng' before single letters.
    """
    result = ''
    i = 0
    while i < len(text):
        # Check digraphs first
        if i + 1 < len(text) and text[i:i+2].lower() in ('sh', 'ch', 'ng'):
            dig = text[i:i+2]
            result += _LATIN_TO_CYRILLIC.get(dig, dig)
            i += 2
            continue
        ch = text[i]
        result += _LATIN_TO_CYRILLIC.get(ch, ch)
        i += 1
    return result

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.provider = os.getenv("LLM_PROVIDER")  # openai or gemini
        self.client = None
        self.model = None
        if self.provider == "openai" and self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "gemini" and self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.client = None
            print("Warning: LLM API Key not found or provider not configured. Using mock responses.")

        # Pool of varied follow‑up phrases (Uzbek Latin)
        self.follow_up_phrases = [
            "Boshqa savolingiz bormi?",
            "Yana qanday ma'lumot kerak?",
            "Qo'shimcha savollaringiz bormi?",
            "Yana biror narsa bilmoqchimisiz?",
            "Boshqa biror narsa haqida so'ramoqchimisiz?",
            "Yana qanday yordam bera olaman?",
            "Qo'shimcha ma'lumot kerakmi?",
            "Boshqa biror savolingiz bo'lsa ayting."
        ]


    def _clean_text(self, text: str) -> str:
        """Remove markdown symbols and ensure clean text, including hyphens and dash characters."""
        # Remove bold/italic markers
        text = text.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
        # Remove headers
        text = text.replace('###', '').replace('##', '').replace('#', '')
        # Remove list markers, hyphens and dash characters
        text = text.replace('- ', '').replace('• ', '').replace('-', '').replace('–', '').replace('—', '')
        return text.strip()

    def _post_process(self, response: str) -> str:
        """Clean text without adding follow‑up phrases."""
        # Clean markdown first
        response = self._clean_text(response)

        lowered = response.lower().strip()
        if lowered.endswith('?'):
            return response
        farewells = ['xayr', 'hayr', 'bye', "ko'rishguncha"]
        thanks = ['rahmat', 'raxmat', 'tashakkur']
        if any(word in lowered for word in farewells + thanks):
            return response
        # No follow‑up phrase added to keep answers concise
        return response

    def get_response(self, prompt: str, context: str = "", conversation_history: list = None, version: int = 1) -> dict:
        """Generate LLM response and optionally transliterate for version 2.
        Returns a dict with 'text' and optional 'cyrillic' fields.
        """
        # ---------- Farewell / Thanks detection ----------
        prompt_lower = prompt.lower().strip()
        farewell_indicators = ['xayr', 'hayr', 'bye', 'alvido', "ko'rishguncha"]
        gratitude_words = ['rahmat', 'raxmat', 'tashakkur']
        negative_responses = ["yo'q", "yoq", "kerak emas", "shart emas"]
        is_short = len(prompt.split()) <= 4
        has_farewell = any(word in prompt_lower for word in farewell_indicators)
        has_thanks = any(word in prompt_lower for word in gratitude_words)
        has_no = any(word in prompt_lower for word in negative_responses)
        
        if is_short and (has_thanks or (has_no and '?' not in prompt)):
            text_response = "Xayr! Murojaat qilganingiz uchun rahmat. Omad tilayman! 😊"
            result = {"text": text_response}
            if version == 2:
                result["cyrillic"] = transliterate_to_cyrillic(text_response)
            return result
            
        if has_farewell:
            text_response = "Siz bilan gaplashganimdan xursand bo'ldim. Xayr! 😊"
            result = {"text": text_response}
            if version == 2:
                result["cyrillic"] = transliterate_to_cyrillic(text_response)
            return result

        # ---------- System prompt ----------
        system_prompt = f"""Siz Axborot Texnologiyalari va Menejment Universiteti (ATMU) bo'yicha yordamchi sun'iy intellektsiz.

QOIDALAR:
1. Faqat o'zbek tilida javob bering
2. To'liq va batafsil ma'lumot bering - qisqa javoblardan saqlaning
3. Kontekstdagi BARCHA tegishli ma'lumotlarni ishlating (manzil, telefon, fakultetlar va boshqalar)
4. Agar savol manzil haqida bo'lsa - TO'LIQ manzilni bering: viloyat, shahar, ko'cha, uy raqami, mo'ljal
5. Agar savol telefon haqida bo'lsa - barcha telefon raqamlarni ko'rsating

MUHIM - Quyidagi hollarda FAQAT javob bering, savol BERMANG:
- Agar siz savol bergan bo'lsangiz ("bormi?", "kerakmi?", "xohlaysizmi?" bilan tugagan)
- Agar foydalanuvchi "rahmat", "yo'q", yoki qisqa javob bersa

Boshqa hollarda javob oxirida TURLI xil iboralardan foydalaning:
- "Boshqa nima haqida bilmoqchisiz?"
- "Yana qanday yordam bera olaman?"
- "Qo'shimcha ma'lumot kerakmi?"
- "Fakultetlar yoki qabul haqida ham ma'lumot berayinmi?"
- "Boshqa savol bormi sizda?"

KONTEKST (barcha ma'lumotlardan foydalaning):
{context}

Esda tuting: To'liq va foydali javob bering!"""

        if not self.api_key:
            return {"text": "Kechirasiz, tizimda API kalit sozlanmagan. Iltimos, administratorga murojaat qiling."}

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        max_retries = 3
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                raw = ""
                if self.provider == "openai" and self.client:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.8,
                        max_tokens=400,
                    )
                    raw = response.choices[0].message.content
                elif self.provider == "gemini" and hasattr(self, "model"):
                    full_prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {prompt}"
                    response = self.model.generate_content(full_prompt)
                    raw = response.text
                else:
                    raw = "Kechirasiz, javob bera olmadim."

                processed = self._post_process(raw)
                result = {"text": processed}
                if version == 2:
                    # Provide Cyrillic version for TTS
                    result["cyrillic"] = transliterate_to_cyrillic(processed)
                return result

            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    return {"text": f"Xatolik yuz berdi: {str(e)}"}
        return {"text": "Kechirasiz, javob bera olmadim."}

llm_service = LLMService()
