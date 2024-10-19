from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
import os
import json

os.environ["OPENAI_API_KEY"] = "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"

def docs2str(docs, title="Document"):
    """Useful utility for making chunks into context string. Optional, but useful"""
    out_str = ""
    for doc in docs:
        doc_name = getattr(doc, 'metadata', {}).get('Title', title)
        if doc_name: out_str += f"[Quote from {doc_name}] "
        out_str += getattr(doc, 'page_content', str(doc)) + "\n"
    return out_str

def flatten_dict(nested_dict):
    items = {}

    def flatten(d):
        for key, value in d.items():
            if isinstance(value, dict):
                flatten(value)
            else:
                items[key] = "None"

    flatten(nested_dict)
    return items

def parse_output(output):
    # Split the string into two parts: the key and the list of bullets
    key, bullets_string = output.split(":", 1)  # Split only at the first ':'
    
    # Strip whitespace from the key
    key = key.strip("[]").strip()
    
    # Split the bullets by commas and strip whitespace around them
    bullets = [bullet.strip("[]").strip() for bullet in bullets_string.split(",")]
    
    return key, bullets

def main():
    model = ChatOpenAI(model="gpt-4o-mini")
    with open('topics.json', 'r') as json_file:
        template_dict = json.load(json_file)

    flattened = flatten_dict(template_dict)

    #memory = ConversationBufferMemory()

    question_prompt = ChatPromptTemplate.from_template(
        "System"
        "You are a nurse. Ask a question to answer one or more of the keys with null values in this information\n{input}\n"
        "Ask the question conversationally. Limit to only ONE question! Make sure the conversation flows naturally.\n"
    )

    read_answer = ChatPromptTemplate.from_template(
        "System"
        "Read the users response: {answer}"
        "List of Keys: {keys}"
        "Give me the key from the list of keys that fits this response most and important points from the response in a list of bullet points"
        "You don't need to write complete sentences for the bullet points"
        "FOLLOW THIS FORMAT FOR THE OUTPUT! THIS IS IMPORTANT!: [Key]: [bullet 1], [bullet 2]..."
    )

    clarification_prompt = ChatPromptTemplate.from_template(
        "System"
        "Do you have additional follow up questions or need clarification from the patient on their most recent response that would be useful for the doctor to know?"
        "If you don't have any follow up questions on this topic, then return an empty string"
    )

    clar_q_prompt = clarification_prompt = ChatPromptTemplate.from_template(
        "System"
        "Context: {input}"
        
    )

    output_parser = StrOutputParser()

    question_chain = (question_prompt
                      | model
                      | output_parser
                      | RunnableLambda(lambda x: print(x))
                      | RunnableLambda(lambda _: input("Enter response: "))
                      | RunnableLambda(lambda x: {"keys": flattened.keys, "answer": x})
                      | read_answer
                      | model
                      | clarification_prompt
                      | model
                      | output_parser
                      )
    
    clarification_chain = (clar_q_prompt
                           | output_parser
                           | RunnableLambda(lambda x: input(x))
                           | clarification_prompt
                           | model
                           | output_parser
                           )

    while any(value == "None" for value in flattened.values()):
        json_str = json.dumps(flattened, indent=2)
        output = question_chain.invoke(json_str)

        while output_text != "":
            output_text = clarification_chain.invoke(output_text)
        return

if __name__ == "__main__":
    main()