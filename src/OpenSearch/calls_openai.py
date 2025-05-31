import openai
from dotenv import load_dotenv
import os
load_dotenv()

def create_openai_prompt(results, index_source_fields):
    context = ""
    for hit in results:
        if "highlight" in hit:
            highlighted_texts = []
            for values in hit["highlight"].values():
                highlighted_texts.extend(values)
            context += "\n --- \n".join(highlighted_texts)
        else:
            context_fields = index_source_fields.get(hit["_index"])
            for source_field in context_fields:
                hit_context = hit["_source"][source_field]
                if hit_context:
                    context += f"{source_field}: {hit_context}\n"
    prompt = f"""
    Instruções:
    
    - Você é um assistente virtual especializado no santos futebol clube.
    - Use somente as informações do seu contexto para responder as perguntas.
    - Se você não souber a resposta, apenas diga que não sabe, não tente supor coisas.

    Context:
    {context}
    """
    return prompt

def generate_openai_completion(user_prompt, question):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": question},
        ]
    )

    return response.choices[0].message.content