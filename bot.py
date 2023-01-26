import os
right_path = __file__.rstrip(os.path.basename(__file__))  # 获取当前文件的所在路径
os.chdir(right_path)    # 将工作路径改至目标路径


import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter



nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

nonebot.load_builtin_plugins('echo', 'single_session')


nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()