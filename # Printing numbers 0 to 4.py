# 1. We set a variable to control the loop
user_choice = "" 

# 2. We use '!=' (Not Equal) to keep the loop running
# as long as the user hasn't typed 'quit'
while user_choice != "quit":
    user_choice = input("Enter a task (or type 'quit' to exit): ")
    
    if user_choice == "quit":
        print("Exiting program...")
        # We don't even need 'break' here because the 'while' 
        # condition will become False on the next check!
    else:
        print(f"Adding task: {user_choice}")