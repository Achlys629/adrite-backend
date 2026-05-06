from fastapi import FastAPI
app=FastAPI()

@app.get("/")
def root():
    return{"messgae":"adrite backend is running"}