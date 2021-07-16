
def send_post(username,password,image_url1,text):  #,image_url2,image_url3

    import requests
    from pathlib import Path
    from bs4 import BeautifulSoup
    from info_embed import info_embed
    import random

    a = random.randint(1,1000)
    saved_url = 'D:\\Captures\\secret'+str(a)+'.png'
    



    
    # 会话保持
    s = requests.session() 
    url = 'http://192.168.43.27/'  # 网站地址
    r = s.get(url + 'login')
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_token = soup.find(id="csrf_token")['value']
    params = {
        'username': username,
        'password': password,
        'csrf_token': csrf_token
    }
    #print(params)
    r = s.post(url + 'login', data=params)
    
    #print(r.history)

    if not r.status_code == 200:
        print(r.status_code ,'Login failed.')
        return
    
        #嵌入秘密信息
    #if not image_url1 == '':
    info_embed(image_url1,saved_url)
    image = Path(saved_url)
    #print(image.name)
    form_data = {'data': text}
    file = {'files': (image.name, open(image, 'rb'))}
    r = s.post(url + 'upload', data=form_data,files=file)
    #print(r.text)
    if not r.status_code == 200:
        print(r.status_code,'Upload post failed.')
        return
    s.close




