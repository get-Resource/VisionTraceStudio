import sys
if __name__ in {"__main__", "__mp_main__"}:
    if sys.argv[-1] == "initdb":
        import app.db.initial_data as init
        init.main()
    else:
        from app.nicegui.main import gui_run
        from app.application import *
        gui_run()