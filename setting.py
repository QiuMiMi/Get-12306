from pydantic import BaseSettings, dataclasses
from typing_extensions import TypedDict
from enum import Enum

class Config(BaseSettings):
    login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
    personal_url = 'https://kyfw.12306.cn/otn/view/index.html'
    left_ticket_url ='https://kyfw.12306.cn/otn/leftTicket/init'

class SeatEnum(str, Enum):
    # 二等座
    second_class = 'second class'
    # 硬卧
    hard_sleeper = 'hard sleeper'

@dataclasses.dataclass
class InfoUser:
    username: str
    password: str
    from_station: str
    to_station: str
    depart_time: str
    trains: dict
    passengers: list
    cookie_str: str = None