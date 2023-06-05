from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from setting import Config, InfoUser
from loguru import logger
import random
import time


class Pc12306:
    def __init__(self, user_info: InfoUser):
        self.driver = webdriver.Chrome()
        self.user_info = user_info
        self.config = Config()

    def use_cookie(self):
        """
        使用cookie登录
        """
        if not self.user_info.cookie_str:
            return False
        self.driver.get(self.config.personal_url)
        for i in self.user_info.cookie_str.split(';'):
            k, v = i.split('=')
            self.driver.add_cookie({'name': k.strip(), 'value': v})
        self.driver.get(self.config.personal_url)

        time.sleep(1)
        if self.driver.current_url == self.config.personal_url:
            logger.info("Login Success")
            return True
        else:
            logger.error("Loading Error")
            return False
        # try:
        #     WebDriverWait(self.driver, 10).until(EC.url_to_be(self.config.personal_url))
        # except Exception as e:
        #     logger.warning("Login Fail, Loading Error")
        #     return False
        # if '欢迎登录12306'in self.driver.page_source:
        #     logger.warning("Cookie Invalid, Login Fail")
        #     return False
        # logger.info("Use Cookie Login Success")
        # return True

    def login(self):
        """
        登录
        """
        if self.use_cookie():
            return True
        
        # 进入登入页面
        self.driver.get(self.config.login_url)
        WebDriverWait(self.driver, 10, 0.5).until(EC.url_to_be(self.config.login_url))
        self.driver.maximize_window()

        # 通过反扒机制(防止滑动验证码有可能显示失败)
        script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
        self.driver.execute_script(script)

        # 账号密码输入
        self.driver.find_element(By.ID, "J-userName").send_keys(self.user_info.username)
        self.driver.find_element(By.ID, "J-password").send_keys(self.user_info.password)

        # 点击登录
        WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable((By.ID, "J-login")))
        self.driver.find_element(By.ID, "J-login").click()

        # 滑块验证处理
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.presence_of_element_located((By.ID, "nc_1_n1z")))
        except Exception as e:
            logger.error('加载验证码出错')
        if '点击刷新' in self.driver.page_source:
            self.driver.find_element(By.XPATH, '//*[@id="J-slide-passcode"]/div/span[1]/a[1]').click()
        
        # 存在无需验证码也能成功登录的情况
        try:
            slide = self.driver.find_element(By.ID,"nc_1_n1z")
            ActionChains(self.driver).click_and_hold(slide).move_by_offset(380,0).release().perform()
        except Exception as e:
            pass

        # 判断是否登录成功
        time.sleep(1)
        if self.driver.current_url == self.config.personal_url:
            logger.info("Login Success")
            return True
        else:
            logger.error("Loading Error")
            return False
    
    def info_select(self):
        """
        信息查询
        """
        # 进入车票查询页
        self.driver.get(self.config.left_ticket_url)
        WebDriverWait(self.driver, 10, 0.5).until(EC.url_to_be(self.config.left_ticket_url))

        #出发地输入
        self.driver.find_element(By.ID,'fromStationText').click()
        self.driver.find_element(By.ID,'fromStationText').send_keys(self.user_info.from_station)
        self.driver.find_element(By.ID,'fromStationText').send_keys(Keys.ENTER)
        #目的地输入
        self.driver.find_element(By.ID,'toStationText').click()
        self.driver.find_element(By.ID,'toStationText').send_keys(self.user_info.to_station)
        self.driver.find_element(By.ID,'toStationText').send_keys(Keys.ENTER)
        #出发日期输入
        self.driver.find_element(By.ID,'train_date').clear()
        self.driver.find_element(By.ID,'train_date').send_keys(self.user_info.depart_time)

        # 点击查询
        WebDriverWait(self.driver, 5 , 0.5).until(EC.element_to_be_clickable((By.ID,"query_ticket")))
        self.driver.find_element(By.ID,'query_ticket').click()

        # 等待查询加载完毕
        WebDriverWait(self.driver,10, 0.5).until(EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr")))

        # 获取车票列表
        tr_list = self.driver.find_elements(By.XPATH,".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
        return tr_list

    def vote(self, tr_list):
        """
        选票
        """
        if not self.user_info.trains:
            logger.info("目标车次为空啦")
            return True
        # 迭代票信息
        for tr in tr_list[:-1]:
            # 找到目标车次预订
            try:
                train_number = tr.find_element(By.CLASS_NAME,"number").text
            except Exception as e:
                continue
            if train_number not in self.user_info.trains:
                continue

            # 目标座位类型是否有票
            if self.user_info.trains[train_number] == 'hard sleeper':
                td_index = 8
            elif self.user_info.trains[train_number] == 'second class':
                td_index = 4
            else:
                td_index = 4
            left_ticker_td = tr.find_element(By.XPATH,f'.//td[{td_index}]').text
            logger.info(f"车次 {train_number} 状态: {left_ticker_td}")
            if left_ticker_td == '有' or left_ticker_td.isdigit():
                btn72 = tr.find_element(By.CLASS_NAME,'btn72')
                btn72.click()

                # 完善乘客信息
                WebDriverWait(self.driver, 5 , 0.5).until(EC.presence_of_element_located((By.XPATH,".//ul[@id='normal_passenger_id']/li")))
                passenger_labels = self.driver.find_elements(By.XPATH,".//ul[@id='normal_passenger_id']/li/label")
                for passenger_label in passenger_labels:
                    name = passenger_label.text
                    if name in self.user_info.passengers:
                        passenger_label.click()
                submitbtn = self.driver.find_element(By.ID,'submitOrder_id')
                submitbtn.click()

                # 信息确认
                WebDriverWait(self.driver, 5, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME,"dhtmlx_wins_body_outer")))
                WebDriverWait(self.driver, 5, 0.5).until(EC.presence_of_element_located((By.ID,"qr_submit_id")))
                WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable((By.ID, "qr_submit_id")))
                confirmbtn = self.driver.find_element(By.ID, "qr_submit_id")
                confirmbtn.click()
                try:
                    while confirmbtn:
                        confirmbtn.click()
                        confirmbtn = self.driver.find_element(By.ID, "qr_submit_id")
                except:
                    pass
                logger.info(f'恭喜，车次 {train_number} {self.user_info.trains.pop(train_number)}抢票成功！请前往客户端确认订单')
                
        return False

    def main(self):
        logger.info('用户信息如下, 开始执行......')
        logger.info(self.user_info)
        # 登录
        login_state = self.login()
        if not login_state:
            return
        
        # 抢票
        for _ in range(10):
            logger.info('轮询选票中')
            tr_list = self.info_select()
            if self.vote(tr_list):
                break
            time.sleep(random.uniform(1, 2))
        time.sleep(10)

    def __del__(self):
        logger.info('页面退出')
        self.driver.quit()

if __name__ == "__main__":
    user_info = InfoUser(
        username = "账号(user)",
        password = "密码(12345678)",
        from_station = "出发地(上海)",
        to_station = "目的地(北京)",
        depart_time = "出发时间(2023-06-15)",
        trains = "目标车次列表(['G1630', 'G1631'])",
        passengers = "目标乘车人列表(['某某某1', '某某某2'])",
    )
    p1 = Pc12306(user_info=user_info)
    p1.main()
    del p1
