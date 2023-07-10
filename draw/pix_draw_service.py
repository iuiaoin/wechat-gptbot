import os
import time
import base64
import json
import requests
from config import conf
import asyncio

from utils.log import logger
from utils.erciyuan import getdesc

from concurrent.futures import ThreadPoolExecutor

async def async_pix_stable_image(wx_plugin,tags,wxid):
    headers = {'Content-Type': 'application/json',  'authorization': conf().get('bbs_pix')}
    sourcecfg = aidraw['text2image']
    sourcecfg['v2'] = True
    sourcecfg['model'] = 'anything_v3'
    sourcecfg['type'] = 'text2image'
    sourcecfg['prompts'] = sourcecfg['prompt']
    sourcecfg['negativePrompts'] = sourcecfg['negative_prompt']
    sourcecfg['step'] = sourcecfg['steps']
    sourcecfg['cfg'] = sourcecfg['cfg_scale']
    sourcecfg['batch'] = sourcecfg['batch_size']

    try:
        # json_conent = json.dumps(sourcecfg)
        # print(json_conent)
        print('post pix '+'https://api.hua-der.com/api/artworks/create')
        response = requests.post('https://api.hua-der.com/api/artworks/create', json=sourcecfg,headers=headers)    
        response.raise_for_status()
    except Exception as e:
        print("发生错误:", e)
        print("error:", response.text)
        return ""
    try:
        # print(response.text)
        jsonarray = json.loads(response.text)
        hashid = jsonarray[0]['hashid']
        image_url = None
        for i in range(20):
            await asyncio.sleep(3)
            get_url = 'https://api.hua-der.com/api/artworks?hashid='+hashid
            print('request pix '+get_url)
            get_response = requests.get(get_url,headers=headers)
            # print(get_response.text)
            get_response_json = json.loads(get_response.text)
            my_list = get_response_json['artworks']
            result = list(filter(lambda obj: obj['hashid'] == hashid, my_list)) 
            if result[0]['status']=='generated':
                image_url = result[0]['meta']['generateResultUrl']['jpg']
                break
            else:
                print('request pix:'+result[0]['status'])
        if image_url != None:
            print('imgae '+hashid+" is "+image_url)
            path = os.path.abspath("./assets")
            img_name = int(time.time() * 1000)            
            save_image_from_url(image_url,f"{path}\\{img_name}.png")
            img_path = os.path.abspath(f"{path}\\{img_name}.png").replace("\\", "\\\\")
            wx_plugin.send_image_path(img_path,wxid)
    except Exception as e:
        print("发生错误:", e)
    return ""

def async_pix_task(wx_plugin,tags,wxid):
    
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(async_pix_stable_image(wx_plugin,tags,wxid))
    finally:
        loop.close()