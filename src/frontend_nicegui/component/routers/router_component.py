import asyncio
from concurrent.futures import Future
import inspect
from typing import Callable, Dict, Union

from nicegui import app, background_tasks, helpers, ui,Client,context

# from api.user.permission import check_token
from loguru import logger

# from frontend_nicegui.middleware.permission import unrestricted_page_routes
from pathlib import Path

class RouterFrame(ui.element, component='router_frame.js'):
    pass

def menu(router,label,icon,open):
    def click():
        router.open(open)
    with ui.item(on_click=click).props('clickable v-ripple') as item:
    # with ui.element("q-list").on("click",lambda:router.open(open)).props('clickable v-ripple'):
        with ui.item_section().props("avatar"):
        # with ui.element("q-item").props("avatar"):
            ui.icon(icon)
        # with ui.element("q-item"):
        with ui.item_section():
            ui.label(label)
    # with ui.menu_item(on_click=lambda:router.open(open),auto_close=False) as btn:
    #     ui.icon(icon, size='24px')
    #     ui.label(label).style("padding-left: 0px;width: 80px;display: grid; place-items: center;")

class Router():

    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.content: ui.element = None
        self.background: str = None
        self.layout: bool = False

    def add(self, path: str,func: Callable = None,text=None,icon="home",):
        self.routes[path] = {"builder":func,"path":path,"text":text,"icon":icon,}
        if func == None:
            def decorator(func: Callable):
                return func
            return decorator
        else:
            return func
        
    def init_layout(self):
        if self.layout: return
        header = ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between')
        left_drawer = ui.left_drawer()
        left_drawer.classes("$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'")
        left_drawer.props(':mini=true  :width="200" :breakpoint="500" show-if-above bordered')
        def mouseover_out(props=":mini=false"):
            # left_drawer.props(props)
            left_drawer._props["mini"] = not left_drawer._props.get("mini")
            left_drawer.update()
        
        # left_drawer.on('mousemove', lambda: left_drawer.props(":mini=false"))
        # left_drawer.on("mouseout", lambda: left_drawer.props(":mini=true"))
        # left_drawer.on("click", lambda: left_drawer.props(":mini=false"))
        with left_drawer:
            # with ui.scroll_area().classes("fit").props(':horizontal-thumb-style="{ opacity: 0 }"'): # 
            left_drawer.on('mousemove', lambda: left_drawer.props(":mini=false"))
            left_drawer.on("mouseout", lambda: left_drawer.props(":mini=true"))
            with ui.element("q-scroll-area").classes("fit").props(':horizontal-thumb-style="{ opacity: 0 }"') as scroll:
                scroll.on('mousemove', lambda: left_drawer.props(":mini=false"))
                scroll.on("mouseout", lambda: left_drawer.props(":mini=true"))
                with ui.element("q-list").props("padding"):
                    for k, v in self.routes.items():
                        icon = v["icon"]
                        text = v["text"]
                        path = v["path"]
                        builder = v["builder"]
                        menu(self,text,icon,path)
            # with ui.element("div").classes("q-mini-drawer-hide absolute").style("top: 15px; right: -17px"):
            #     ui.button(on_click=lambda: left_drawer.props(":mini=true"),icon="chevron_left").props('dense round unelevated color="accent" ')
        with header:
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white round dense')
        # with ui.footer().style('background-color: #3874c8 height'):
        #     ui.label('FOOTER')
        self.layout = True

    def berify_builder_transmission(self,builder):
        argspec = inspect.getfullargspec(builder)
        args = argspec.args
        annotations = argspec.annotations
        set1 = set(args)
        set2 = set(argspec.annotations.keys())
        args_ = list(set1 - set2)
        parameter = dict(zip(args_, "" * len(args_)))
        for name in args_:
            if "content" == name:
                parameter[name] = self.content
            elif "router" == name:
                parameter[name] = self
            elif "client" == name:
                parameter[name] = context.get_client()
            else:
                parameter[name] = None
        for key,value in annotations.items():
            if key not in parameter and key in args:
                if value == Client:
                    parameter[key] = context.get_client()
                elif value == Router:
                    parameter[key] = self
                else:
                    parameter[key] = None
        builder(**parameter)

    def open(self, target: Union[Callable, str]) -> None:
        if isinstance(target, str):
            target_dict = self.routes[target]
        else:
            target_dict = {v["builder"]: v for k, v in self.routes.items()}[target]
        path = target_dict["path"]
        builder = target_dict["builder"]
        async def build() -> None:
            with self.content:
                await context.get_client().connected()
                ui.run_javascript(f'''
                    if (window.location.pathname !== "{path}") {{
                        history.pushState({{page: "{path}"}}, "", "{path}");
                    }}
                ''')
                
                result = self.berify_builder_transmission(builder)
                if helpers.is_coroutine_function(builder):
                    await result
        # if path not in ['/login'] and True: # 不进行登录直接使用
            # if not check_token_access(app.storage.user.get('access_token', "")):
            #     app.storage.user['referrer_path'] = path  # remember where the user wanted to go
            #     self.content.clear()
            #     self.open('/login')
            #     return
        if path not in ['/login']:
            self.init_layout()
        self.content.clear()
        background_tasks.create(build())

    def frame(self) -> ui.element:
        self.content = RouterFrame().on('open', lambda e: self.open(e.args))
        return self.content
