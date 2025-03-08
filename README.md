
# Blog Engine - MongoDB Blogging App

## Overview

This project is a command-line blog engine built with **Python** and  **MongoDB** . It processes user registrations, blog posts, comments, and deletions through standard input (stdin).

## Features

* Register users
* Create blog posts with unique permalinks
* Add comments to posts
* Search posts and comments for keywords
* Delete posts and comments
* Display blog posts and associated comments

## Prerequisites

Ensure you have the following installed:

* Python 3.x
* MongoDB
* `pip` (Python package manager)
* `mongosh` (MongoDB shell)

## Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd blog-engine-mongodb
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start MongoDB (if not already running):
   ```sh
   mongod --dbpath <path-to-your-database-directory>
   ```
5. Run the blog engine:
   ```sh
   python3 app.py
   ```

## Usage

To interact with the blog engine, enter commands in the following format:

### Register a User

I added an email to distinguish users

```sh
register <userName> <email>
```

Example:

```sh
register Alice alice@example.com
```

### Create a Blog Post

```sh
post <blogName> <userName> <title> <postBody> <tags> <timestamp>
```

Example:

```sh
post tech_blog Alice "MongoDB Tips" "This is a test post." "database,mongodb" 2025-03-07T12:00:00
```

### Add a Comment

```sh
comment <blogName> <permalink> <userName> <commentBody> <timestamp>
```

Example:

```sh
comment tech_blog tech_blog.MongoDB_Tips Bob "Great post, Alice!" 2025-03-07T12:30:00
```

### Search for a String in Posts and Comments

```sh
find <blogName> <searchString>
```

Example:

```sh
find tech_blog "MongoDB"
```

### Delete a Post or Comment

```sh
delete <blogName> <permalink> <userName> <timestamp>
```

Example:

```sh
delete tech_blog tech_blog.MongoDB_Tips Bob 2025-03-07T12:50:00
```

### Show Blog Posts and Comments

```sh
show <blogName>
```

Example:

```sh
show tech_blog
```

### Exit the Blog Engine

```sh
exit
```

## Running MongoDB Shell (`mongosh`)

To interact with your MongoDB database, follow these steps:

1. **Start MongoDB** (if not already running):
   ```sh
   mongod --dbpath <path-to-your-database-directory>
   ```
2. **Open MongoDB Shell (`mongosh`)** :

```sh
   mongosh
```

1. **Verify Your Database (`blogDB`) Exists** :

```sh
   show dbs
```

1. **Switch to Your Blog Database** :

```sh
   use blogDB
```

1. **View Collections (Tables) in Your Database** :

```sh
   show collections
```

1. **Query Documents in `posts` Collection** :

```sh
   db.posts.find().pretty()
```

1. **Query Users in `users` Collection** :

```sh
   db.users.find().pretty()
```

1. **Exit `mongosh`** :

```sh
   exit
```

## Testing

To verify correct operation, run test files:

```sh
python3 app.py < testfile1.in > grader.testfile1.out 2>&1
```

Then compare the output:

```sh
diff grader.testfile1.out testfile1.out
```

## Configuration

Use a `config.ini` file to hold your MongoDB login credentials if necessary:

```ini
[database]
uri = mongodb://localhost:27017
```

## License

This project is open-source and available under the MIT License.
