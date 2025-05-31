from configuration import OpenSearchIterations
from calls_openai import create_openai_prompt, generate_openai_completion

if __name__ == "__main__":
    op = OpenSearchIterations()
    question = "Qual é a missão do Santos Futebol Clube?"
    elasticsearch_results = op.get_elasticsearch_results(question)
    context_prompt = create_openai_prompt(elasticsearch_results, op.index_source_fields)
    openai_completion = generate_openai_completion(context_prompt, question)
    print(openai_completion)