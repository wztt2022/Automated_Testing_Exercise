# -*- encoding: utf-8 -*-
import unittest
import yaml
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from img_compare import _compare


class WebTest(unittest.TestCase):

    # 初始化driver
    def setUp(self):
        self.params = yaml.load(open('search_by_img_config.yaml', 'r', encoding="utf-8"))['page1']
        self.driver = webdriver.Chrome("/Users/zhangwei14/Downloads/chromedriver")
        self.driver.maximize_window()
        self.driver.get(self.params['google_search_url'])

    # 隐式等待
    def wait_element(self, *locator):
        wait = WebDriverWait(self.driver, 10, 1, (StaleElementReferenceException,))
        try:
            ele = wait.until(EC.visibility_of_all_elements_located(*locator))
            return ele
        except TimeoutException:
            print("timeout exception,Can't find element by method : %s", *locator)
            return None

    # case step
    def test_search_by_image(self):
        target = 2
        img_url = self.params['img_url']
        # 打开search by image功能
        self.driver.find_element_by_xpath(self.params['search_by_image_button']).click()
        # 等待弹框
        self.wait_element((By.NAME, 'image_url'))
        # 输入查询image url
        self.driver.find_element_by_name('image_url').send_keys(img_url)
        # 执行查询
        self.driver.find_element_by_xpath(self.params['search_button']).click()
        # 等待查询结果渲染
        self.wait_element((By.ID, 'result-stats'))
        # 获取查询结果集
        elements = self.driver.find_elements_by_tag_name('h3')
        # 查看指定结果
        elements[target].click()
        self.wait_element((By.XPATH, self.params['result_title']))
        # case 1 screenshoot
        self.driver.save_screenshot('result_page.png')
        # 获取比对图片
        result_img_url = self.driver.find_element_by_xpath(self.params['target_img_url']).get_attribute('src')
        with open('result_img.png', 'wb') as f:
            f.write(requests.get(result_img_url).content)
        # case 2 assert image
        rms = _compare('result_img.png', 'except_img.jpeg')
        # 相似度大于等于80%定义为符合查询结果
        assert rms >= 80

    def tearDown(self):
        self.driver.quit()
