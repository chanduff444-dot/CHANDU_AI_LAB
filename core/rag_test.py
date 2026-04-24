from rag_engine import rag_generate

def main():
    while True:
        query = input("\nAsk something (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        print("\n⏳ Processing...\n")
        response = rag_generate(query)

        print("\n📢 Final Answer:\n")
        print(response)
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
