from pydantic import BaseSettings, dataclasses

class Config(BaseSettings):
    login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
    personal_url = 'https://kyfw.12306.cn/otn/view/index.html'
    left_ticket_url ='https://kyfw.12306.cn/otn/leftTicket/init'

@dataclasses.dataclass
class InfoUser:
    username: str
    password: str
    from_station: str
    to_station: str
    depart_time: str
    trains: list
    passengers: list
    cookie_str: str = None