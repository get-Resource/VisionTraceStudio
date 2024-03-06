
import httpx

client = None
# @pytest.fixture(scope='module')
def service_client(app,base_url="",token=None):
    global client
    headers = None
    if token:
        headers = {
            'Authorization': 'Basic ' + token,
            'Content-Type': 'application/json'
        }
    # client = TestClient(app,base_url,headers=headers)
    client = httpx.Client(base_url=base_url,headers=headers)
    return client

def login_access(username,password) -> (str,dict,):
    status = False
    try:
        Auth = httpx.BasicAuth(username,password)
        Auth = dict(username=username,password=password)
        Response = client.get("/api/v1/auth/access-token",data=Auth)
        response_content = Response.json()
        status = Response.status_code == 200
        if status:
            access_token = response_content.get("access_token","")
            token_type = response_content.get("token_type","")
            # bearer
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            client.headers.update(headers)
    except Exception as e:
        response_content = dict(
            detail = [e,],
            msg = str(e),
        )
    return status,response_content

def check_token_access(access_token=None) -> bool:
    status = False
    try:
        # Auth = httpx.BasicAuth(username,password)
        headers = None
        if access_token:
            Authorization = 'Bearer ' + access_token
            headers = {
                'Authorization': Authorization,
                # 'Content-Type': 'application/json'
            }
            # if client.headers.get("Authorization") !=Authorization:
            #     client.headers.update(headers)
        Response = client.post("/api/v1/login/test-token")
        response_content = Response.json()
        status = Response.status_code == 200
    except Exception as e:
        response_content = dict(
            detail = [e,],
            msg = str(e),
        )
    return status

def get_datasets(access_token=None,dataset_id=None,page=0,page_size=15) -> list:
    status = False
    try:
        # Auth = httpx.BasicAuth(username,password)
        headers = None
        if access_token:
            Authorization = 'Bearer ' + access_token
            headers = {
                # 'Authorization': Authorization,
                'accept': 'application/json'
            }
            if client.headers.get("Authorization") !=Authorization:
                client.headers.update(headers)
        Response = client.get("/api/v1/datasets/get_datasets/")
        response_content = dict(
            data = Response.json(),
            detail = [],
            msg = "成功返回",
            code = 1,
        )
    except Exception as e:
        response_content = dict(
            detail = [e,],
            msg = str(e),
            code = -1,
        )
    return response_content