"""Run FastAPI with uvicorn on port 9322."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9322, reload=False)
