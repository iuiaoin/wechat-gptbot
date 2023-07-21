import requests
import json
import uuid

class ClaudeAPIWrapper:
    def __init__(self, session_key):
        self.session_key = session_key
        self.headers = {
            'Cookie': f'{self.session_key}',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        }
        
    def add_chat_conversation(self, organization_uuid, name=""):
        url = f"https://claude.ai/api/organizations/{organization_uuid}/chat_conversations"
        self.headers["Content-Type"] = "application/json"
        payload = json.dumps({
            "uuid": str(uuid.uuid4()),
            "name": "",
        })
        response = requests.request("POST", url, headers=self.headers, data=payload)
        # 去掉['Content-Type'] = 'application/json'，否则会报错
        self.headers.pop("Content-Type")
        return response.json()

    def get_conversation(self, organization_uuid, conversation_uuid):
        url = f"https://claude.ai/api/organizations/{organization_uuid}/chat_conversations/{conversation_uuid}"
        response = requests.request("GET", url, headers=self.headers)
        return response.text
    
    def get_organizations(self):
        url = "https://claude.ai/api/organizations"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()
    
    def get_chat_conversations(self, organization_uuid):
        url = f"https://claude.ai/api/organizations/{organization_uuid}/chat_conversations"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()
    
    def delete_chat_conversation(self, organization_uuid, conversation_uuid):
        url = f"https://claude.ai/api/organizations/{organization_uuid}/chat_conversations/{conversation_uuid}"
        response = requests.request("DELETE", url, headers=self.headers)
        return response.status_code
    
    def convert_document(self, file_path, organization_uuid):
        url = "https://claude.ai/api/convert_document"
        payload = {'orgUuid': organization_uuid}
        file_name = file_path.split('/')[-1]
        files=[
            ('', (file_name, open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
        ]
        response = requests.request("POST", url, headers=self.headers, data=payload, files=files)
        try:
            return_obj = response.json()
            return return_obj
        except:
            return None

    def send_message(self, organization_uuid, conversation_uuid, message, attachments=[]):
        url = "https://claude.ai/api/append_message"
        payload = json.dumps({
            "completion": {
                "prompt": message,
                "timezone": "Asia/Shanghai",
                "model": "claude-2",
                "incremental": True
            },
            "organization_uuid": organization_uuid,
            "conversation_uuid": conversation_uuid,
            "text": message,
            "attachments": attachments
        })
        response = requests.request("POST", url, headers=self.headers, data=payload, stream=True)
        for message_chunk in response.iter_lines():
            message_chunk = message_chunk.decode('utf-8')
            if message_chunk.strip() == '':
                continue
            # print(message_chunk[6:])
            message_json = json.loads(message_chunk[6:])  # Skip the 'data: ' prefix
            if "stop_reason" in message_json and message_json["stop_reason"] is not None:
                break
            yield message_json["completion"]