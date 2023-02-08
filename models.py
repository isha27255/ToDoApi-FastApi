from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    complete = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password_hash = Column(String(128))

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)