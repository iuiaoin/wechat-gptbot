<h1 align="center">Welcome to wechat-gptbot 👋</h1>
<div align="center">
  <img width="200" src="./docs/images/logo.png">
</div>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="#" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg" />
  </a>
  <a href="https://www.python.org/">
    <img
      alt="Python Version"
      src="https://img.shields.io/badge/python-%20%3E%3D%203.8-brightgreen"
    />
  </a>
</p>

> A wechat robot based on ChatGPT with no risk, very stable! 🚀  
> English | [中文文档](README_ZH.md)

## 🌟 Features

- [x] **Extremely Stable：** Implement based on windows hook, no worry about risk of wechat account restriction
- [x] **Basic Conversation：** Smart reply for private chat and group chat, support multiple rounds of session context memory, support GPT-3, GPT-3.5, GPT-4 models
- [x] **Image Generation：** Support image generation, Dell-E only model for now
- [x] **Flexible Configuration：** Support prompt settings, proxy, command settings and etc.

## 🚀 Getting Start

### Environment

Support Windows system(probably support Linux in the future based on [sandbox](https://github.com/huan/docker-wechat)) and `Python` needs to be installed at the same time

> It is recommended that the Python version be between 3.8.X~3.10.X, version 3.8 is perfect

#### 1. Clone repo

```bash
git clone https://github.com/iuiaoin/wechat-gptbot && cd wechat-gptbot
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### Configuration

`config.template.json` in the root directory contains the configs template, you need to copy the template to create the final effective `config.json`

```bash
  cp config.template.json config.json
```

Then fill in the configuration in `config.json`, the following is the description of the default configuration, which can be customized according to the needs:

```bash
{
  "openai_api_key": "YOUR API SECRET KEY",             # Fill in your OpenAI API Key
  "model": "gpt-3.5-turbo",                            # ID of the model to use, support gpt-3.5-turbo, gpt-4, gpt-4-32k etc.
  "role_desc": "You are a helpful assistant.",         # Role description as system prompt
  "session_expired_duration": 3600,                    # Session memory kept duration
  "max_tokens": 1000,                                  # Max tokens of characters for session memory
  "temperature": 0.9,                                  # Between 0 and 2. Higher values make the output more random, while lower values more focused
  "proxy": "127.0.0.1:3000",                           # Proxy client ip and port
  "create_image_prefix": ["draw", "paint", "imagine"], # Text prefix for image generation
  "clear_current_session_command": "#clear session",   # Clear current session
  "clear_all_sessions_command": "#clear all sessions"  # Clear all sessions
}
```

### Running

#### 1. Prepare

> We need the specific wechat version and dll to make windows hook work.

1. Download assets from the [release](https://github.com/iuiaoin/wechat-gptbot/releases/tag/v1.0.0)
2. Install WeChatSetup-3.2.1.121.exe and login
3. Run the wechat-dll-injectorV1.0.3.exe
4. Select 3.2.1.121-LTS.dll and click `inject dll`, you will see "Successfully injected: 3.2.1.121-LTS.dll"

#### 2. Run command

```bash
python app.py
```

<img width="1440" src="./docs/images/startup.svg">

Voilà! Enjoy your exploring journey~
