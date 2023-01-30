# CirnoBot

~~Baka!~~

使用 [Nonebot2](https://nb2.baka.icu/) 重构的 QQ 聊天机器人。

## Requirements

考虑到兼容性问题，建议使用 `venv`。

- Python 3.10 (推荐，其他版本未测试)
	- nb-cli
		- nonebot_plugin_apscheduler
			- 如果没有的话，可以通过 `nb plugin install nonebot_plugin_apscheduler` 来安装
			- 或者直接 `pip install -r requirements.txt`
	- fastapi, httpx (应当包含在 `nb-cli` 中)
	- sqlite3 (通常在 Python 3.10 中自带)
	- lxml, pandas
- SQLite3