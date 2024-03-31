import io

def user_input_await(prompt: str) -> str:
    print("\n** COPY FOLLOWING TEXT TO CHATBOT **")
    print(f"\n> {prompt}")
    print("\n** AFTER PASTING, PRESS: (ENTER), (CTRL+Z), (ENTER) TO FINISH **")
    print("\n**> PASTE YOUR RESPONSE: **\n")

    with io.StringIO() as input_text:
        input_text.write(input(""))
        input_text.seek(0)
        return input_text.read().strip()
