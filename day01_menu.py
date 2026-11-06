while True:
    print("-----------------------------------------------------")
    print("             FastAPI Guide Project Card              ")
    print("-----------------------------------------------------")
    print("1. About FastAPIGuide")
    print("2. Sample questions")
    print("3. check a topic")
    print("0. Exit")

    choice = input("Enter your choice:")

    print("\n Your choice is:", choice)

    if choice =="1":
        print("FastApiGuide is a comprehensive resource for learning FastAPI, a modern web framework for building APIs with python. ")

    elif choice =="2":
        print("sample questions are:")
        print("1. What is FastAPI?")
        print("2. How to create an API using FastAPI?") 
        print("3. How to handle requests and responses in FastAPI?")

    elif choice =="3":
        topic = input("enter the topic you want to check:").lower()
        if "api" in topic:
            print("This is a topic related to API development using FastAPI.")
        elif "request" in topic:
            print("This is a topic related to handling requests in FastAPI.")
        elif "python" in topic:
            print("This is a topic related to using Python with FastAPI.")
        elif "response" in topic:
            print("This is a topic related to handling responses in FastAPI.")
        else:
            print("sorry! topic not found in FastAPIGuide.")

    elif choice =="0":
        print("Exiting the FastAPI Guide Project Card. bye!")
        break

    else:
        print("Invalid choice, please select 1,2,3 or 0")


