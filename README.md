# chatGPT_API

简单改动[原版插件](https://github.com/Poppy-xiao/chatGPT)，使之调用api来回复。

## 部署

- 在`hoshino/modules`下打开powershell，输入`pip install openai`安装依赖
- 输入`git clone https://github.com/Mirai3rai/chatGPT_API.git`或`git clone git@github.com:Mirai3rai/chatGPT_API.git`
- 参考`config.json.example`生成`config.json`，填入token。记得填入proxy或使用TUN模式以使本脚本顺利访问OpenAI API。
- 在`hoshino/config/__bot__.py`中加入`chatGPT_API`（或同插件目录名）。

## 使用

```
#GPT <...>
GPT设定 你是<...>
GPT设定重置
```

## utils

[支持AliPay支付的虚拟号平台](https://smspva.com/)

[API获取和使用情况](https://platform.openai.com/account/usage)

[API文档](https://platform.openai.com/docs/api-reference/chat/create)

[API定价](https://openai.com/pricing)

## Credits

- utils 来自 [chatgpt-ui-server](https://github.com/WongSaang/chatgpt-ui-server)
