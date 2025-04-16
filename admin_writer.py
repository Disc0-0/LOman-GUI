import json
import time
import os


def write_to_json(message, folder):
    """Helper function to write a message to a JSON file."""
    final_path = os.path.join(folder, 'Mist', 'Content', 'admin.json')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    
    # Write the message to the file
    with open(final_path, 'w') as file:
        json.dump({"Message": message}, file)


def write(message, folder):
    write_to_json(message, folder)
    time.sleep(11)
    write_to_json("", folder)


def main():
    with open("config.json", 'r') as file:
        config = json.load(file)

    user_input = input("Enter your message: ")
    write(user_input, config["folder_path"])
    main()


if __name__ == "__main__":
    main()