# python实现12306买票 - 待完善

## 使用：修改__init__中对应参数即可
```python
self.username = 账号(str)
self.password = 密码(str)
self.cookie_str = cookie登录(可选)
self.from_station = 出发地(str)
self.to_station = 目的地(str)
self.depart_time = 出发时间(str YYYY-MM-DD)
self.trains = 车次号(list(str))
self.passengers = 乘车人(list(str))
```