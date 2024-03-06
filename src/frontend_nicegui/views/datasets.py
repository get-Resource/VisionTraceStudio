from pathlib import Path
import time
from nicegui import app, ui,background_tasks
from ex4nicegui import ref_computed, effect, to_ref
from ex4nicegui.reactive import rxui
from component.pick_files.client_file_picker import client_file_picker
from ex4nicegui import effect, effect_refreshable
from component.pick_files.local_file_picker import local_file_picker
from core.config import settings
from store.action import get_datasets
from PIL import Image

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
local_files=[]
upload_files=[]
async def pick_file() -> None:
    global local_files,upload_files
    upload_files = []
    local_files = await local_file_picker(settings.RemoteDirectory + "/", multiple=True)
    # ui.notify(f'You chose {local_file}')

async def choose_file():
    files = await app.native.main_window.create_file_dialog(allow_multiple=True)
    for file in files:
        ui.notify(file)


async def add_photos() -> None:
    if len(local_files):
        pass
    if len(upload_files):
        pass
    local_files = []
    upload_files = []
    
def add_to_photos(): # 添加数据集弹窗
    with ui.dialog(value=True) as add_dialog:
        async def upload_files():
            parameter = dict(
                data_nmae=data_nmae.value,
                data_source=data_source.value,
                data_type=data_type.value,
                data_description=data_description.value,
                is_client_file=True,
                token=f"Bearer {app.storage.user.get("access_token","")}",
            )
            app.storage.user.update(parameter)
            result = await client_file.run_method("uploadFiles",client_file.baseurl,parameter,timeout=60 * 30)
            add_dialog.close()
        with ui.card():
            with ui.grid():
                data_nmae = ui.input('数据内容名称').bind_value(app.storage.user, 'data_nmae')
                data_source = ui.input('数据采集来源').bind_value(app.storage.user, 'data_source')
                data_type = ui.select(options=["image","video"],value="image",label='数据类型').bind_value(app.storage.user, 'data_type')
                data_description = ui.textarea('数据说明').bind_value(app.storage.user, 'data_description')
                with ui.row():
                    ui.button('在共享文件夹中选择文件', on_click=pick_file, icon='folder')
                    client_file = client_file_picker(multiple=True,label="本地目录上传",auto_upload=False)\
                        .classes('max-w-full').props("batch")
                    # client_file_picker(multiple=True,on_change=upload_file)
                with ui.row():
                    ui.button('确认',icon="done_outline",on_click=upload_files)
                    ui.button('去掉',icon="highlight_off",on_click=add_dialog.close)

def search_datasets(page =0,date_range = None,):
    date_range_ = date_range or app.storage.user.get("datasets_date_range",None)
    response_content = get_datasets(app.storage.user.get("access_token",""),page=page)
    if response_content.get("code"):
        datasets = response_content.get("data")
        app.storage.user["datasets_return_list"] = datasets
        Dataset_preview_list.refresh()

@ui.refreshable
def Dataset_preview_list():
    # datasets_return = datasets or datasets_return
    datasets_return:list = app.storage.user.get("datasets_return_list",[])
    datasets_return_list_page:int = app.storage.user.get("datasets_return_list_page",1)
    count = 15
    with ui.grid(columns=8): 
        datasets_return_ = datasets_return[datasets_return_list_page - 1:count]
        for dataset in datasets_return_:
            task_data_card(dataset)
                
    ui.separator()
    
    # with ui.element("q-footer").classes('q-pa-md'):
    with ui.row():
        ui.pagination(1,int(len(datasets_return) / count) + 1, 
                      direction_links=True,on_change=lambda v: app.storage.user.update({"datasets_return_list_page": v}))\
            .props('''max-pages=5 ellipses=true 
      boundary-links
      icon-first="skip_previous"
      icon-last="skip_next"
      icon-prev="fast_rewind"
      icon-next="fast_forward"
    ''').style("margin-top: auto")
        # Dataset_preview_page_numbers = ui.toggle([1], value=1).bind_value(app.storage.user, 'datasets_page_number')
        

# def task_preview_ui(router):
def datasets_ui(router):
    with ui.splitter(horizontal=True) as splitter:
        with ui.list().classes('w-full border'):
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
                    ui.icon('event').classes('cursor-pointer').props('round color="primary"').on('click', toggle_type)
                    # date_range.on('click', toggle_type)
                ui.button('搜索',icon="manage_search",on_click=lambda e:search_datasets(date_range = date_range.value))
                ui.button('添加',icon="add_to_photos",on_click=add_to_photos)
            Dataset_preview_list()
                # def update_options():
                #      print(len(Dataset_preview_page_numbers.options))
                #      Dataset_preview_page_numbers.options.append(len(Dataset_preview_page_numbers.options) + 1)
                #      Dataset_preview_page_numbers.update()
                # ui.timer(2.0, update_options)