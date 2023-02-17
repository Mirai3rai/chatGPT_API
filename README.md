# chatGPT_API

简单改动原版插件，使之调用api来回复。

使用方法：
首先在hoshino/modules下面打开powershell，输入`pip install openai`安装依赖

然后输入`git clone https://github.com/Mirai3rai/chatGPT_API.git`来拉取仓库

之后改动__init__.py，第9行填入你的api，57行修改你自己的触发词。

最后在星乃的__bot__.py中加入"chatGPT_API"。

加入了敏感词系统(缝合XQA的)，不想用可以自己修改一下.

model可以自己改一改，但是text-davinci-003是我自己测下来最好的。
