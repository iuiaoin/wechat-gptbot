<h1 align="center">Welcome to wechat-gptbot 👋</h1>
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

Work in progress...
