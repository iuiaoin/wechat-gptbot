## Plugin System

Support personalized plugin extensions, you can easily integrate the functions you want

## Usage

1. Find available plugins [here](source.json), and pick the plugin you want
2. Add them in your `config.json` like this:

```bash
 "plugins": [
    {
      "name": "tiktok",     // plugin name, this is required
      "command": "#tiktok"  // plugin configs, you can find related docs in the plugin repo
      ...
    }
  ]
```

And then you are done, nothing else to do! Just play with your plugins!

## Contributing

### 1. Create your plugin repo

> Maintain the plugin in your own independent GitHub repository.

Take this [sample plugin](https://github.com/iuiaoin/plugin_tiktok) as an example, your plugin repo should be like:

```
tiktok
├──.gitignore
├── __init__.py
├── tiktok.py
├── requirements.txt
└── README.md
```

### 2. Write plugin class

Use `@register` decorator to register plugin and extend basic `Plugin` class

```python
@register
class TikTok(Plugin):
    name = "tiktok" # name is required and must be the same as in source.json
```

### 3. Implement abstract methods

There're four abstract methods in `Plugin` class need to be implemented, and the three hook methods will take the `Event` object as the parameter

- `did_receive_message`: will be called as soon as received the message, its Event contains `channel` and `message`
- `will_generate_reply`: will be called before the reply is generated, its Event contains `channel`, `message` and `context`
- `will_decorate_reply`: will be called before decorate the reply, its Event contains `channel`, `message`, `context` and `reply`
- `will_send_reply`: will be called before sending the reply, its Event contains `channel`, `message`, `context` and decorated `reply`
- `help`: will be used to show help docs to users by `#help <plugin name>` command

You can modify the `context` and `reply` to change the default behavior, and call `event action method` to decide whether to continue the plugin chain or whether to execute the default logic.

- `event.proceed()`: proceed the plugin chain
- `event.stop()`: stop the plugin chain
- `event.bypass()`: bypass the plugin chain and default logic

Here's an example:

```python
def did_receive_message(self, event: Event):
    pass

def will_generate_reply(self, event: Event):
    query = event.context.query
    if query == self.config.get("command"): # instance will get plugin configs when inits
        event.reply = self.reply()          # modify the reply
        event.bypass()                      # bypass the plugin chain and default logic

def will_decorate_reply(self, event: Event):
    pass

def will_send_reply(self, event: Event):
    pass

def help(self, **kwargs) -> str:
    return "Use the command #tiktok(or whatever you like set with command field in the config) to get a wonderful video"
```

### 4. Test your plugin

Run and test the plugin to make sure it works as you expected

### 5. Add to source.json

After testing, you can add your plugin to [source.json](source.json). When the app starts, it will automatically check the plugin configured in config.json and also refer to source.json to install it.

```json
{
  "tiktok": {
    "repo": "https://github.com/iuiaoin/plugin_tiktok.git",
    "desc": "A plugin show you short videos with pretty girls"
  }
}
```
