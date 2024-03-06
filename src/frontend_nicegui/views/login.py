from nicegui import app, ui
from pathlib import Path

from store.action import login_access
def verify_user(username: str, password: str) -> bool:
    status,response_content = login_access(username,password)
    if status:
        access_token = response_content.get("access_token","")
        app.storage.user["access_token"] = access_token
        ui.open("/")
    return username == "admin" and password == "password"

def login(username: str, password: str):
    if verify_user(username, password):
        ui.notify('登录成功，跳转到首页', level='success')
    else:
        ui.notify('登录失败，请检查用户名和密码', level='error')

# 将 CSS 添加到 UI 中
def show_login_form():
    with ui.card().classes('max-w-lg mx-auto mt-20 bg-white bg-opacity-80 shadow-lg rounded-lg p-8'):
        ui.label('用户登录').classes('text-2xl font-bold mb-4 text-center')
        username_input = ui.input(label='用户名', placeholder='请输入您的用户名').classes('mb-4')
        password_input = ui.input(label='密码', placeholder='请输入您的密码').classes('mb-4')
        login_button = ui.button('登录', on_click=lambda: login(username_input.value, password_input.value))
        login_button.classes('w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline')


if __name__ in {"__main__", "__mp_main__"}:
    # 启动UI服务器
    ui.run(port=8088)
