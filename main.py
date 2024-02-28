import uvicorn
import sys
# from app import main
if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[1] == "initdb":
        import app.db.initial_data as init
        init.main()
    else:
        uvicorn.run("app.application:app",port=8000,reload=True)