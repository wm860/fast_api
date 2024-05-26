from fastapi import FastAPI
import uvicorn
import random

app = FastAPI()

@app.get("/")
async def root():
   return {"message": "Hello World ssss", 'data': 'data from server', 'random': random.randint(1, 100)}

@app.get("/random")
async def random_number():
    return random.randint(1, 100)

 if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", reload=True)