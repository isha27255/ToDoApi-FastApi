import jwt
from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt

from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

JWT_SECRET = 'myjwtsecret'

class User(Model):
    __tablename__ = "users"

    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

# Dependency
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)


@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)



@app.get("/")
async def home(req: Request, db: Session = Depends(get_db),user: User_Pydantic = Depends(get_current_user)):
    todos = db.query(models.Todo).all()
    return {"todo_list": todos}

@app.post("/add")
def add(req: Request, title: str = Form(...), db: Session = Depends(get_db),user: User_Pydantic = Depends(get_current_user)):
    new_todo = models.Todo(title=title)
    db.add(new_todo)
    db.commit()
    return {"id":new_todo.id,"title":new_todo.title,"complete":new_todo.complete}
  
@app.get("/update/{todo_id}")
def add(req: Request, todo_id: int, db: Session = Depends(get_db),user: User_Pydantic = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete
    db.commit()
    return {"id":todo.id,"title":todo.title,"complete":todo.complete}


@app.get("/delete/{todo_id}")
def add(req: Request, todo_id: int, db: Session = Depends(get_db),user: User_Pydantic = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    deleted_todo_id = todo.id
    deleted_todo_title = todo.title
    db.delete(todo)
    db.commit()
    return {"id":deleted_todo_id,"title":deleted_todo_title}

register_tortoise(
    app, 
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)