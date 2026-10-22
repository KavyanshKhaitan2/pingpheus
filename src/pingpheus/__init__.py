import sys

import uvicorn


def run_dev():
    uvicorn.run("pingpheus.api:api", host="127.0.0.1", port=8000, reload=True)


def main():
    if len(sys.argv) < 2:
        print("No argument found!\n")
        print("List of commands:")
        print("- dev: Start development server")
        return

    if sys.argv[1] == 'dev':
        run_dev()
    
if __name__ == "__main__":
    main()
