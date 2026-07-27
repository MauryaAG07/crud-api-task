from fastapi import FastAPI

#initializing application
app = FastAPI()

#create endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, server"}