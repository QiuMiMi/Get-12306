# python实现12306买票 - 待优化

## 使用：初始化一个InfoUser参数对象即可
```python
username = 账号(str)
password = 密码(str)
from_station = 出发地(str)
to_station = 目的地(str)
depart_time = 出发时间(str) - YYYY-MM-DD
trains = 车次信息{车次号: 需要的座位类型}(dict(str, SeatEnum))
passengers = 乘车人(list(str))
cookie_str = cookie登录(可选)
```