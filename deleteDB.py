import os

# Make into a function in the future
db_file = "posts.db"

if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f"Database '{db_file}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting database file: {e}. Is the file open in another program?")
else:
    print(f"Database '{db_file}' not found.")
    
