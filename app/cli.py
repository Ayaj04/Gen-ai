
from app.records import load_records, search, count_by, get_by_id


def show_all_records():
    records = load_records()

    for index, record in enumerate(records, start=1):
        print(f"\nID: {index}")
        print(f"Title: {record['page_title']}")
        print(f"Section: {record['guide_section']}")
        print(f"Concept: {record['key_concept']}")
        print(f"Symbol: {record['main_symbol']}")
        print(f"Example: {record['example_response']}")
        print(f"Source: {record['source_url']}")


def show_search_results():
    keyword = input("Enter a keyword: ").strip()
    results = search(keyword)

    if not results:
        print("No matching records found.")
        return

    print(f"\nFound {len(results)} matching record(s):")

    for record in results:
        print(f"- {record['page_title']}")
        print(f"  {record['source_url']}")


def show_counts():
    fields = [
        "page_title",
        "guide_section",
        "key_concept",
        "main_symbol",
    ]

    print("\nAvailable fields:")
    for field in fields:
        print(f"- {field}")

    field = input("Count records by which field? ").strip()

    try:
        counts = count_by(field)
    except ValueError as error:
        print(error)
        return

    for value, count in counts.items():
        print(f"{value}: {count}")


def show_record_by_id():
    try:
        record_id = int(input("Enter record ID (1-20): "))
    except ValueError:
        print("Please enter a valid whole number.")
        return

    record = get_by_id(record_id)

    if record is None:
        print("Record ID not found.")
        return

    for field, value in record.items():
        print(f"{field}: {value}")


def main():
    while True:
        print("\n===== FastAPIGuide Record Manager =====")
        print("1. Show all records")
        print("2. Search by keyword")
        print("3. Count records by field")
        print("4. Get record by ID")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_all_records()
        elif choice == "2":
            show_search_results()
        elif choice == "3":
            show_counts()
        elif choice == "4":
            show_record_by_id()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Select 1, 2, 3, 4, or 0.")


if __name__ == "__main__":
    main()
