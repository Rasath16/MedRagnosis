from fastapi import FastAPI

app=FastAPI()

@app.get("/health")
def healthCheck():
    return {"message":"ok"}
def main():
    print("Hello from med-ragnosis-a-retrieval-augmented-generation-platform-for-streamlined-medical-diagnosis!")


if __name__ == "__main__":
    main()
