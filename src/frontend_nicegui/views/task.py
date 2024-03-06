from pathlib import Path
import time
from nicegui import app, ui,background_tasks
from ex4nicegui import ref_computed, effect, to_ref
from ex4nicegui.reactive import rxui
from component.pick_files.client_file_picker import client_file_picker
from ex4nicegui import effect, effect_refreshable
from component.pick_files.local_file_picker import local_file_picker
from core.config import settings
# from store.action import get_tasks
from PIL import Image
from nicegui.events import GenericEventArguments,ColorPickEventArguments
from utils.tools import generate_distinct_colors

def task_data_card(dataset = None):
    name = dataset.get("name","")
    source = dataset.get("source","")
    data_type = dataset.get("data_type","")
    description = dataset.get("description","")
    created_at = dataset.get("created_at","")
    image = "resources/background.webp"
    try:
        image = dataset.get("files")[0].get("path","resources/background.webp")
    except: pass
    with ui.card().tight():
        ui.image(Image.open(Path(image))) # 应该是ui.image 访问不到中文路径，所以使用Image.open(Path(
        with ui.card_section():
            ui.label(f'{name}: 来自 {source} 的 {data_type}')
            ui.label(f'{description}')
            ui.label(f'{created_at}')

        with ui.context_menu():
            ui.menu_item('打开')
            ui.menu_item('删除')

            ui.separator()
            ui.menu_item('取消')




async def add_photos() -> None:
    if len(local_files):
        pass
    if len(upload_files):
        pass
    local_files = []
    upload_files = []

def add_task_dialog(): # 添加数据集弹窗
    def add_tag():
        tag_value = tag_unput_em.value
        if tag_value:
            if tag_value not in [item[0] for item in current_tags]:
                color_id = ((len(current_tags) + 1) % len(colors)) -1
                print(color_id)
                color = colors[color_id]
                current_tags.append([tag_value,color,"A"])
                tags_editor.refresh()
        tag_unput_em.set_value("")
    current_tags = []
    colors = generate_distinct_colors(30)
    def auto_color_lens(e):
        
        colors_list = generate_distinct_colors(len(current_tags))
        for i,color in enumerate(colors_list):
            current_tags[i][1] = color
        tag_row_editor.refresh()
    @ui.refreshable
    def tag_row_editor(row_id):
        tag_item = current_tags[row_id]
        with ui.grid(columns=4) as tag_item_row: 
            tag_name = tag_item[0]
            tag_name_em = ui.input(value=tag_name).props('standout :dense="dense"')

            with ui.input(value=tag_item[1]).props("readonly") as input_color_em:
                def update_input_color(e:ColorPickEventArguments):
                    current_tags[row_id][1] = e.color
                    # item_row = current_tags.pop(int(clear_ui._props["item_row"]))
                    input_color_em.set_value(e.color)
                    input_color_em.style(f'background-color:{e.color}')

                ui.color_picker(on_pick=update_input_color)
            input_color_em.style(f'background-color:{tag_item[1]}')
            input_color_em.update()
                # print(e.modifiers,e.key)
            def handle_key(e: GenericEventArguments):
                keys = ''
                key = str(e.args.get("key"))
                if len(key) == 1:
                    if e.args.get("ctrlKey"):
                        keys += 'Ctrl+'
                    if e.args.get("altKey"):
                        keys += 'Alt+'
                    if e.args.get("shiftKey"):
                        keys += 'Shift+'
                    keys += key.capitalize()
                    current_tags[row_id][2] = keys
                    # ui.notify(f'按下{keys}')
                    e.sender.set_value(keys)
            keyboard = ui.input("快捷键",value = tag_item[2]).props("readonly").on('keydown', handle_key)
            def clear(e):
                item_row = current_tags.pop(row_id)
                tags_editor.refresh()
            clear_ui = ui.button("删除",icon="clear",on_click=clear)
    @ui.refreshable
    def tags_editor():
        for i,tag_item in enumerate(current_tags):
            # with ui.row():
            tag_row_editor(i)
            # current_tags[i].append([tag_name_em,input_color_em,keyboard,clear_ui,])
            current_tags[i] = current_tags[i][:4]
    with ui.dialog(value=True) as add_dialog:
        async def post_add_task(): pass
        #     parameter = dict(
        #         data_nmae=data_nmae.value,
        #         data_source=data_source.value,
        #         data_type=data_type.value,
        #         data_description=data_description.value,
        #         is_client_file=True,
        #         token=f"Bearer {app.storage.user.get("access_token","")}",
        #     )
        #     app.storage.user.update(parameter)
        #     result = await client_file.run_method("uploadFiles",client_file.baseurl,parameter,timeout=60 * 30)
        #     add_dialog.close()
        with ui.card():
            with ui.grid():
                name_em = ui.input('任务名称',placeholder="简要总结").bind_value(app.storage.user, 'data_nmae')
                description_em = ui.textarea('任务说明',placeholder="为该任务需求详细说明").bind_value(app.storage.user, 'data_description')
                priority_em = ui.select(options={'Low':"低", 'Medium':"中", 'High':"高"},value="Low",label='优先级').bind_value(app.storage.user, 'priority') # “低”、“中”、“高”
                status = "Started" # 'Started', 'Annotated', 'Reviewed', 'Delivered' “已开始”、“注释”、“已审核”、“交付”
                with ui.list():
                    with ui.row():
                        tag_unput_em = ui.input('标签名称',placeholder="标签名称")
                        ui.button('添加标签', on_click=add_tag, icon='add_circle_outline')
                        ui.button('自动生成颜色', on_click=auto_color_lens, icon='color_lens')
                    with ui.list():
                        tags_editor()
                    # client_file_picker(multiple=True,on_change=upload_file)
                with ui.row():
                    ui.button('确认',icon="done_outline",on_click=post_add_task)
                    ui.button('去掉',icon="highlight_off",on_click=add_dialog.close)

def search_tasks(page =0,date_range = None,):
    date_range_ = date_range or app.storage.user.get("tasks_date_range",None)
    response_content = get_tasks(app.storage.user.get("access_token",""),page=page)
    if response_content.get("code"):
        tasks = response_content.get("data")
        app.storage.user["tasks_return_list"] = tasks
        Dataset_preview_list.refresh()

@ui.refreshable
def Dataset_preview_list():
    # tasks_return = tasks or tasks_return
    tasks_return:list = app.storage.user.get("tasks_return_list",[])
    tasks_return_list_page:int = app.storage.user.get("tasks_return_list_page",1)
    count = 15
    with ui.grid(columns=8): 
        tasks_return_ = tasks_return[tasks_return_list_page - 1:count]
        for dataset in tasks_return_:
            task_data_card(dataset)
                
    ui.separator()
    
    # with ui.element("q-footer").classes('q-pa-md'):
    with ui.row():
        ui.pagination(1,int(len(tasks_return) / count) + 1, 
                      direction_links=True,on_change=lambda v: app.storage.user.update({"tasks_return_list_page": v}))\
            .props('''max-pages=5 ellipses=true 
      boundary-links
      icon-first="skip_previous"
      icon-last="skip_next"
      icon-prev="fast_rewind"
      icon-next="fast_forward"
    ''').style("margin-top: auto")
        # Dataset_preview_page_numbers = ui.toggle([1], value=1).bind_value(app.storage.user, 'tasks_page_number')
        

# def task_preview_ui(router):
def tasks_ui(router):
    with ui.splitter(horizontal=True) as splitter:
        with ui.list().classes('w-full border'):
            # def handle_key(e: KeyEventArguments):
            #     print(e)
            #     ui.notify(f'按下{e.modifiers} {e.key} ')
            #     print(e.modifiers,e.key)
            # ui.input("").on('keydown.enter', handle_key)
            with ui.row():
                date_range = ui.input(label='时间', placeholder='数据上传时间',)
                with date_range.add_slot('prepend'):
                    def on_change(e):
                        if e.value is not None:
                            if isinstance(e.value, str):
                                from_date = to_date = e.value
                            elif isinstance(e.value, dict):
                                from_date = e.value.get("from")
                                to_date = e.value.get("to")

                            print(from_date,to_date,from_date>to_date)
                            
                            date1 = time.mktime(time.strptime(from_date, '%Y-%m-%d'))
                            date2 = time.mktime(time.strptime(to_date, '%Y-%m-%d'))
                            # 确保from_date  在 to_date 之前，否则交换
                            if date1 < date2:
                                pass
                            elif date1 > date2:
                                to_date_ = from_date
                                from_date = to_date
                                to_date = to_date_
                            else:
                                pass
                            date_range.set_value(f"{from_date} ~ {to_date}")
                    def toggle_type(_): pass
                    with ui.menu() as menu:
                        with ui.column():
                            ui.date(value='2023-01-01', on_change=on_change).props('range today-btn')
                    ui.icon('date_range').classes('cursor-pointer').props('round color="primary"').on('click', toggle_type)
                    # date_range.on('click', toggle_type)
                ui.button('搜索',icon="search",on_click=lambda e:search_tasks(date_range = date_range.value))
                ui.button('添加',icon="add_task",on_click=add_task_dialog)
            Dataset_preview_list()