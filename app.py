import sys
import re
from datetime import datetime, timezone
from pymongo import MongoClient
import shlex

#connect to mongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["blogDB"]
posts_collection = db["posts"]
users_collection = db["users"]

# Define `register_user()` before `process_input()`
def register_user(userName: str, email: str):
    """ Register a new user. """
    
    # Check if user already exists
    existing_user = users_collection.find_one({"userName": userName})
    if existing_user:
        print(f"Error: User '{userName}' already exists.", file=sys.stderr)
        return

    # Insert new user
    user = {
        "userName": userName,
        "email": email,
    }
    users_collection.insert_one(user)
    print(f"User '{userName}' registered successfully.")


#Each post has a one-to-many relationship with the post comments
def generate_permalink(blogName: str, title:str):
    #generate a permalink by replacing non-alphanumeric characters with underscores
    return f"{blogName}.{re.sub(r'[^0-9a-zA-Z]+', '_', title)}"


def create_post(blogName, userName, title, postBody, tags, timestamp):
    """Validate and insert a new blog post into MongoDB."""
    
    # Check if the user exists
    user = db.users.find_one({"userName": userName})
    if not user:
        print(f"Error: User '{userName}' does not exist.", file=sys.stderr)
        return

    if db.posts.find_one({"title": title, "blogName": blogName}):
        print(f"Error: Post titled '{title}' already exists in blog '{blogName}'.", file=sys.stderr)
        return

    
    # Drop (delete) an existing post if it already exists
    existing_post = db.posts.find_one({"title": title, "blogName": blogName})
    if existing_post:
        db.posts.delete_one({"_id": existing_post["_id"]})  # Drop the existing post
        print(f"Existing post '{title}' in blog '{blogName}' was deleted and will be replaced.")


    # Convert timestamp from string to datetime
    try:
        timestamp = datetime.now(timezone.utc)
    except ValueError:
        print(f"Error: Invalid timestamp format '{timestamp}'. Expected ISO format (YYYY-MM-DDTHH:MM:SS).", file=sys.stderr)
        return

    # Ensure tags are stored as a list
    if isinstance(tags, str):
        tags = tags.split(",") if tags else []

    # Create the post document
    post = {
        "blogName": blogName,
        "userName": userName,
        "title": title,
        "postBody": postBody,
        "tags": tags,
        "timestamp": timestamp,
        "permalink": generate_permalink(blogName, title),
        "comments": []
    }

    # # DEBUG: Print before inserting
    # print(f"DEBUG: Inserting post - {post}")

    # Insert into MongoDB
    result = db.posts.insert_one(post)
    if result.acknowledged:
        print(f"Post added: {title}")
    else:
        print("post insertion failed!", file=sys.stderr)


def add_comment(permalink, userName: str, commentBody: str, timestamp: str):
    """Validate and add a comment to an existing post. """
    post = posts_collection.find_one({"permalink": permalink})
    if not post:
        print(f"Error: post with permalink '{permalink}' not found")
        return

    
    #Generate comment permalink using timestamp
    comment_permalink = datetime.now(timezone.utc).isoformat()

    #Add a comment to an existing post by embedding it in the comment array
    comment = {
        "userName": userName,
        "commentBody": commentBody,
        "timestamp": datetime.now(timezone.utc)

    }


    result = posts_collection.update_one(
        {"permalink": permalink},
        {"$push": {"comments": comment}}
    )

    if result.modified_count > 0:
        print(f"Comment added by {userName}. New comment permalink: {comment_permalink}")
    else:
        print(f"Error: Could not add comment to '{permalink}'.", file=sys.stderr)

    
#Show all posts in a blog
def show_blog(blogName):
    """Display all posts in a blog."""

    posts = posts_collection.find({"blogName": blogName})
    printed_header = False  # Track if header is printed
    seen_permalinks = set() #Track printed posts

    if not printed_header:
        print(f"\nin {blogName.capitalize()}:\n")
        printed_header = True

    for post in posts:
        # Ensure we only print unique posts
        if post["permalink"] in seen_permalinks:
            continue  # Skip duplicate post
        seen_permalinks.add(post["permalink"])  # Add to seen set

        

        print("- - - -")
        print(f"title: {post['title']}")
        print(f"userName: {post['userName']}")
        print(f"tags: {', '.join(post['tags'])}" if post['tags'] else "tags: None")
        print(f"timestamp: {post['timestamp'].isoformat() if isinstance(post['timestamp'], datetime) else post['timestamp']}")
        print(f"permalink: {post['permalink']}")
        print("body:")
        print(f"    {post['postBody']}")

        for comment in post.get("comments", []):
            print(f"\n    userName:, {comment['userName']}")
            print(f"     permalink: {comment['timestamp']}")
            print("      comment:")
            print(f"        {comment['commentBody']}")

   

def find_in_blog(blogName, searchString):
    """Search for a string in blog posts and comments."""
    # Query posts in the given blog that contain the searchString
    results = posts_collection.find({
        "blogName": blogName,
        "$or": [
            {"postBody": {"$regex": f"{searchString}", "$options": "i"}},
            {"tags": searchString},
            {"comments.commentBody": {"$regex": f"{searchString}", "$options": "i"}}
        ]
    })


    found_results = False  # Track if results were found
    print(f"\nin {blogName.capitalize()}:\n")  # Print blog name

    # Loop through matching posts
    for post in results:
        found_results = True  # Mark results found

        # Print a separator
        print("- - - -")

        # Ensure timestamp is printed correctly
        timestamp = post["timestamp"]
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)  # Convert string to datetime
                print(f"timestamp: {timestamp.isoformat()}")
            except ValueError:
                print(f"timestamp: {timestamp}")  # If conversion fails, print the string as-is
        else:
            print(f"timestamp: {timestamp.isoformat()}")  # If it's already a datetime, print it normally

        # Print post details if the search is found in body or tags
        if searchString in post["postBody"] or searchString in post.get("tags", []):
            print(f"title: {post['title']}")
            print(f"userName: {post['userName']}")
            
            # Handle tags properly
            if post.get("tags"):
                print(f"tags: {', '.join(post['tags'])}")
            
            # print(f"timestamp: {post['timestamp'].isoformat()}")
            print(f"permalink: {post['permalink']}")
            print(f"body: {post['postBody']}\n")

        # Handle comments properly
        found_comment = False  # Track if the search string was found in a comment

        for comment in post.get("comments", []):
            if searchString.lower() in comment["commentBody"].lower():
                found_comment = True  # Found a match in a comment
                print(f"Found in comment by {comment['userName']}: {comment['commentBody']}")  # No indentation

        # If the search string was not found in comments but the post has comments, indent them
        if not found_comment:
            for comment in post.get("comments", []):
                print(f"\tComment by {comment['userName']}: {comment['commentBody']}")  # Indented format


    # If no results were found, print an error
    if not found_results:
        print(f"No matches found for '{searchString}' in blog '{blogName}'.", file=sys.stderr)



def delete_entry(blogName, permalink, userName, timestamp):
    """Replace a post or comment with 'deleted by {userName}' message."""
    
    # Find the post containing the given permalink
    post = posts_collection.find_one({"permalink": permalink})

    if not post:
        print(f"Error: No post or comment found with permalink '{permalink}' in blog '{blogName}'.", file=sys.stderr)
        return

    # If the permalink matches a post, replace the post body
    if post["permalink"] == permalink:
        result = posts_collection.update_one(
            {"permalink": permalink},
            {"$set": {
                "postBody": f"deleted by {userName}",
                "timestamp": datetime.utcnow()
            }}
        )

        if result.modified_count > 0:
            print(f"Post '{permalink}' deleted by {userName}.")
        else:
            print(f"Error: Could not delete post '{permalink}'.", file=sys.stderr)
        return

    # If the permalink is in the comments, update the comment instead
    result = posts_collection.update_one(
        {"comments.permalink": permalink},
        {"$set": {
            "comments.$.commentBody": f"deleted by {userName}",
            "comments.$.timestamp": datetime.now(timezone.utc)
        }}
    )

    if result.modified_count > 0:
        print(f"Comment '{permalink}' deleted by {userName}.")
    else:
        print(f"Error: Could not delete comment '{permalink}'.", file=sys.stderr)

def process_input():
    """ Read and process commands from stdin """
    for line in sys.stdin:
        # parts = line.strip().split(" ", 5)  # Split input into parts
        parts = shlex.split(line.strip())
        if not parts:
            continue

        command = parts[0].lower()  # Convert command to lowercase

        if command == "register":
            if len(parts) < 3:
                print("Error: Invalid register command format.", file=sys.stderr)
                continue
            userName, email = parts[1], parts[2]
            register_user(userName, email)  # Call function to register user

        elif command == "post":
            if len(parts) < 6:
                print("Error: Invalid post command format.Expected 6 fields", file=sys.stderr)
                continue

            blogName, userName, title, postBody, tags, timestamp = parts[1:]
            create_post(blogName, userName, title.strip('"'), postBody.strip('"'), tags.strip('"'), timestamp)
            
        elif command == "delete":
            if len(parts) < 4:
                print("Error: Invalid delete command format.", file=sys.stderr)
                continue
            blogName, permalink, userName, timestamp = parts[1:]
            delete_entry(blogName, permalink, userName, timestamp)

        elif command == "find":
            if len(parts) < 3:
                print("Error: Invalid find command format.", file=sys.stderr)
                continue
            blogName, searchString = parts[1], parts[2]
            find_in_blog(blogName, searchString.strip('"'))

        elif command == "exit":
            print("Exiting blog engine...")
            break  # Stops the loop and exits cleanly

        elif command == "comment":
            if len(parts) < 5:
                print("Error: Invalid comment command format.", file=sys.stderr)
                continue
            blogName, permalink, userName, commentBody, timestamp = parts[1:]
            add_comment(permalink, userName, commentBody.strip('"'), timestamp)
        elif command == "show":
            if len(parts) < 2:
                print("Error: Invalid show command format.", file=sys.stderr)
                continue
            blogName = parts[1]
            show_blog(blogName)

        else:
            print(f"Error: Unknown command '{command}'", file=sys.stderr)



if __name__ == "__main__":
        print("Blog Engine is running... Enter commands below:")
        process_input()

