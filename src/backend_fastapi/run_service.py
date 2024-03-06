import sys
import uvicorn
# from app import main
if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[-1] == "initdb":
        import db.initial_data as init
        init.main()
    else:
        import db.initial_data as init
        init.main()
        uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)