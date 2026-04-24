from router import choose_model, generate_response

def main():
    while True:
        prompt = input("\nAsk something (type 'exit' to quit): ")

        if prompt.lower() == "exit":
            break

        selected_model = choose_model(prompt)
        print(f"\n🧠 Router selected model: {selected_model}")

        print("\n⏳ Generating response...\n")
        response = generate_response(prompt)

        print("📢 Response:\n")
        print(response)
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
