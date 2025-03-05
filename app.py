import sys
import re
import datetime
from pymongo import MongoClient

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

def process_input():
    """ Read and process commands from stdin """
    for line in sys.stdin:
        parts = line.strip().split(" ", 5)  # Split input into parts
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
                print("Error: Invalid post command format.", file=sys.stderr)
                continue
            blogName, userName, title, postBody, tags, timestamp = parts[1:]
            create_post(blogName, userName, title.strip('"'), postBody.strip('"'), tags.strip('"'), timestamp)

        else:
            print(f"Error: Unknown command '{command}'", file=sys.stderr)


if __name__ == "__main__":
        print("Blog Engine is running... Enter commands below:")
        process_input()

def register_user(userName: str, email: str):
    """ Register a new user. """

    # Check if useralready exists
    existing_user = users_collection.find_one({"userName": userName})
    if existing_user:
        print(f"Error: User '{userName}' already exists.", file=sys.stderr)
        return
    # Insert new user
    user = {
        "userName": userName,
        "email": email,
        "createdAt": datetime.utcnow()
    }
    users_collection.insert_one(user)
    print(f"User '{userName}' registered successfully.")

# def create_user(userName ):
#     """Insert a new user into MongoDB """
#     user = {
#         "userName": userName,
#     }
#     return user.insert_one(user).inserted_id #Returns the _id(userId)

#Each post has a one-to-many relationship with the post comments
def generate_permalink(blogName: str, title:str):
    #generate a permalink by replacing non-alphanumeric characters with underscores
    return f"{blogName}.{re.sub(r'[^0-9a-zA-Z]+', '_', title)}"


def create_post(blogName, userName: str, title: str, postBody:str, tags: list):
    """Validate and insert a new blog post into MongoDB. """
    if not db.users.find_one({"_id": user}):
        print("Error: User does not exist.")
        return

    # user = db.users.find_one({"userName": userName})
    # if not user:
    #     print(f"Error: User '{userName}' does not exist.")
    #     return
    # user_id = user["_id"] #Extract the objectID

    #Ensure tags are a list
    if isinstance(tags, str):
        tags = tags.split(",") if tags else []

    #Insert a new blog psot into MongoDB with an empty comments  array
    permalink = generate_permalink(blogName, title)
    post = {
        "blogName": blogName,
        "userName": userName,
        "title": title,
        "postBody": postBody,
        "tags": tags,
        "timestamp": datetime.utcnow(),
        "permalink": permalink,
        "comments": []  # Embedded list of comments
    } 
    db.posts.insert_one(post)
    print(f"Post added: {title} ({permalink})")

def add_comment(permalink, userName: str, commentBody: str):
    """Validate and add a comment to an existing post. """
    post = posts_collection.find_one({"permalink": permalink})
    if not post:
        print(f"Error: post with permalink '{permalink}' not found")
        return

    # #Find the userID from UserName
    # user = users_collection.find_one({"userName": userName})
    # if not user:
    #     print(f"Error: User '{userName}' does not exist.")
    #     return

    # user_id = user["_id"] #Extract the ObjectID

    #Generate comment permalink using timestamp
    comment_permalink = datetime.utcnow().isoformat()

    #Add a comment to an existing post by embedding it in the comment array
    comment = {
        "userName": userName,
        "commentBody": commentBody,
        "timestamp": datetime.utcnow()

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
        """Display all posts in a blog """
        posts = posts_collection.find({"blogName": blogName})
        for post in posts:
            print(f"\nTitle: {post['title']}")
            print(f"User: {post['userName']}")
            print(f"Tags: {','.join(post['tags']) if post['tags'] else 'None'}")
            print(f"Timestamp: {post['timestamp']}")
            print(f"Permalink: {post['permalink']}")
            print(f"Body:\n{post['postBody']}\n")

            #Display comments
            for comment in post.get("comments", []):
                print(f"\tComment by {comment['userName']}: {comment['commentBody']} (Timestamp): {comment['timestamp']})")



    #Search for a string in posts/comments
    def find_in_blog(blogName, searchString):
        """Search for a string in blog posts and comments """
        results = posts_collection.find(
            {"blogName": blogName, "$or":[
                {"postBody": {"$regex": searchString, "$options": "i"}},
                {"comments.commentBody": {"$regex": searchString, "$options": "i"}}
            ]}
        )

        for post in results:
            print(f"\nFound in: {post['title']} by {post['userName']}")
            print(f"Body: {post['postBody']}")
            for comment in post.get("comments", []):
                if searchString.lower() in comment["commentBody"].lower():
                    print(f"\tComment by {comment['userName']}: {comment['commentBody']}")


