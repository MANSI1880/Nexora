from fastapi import FastAPI

app = FastAPI(title="Nexora API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Nexora API"}
