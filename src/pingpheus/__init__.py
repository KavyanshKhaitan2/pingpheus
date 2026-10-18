import uvicorn

def main():
    # Start the Uvicorn server programmatically
    uvicorn.run("pingpheus.api:api", host="127.0.0.1", port=8000, reload=True)
    
if __name__ == "__main__":
    main()