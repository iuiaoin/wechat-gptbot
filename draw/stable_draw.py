from googletrans import Translator
import os
import time
import base64
import json
import requests
from utils.log import logger

translator = Translator()


with open('aidraw.json', mode="r", encoding="utf-8") as f:
    data = f.read()
    aidraw = json.loads(data)

def translate(tags):
    translation  = translator.translate(tags, dest='en')
    print(translation.origin, ' -> ', translation.text)
    return translation.text

def send_stable_img(wx_plugin,tags,wxid):
    try:
        # download image
        path = os.path.abspath("./assets")
        img_name = int(time.time() * 1000)
        # response = requests.get(content, stream=True)
        # response.raise_for_status()  # Raise exception if invalid response

        # print(self.aidraw)
        # print(type(self.aidraw))
        # print(type(self.aidraw['text2image']))
        translation  = translator.translate(tags.replace("draw",""), dest='en')
        print(translation.origin, ' -> ', translation.text)
        aidraw['text2image']['prompt'] = translation.text
        aidraw['text2image']['seed'] = -1
        aidraw['text2image']['sampler_index'] = 'Euler a'
        aidraw['text2image']['steps'] = 20
        aidraw['text2image']['cfg_scale'] = 7


        try:
            headers = {'Content-Type': 'application/json', 'Authorization':''}
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', data=json.dumps(aidraw['text2image']),headers=headers)
            response.raise_for_status()  # 检查响应状态码

            # 从响应中获取数据
            json_data = response.json()
            base64_image = json_data['images'][0].replace('data:image/png;', '').replace('base64,', '')
            # 将base64编码的图像转换为字节数据
            image_bytes = base64.b64decode(base64_image)

            with open(f"{path}\\{img_name}.png", "wb+") as f:
                f.write(image_bytes) # 返回请求到的JSON响应数据
                f.close()

        except requests.exceptions.HTTPError as e:
            print("HTTP请求错误:", e)
            print("响应状态码:", response.status_code)
            print("响应内容:", response.text)
            return
        except requests.exceptions.RequestException as e:
            print("请求发生异常:", e)
            return
        except Exception as e:
            print("发生错误:", e)
            return

        img_path = os.path.abspath(f"{path}\\{img_name}.png").replace("\\", "\\\\")
        wx_plugin.send_image_path(img_path,wxid)

    except Exception as e:
        logger.error(f"[Download Image Error]: {e}")
