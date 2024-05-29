from fastapi import FastAPI, Depends, HTTPException, Form, Request
from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./fastapi_poll.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


# Database model
class Poll(Base):
    __tablename__ = "poll"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    age = Column(Integer)
    city = Column(String)
    country = Column(String)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for request data
class PollCreate(BaseModel):
    username: str
    age: int
    city: str
    country: str


# Pydantic model for response data
class PollResponse(BaseModel):
    id: int
    username: str
    age: int
    city: str
    country: str


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# API endpoint to create an item
@app.post("/poll/", response_model=PollResponse)
async def create_record(record: PollCreate, db: Session = Depends(get_db)):
    db_record = Poll(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# API endpoint to read an item by ID
@app.get("/poll/{record_id}", response_model=PollResponse)
async def read_record(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(Poll).filter(Poll.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_record


@app.get("/", response_class=HTMLResponse, name="index")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/poll", response_class=HTMLResponse, name="poll")
async def read_form(request: Request):
    return templates.TemplateResponse("poll.html", {"request": request})


@app.post("/submit/", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    username: str = Form(...),
    age: int = Form(...),
    city: str = Form(...),
    country: str = Form(...),
    db: Session = Depends(get_db),
):
    db_record = Poll(username=username, age=age, city=city, country=country)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return templates.TemplateResponse(
        "results.html", {"request": request, "item": db_record}
    )


@app.get("/login", response_class=HTMLResponse, name="login")
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, name="register")
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/loaderio-12e71f86ba0e1bc3612073cdb4846861.txt", response_class=FileResponse)
async def verify_loaderio():
    return "static/loaderio-12e71f86ba0e1bc3612073cdb4846861.txt"

@app.get("/loader", response_class=HTMLResponse)
async def verify_loaderio():
    return "nie dziala"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
