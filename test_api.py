from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is working!", "endpoints": ["/", "/test"]}

@app.get("/test")
def test():
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
