# To-Do List Api using FastApi 

## Local Build Instructions

```
# Clone the repository and change the directory
git clone https://github.com/isha27255/ToDoApi-FastApi.git
cd ToDoApi-FastApi

# for virtual environment
python3 -m venv venv
source venv/bin/activate

# install the requirements
pip3 install -r requirements.txt

# run the server
uvicorn main:app --reload
```

This To-Do Application has all the basic `CRUD` functionalities

```
Create (Create a new todo item):

Route: POST /add
Input: Todo item details in request body
Output: Newly created todo item

Read (Get a list of todo items or a single todo item):

Route: GET /
Input: No Input
Output: List of todo items

Update (Update an existing todo item):

Route: PUT /update/:todo_id
Input: ID of todo item and updated todo item details in request body
Output: Updated todo item

Delete (Delete a todo item):

Route: DELETE /delete/:todo_id
Input: ID of todo item
Output: Success or error message
```
### Authentication
We have implemented OAuth2 security in our FastAPI application to ensure secure access to the Todo List API. 
