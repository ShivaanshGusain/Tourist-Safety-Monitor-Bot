from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TestData(BaseModel):
    name: str
    value: int

@app.get("/")
def root():
    return {"message": "API is working", "port": 8002}

@app.post("/test")
def test_post(data: TestData):
    return {"received": data.dict()}

@app.get("/test")
def test_get():
    return {"method": "GET works"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
