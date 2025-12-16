#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
房天下成交数据综合爬虫
功能:
1. 从列表页提取小区详情链接
2. 进入每个小区详情页,爬取"同小区成交"列表
3. 翻页爬取,当时间早于2023年时终止
4. 只提取价格不为0的记录
5. 每完成一个小区就写入CSV
"""

import undetected_chromedriver as uc
import time
import csv
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class CombinedCrawler:
    def __init__(self, base_url='https://esf.fang.com', output_file='community_deals.csv'):
        self.driver = None
        self.base_url = base_url.rstrip('/')  # 去除末尾斜杠
        self.output_file = output_file
        self.csv_file = None
        self.csv_writer = None
        self.total_count = 0
        
    def init_driver(self):
        """初始化浏览器"""
        try:
            print('正在初始化浏览器...')
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_window_size(1920, 1080)
            print('✓ 浏览器初始化成功\n')
            return True
        except Exception as e:
            print(f'✗ 浏览器初始化失败: {e}')
            return False
    
    def init_csv(self):
        """初始化CSV文件"""
        try:
            self.csv_file = open(self.output_file, 'w', encoding='utf-8-sig', newline='')
            fieldnames = ['community', 'district', 'business_area', 'title', 
                         'room_type', 'area', 'orientation', 'floor_info',
                         'total_price', 'unit_price', 'deal_date', 'source', 'url']
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            self.csv_file.flush()
            print(f'✓ CSV文件已创建: {self.output_file}\n')
            return True
        except Exception as e:
            print(f'✗ 创建CSV文件失败: {e}')
            return False
    
    def check_verification(self):
        """检查并处理验证"""
        if '请完成下列验证' in self.driver.page_source:
            print('⚠ 检测到验证页面,请在30秒内手动完成验证...')
            time.sleep(30)
            return True
        return False
    
    def parse_date(self, date_str):
        """解析日期字符串,返回年份"""
        try:
            # 格式: 2025-10-28 或 2025.10.28
            match = re.search(r'(\d{4})', date_str)
            if match:
                return int(match.group(1))
        except:
            pass
        return None
    
    def extract_list_page_urls(self, start_page=1, max_list_pages=1):
        """从列表页提取所有详情页URL，支持翻页"""
        all_urls = []
        
        for page_num in range(start_page, start_page + max_list_pages):
            # 构造URL
            if page_num == 1:
                page_url = f'{self.base_url}/chengjiao/'
            else:
                page_url = f'{self.base_url}/chengjiao/i3{page_num}/'
            
            print(f'正在访问列表第 {page_num} 页: {page_url}')
            
            try:
                # 检查浏览器窗口是否还存在
                try:
                    _ = self.driver.current_url
                except Exception as e:
                    if 'target window already closed' in str(e) or 'no such window' in str(e):
                        print('\n⚠ 检测到浏览器窗口已关闭!')
                        print('   可能原因:')
                        print('   1. 用户手动关闭了浏览器窗口')
                        print('   2. 触发了反爬虫验证,需要手动处理')
                        print('   3. 浏览器崩溃')
                        print('\n   程序将停止运行,请重新启动')
                        print('   提示: 如需继续,可修改 start_list_page 参数从当前页继续')
                        return all_urls
                    raise
                
                self.driver.get(page_url)
                time.sleep(0.1)
                self.check_verification()
                
                # 滚动加载
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.1)
                
                # 提取所有详情页链接
                house_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.houseList dl.list dd.info p.title a")
                
                urls = []
                for elem in house_elements:
                    url = elem.get_attribute('href')
                    if url and 'chengjiao/' in url and '_1_2.htm' in url:
                        urls.append(url)
                
                # 如果找到0个链接,检查是否需要验证
                if len(urls) == 0:
                    page_source = self.driver.page_source
                    if '滑动验证' in page_source or '请完成验证' in page_source or 'SliderTools' in page_source:
                        print(f'  ⚠ 第 {page_num} 页找到 0 个链接,检测到需要滑动验证')
                        print('     请手动完成验证...')
                        print('     验证完成后程序将自动继续')
                        
                        # 等待验证完成
                        max_wait = 120
                        wait_count = 0
                        while wait_count < max_wait:
                            time.sleep(1)
                            wait_count += 1
                            
                            # 每5秒检查一次
                            if wait_count % 5 == 0:
                                # 重新提取链接
                                try:
                                    house_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.houseList dl.list dd.info p.title a")
                                    urls = []
                                    for elem in house_elements:
                                        url = elem.get_attribute('href')
                                        if url and 'chengjiao/' in url and '_1_2.htm' in url:
                                            urls.append(url)
                                    
                                    if len(urls) > 0:
                                        print(f'     ✓ 验证完成! 找到 {len(urls)} 个详情页链接')
                                        break
                                    else:
                                        print(f'     等待验证... ({wait_count}/{max_wait}秒)')
                                except:
                                    print(f'     等待验证... ({wait_count}/{max_wait}秒)')
                        
                        if len(urls) == 0:
                            print(f'  ✗ 验证超时,第 {page_num} 页跳过')
                    else:
                        print(f'  ✓ 第 {page_num} 页找到 {len(urls)} 个详情页链接 (页面可能为空)')
                else:
                    print(f'  ✓ 第 {page_num} 页找到 {len(urls)} 个详情页链接')
                
                all_urls.extend(urls)
                
                # 列表页间隔
                if page_num < start_page + max_list_pages - 1:
                    time.sleep(0.1)
                
            except Exception as e:
                print(f'  ✗ 提取列表第 {page_num} 页失败: {e}')
                continue
        
        print(f'\n✓ 总共找到 {len(all_urls)} 个详情页链接\n')
        return all_urls
    
    def parse_community_deals(self, detail_url):
        """解析小区详情页的同小区成交数据"""
        print(f'\n{"="*80}')
        print(f'正在访问详情页: {detail_url}')
        
        try:
            # 检查浏览器窗口是否还存在
            try:
                _ = self.driver.current_url
            except Exception as e:
                if 'target window already closed' in str(e) or 'no such window' in str(e):
                    print('\n⚠ 浏览器窗口已关闭,停止爬取')
                    return -1  # 返回-1表示需要停止
                raise
            
            self.driver.get(detail_url)
            time.sleep(0.2)  # 增加等待时间
            self.check_verification()
            
            # 检查页面标题,判断是否是有效页面
            page_title = self.driver.title
            if '404' in page_title or '错误' in page_title or not page_title:
                print(f'✗ 页面无效: {page_title}')
                return 0
            
            # 获取小区基本信息
            community_info = self.get_community_info()
            if not community_info:
                # 检查是否需要验证
                page_source = self.driver.page_source
                if '滑动验证' in page_source or '请完成验证' in page_source or 'SliderTools' in page_source:
                    print('⚠ 无法获取小区信息,检测到需要滑动验证')
                    print('   请手动完成验证...')
                    print('   验证完成后程序将自动继续')
                    
                    # 等待验证完成
                    max_wait = 120  # 最多等待120秒
                    wait_count = 0
                    while wait_count < max_wait:
                        time.sleep(1)
                        wait_count += 1
                        
                        # 每5秒检查一次
                        if wait_count % 5 == 0:
                            community_info = self.get_community_info()
                            if community_info:
                                print(f'✓ 验证完成! 成功获取小区信息: {community_info.get("community", "")}')
                                break
                            else:
                                print(f'   等待验证... ({wait_count}/{max_wait}秒)')
                    
                    if not community_info:
                        print('✗ 验证超时,跳过该小区')
                        return 0
                else:
                    print('✗ 无法获取小区信息,跳过')
                    return 0
            
            print(f'\n小区: {community_info["community"]} | 区域: {community_info["district"]}-{community_info["business_area"]}')
            
            # 爬取所有页面的成交数据
            all_items = []  # 收集该小区所有数据
            page_num = 1
            should_continue = True
            max_pages = 100  # 设置最大翻页次数,防止死循环
            
            # 获取总页数
            total_pages = self.get_total_pages()
            if total_pages:
                print(f'检测到总页数: {total_pages}')
            
            while should_continue and page_num <= max_pages:
                print(f'\n--- 第 {page_num} 页 ---')
                page_items, should_stop = self.parse_current_page(community_info)
                all_items.extend(page_items)
                
                if should_stop:
                    print(f'⚠ 发现2023年之前的数据,停止翻页')
                    break
                
                # 检查是否已到最后一页
                if total_pages and page_num >= total_pages:
                    print(f'⚠ 已到最后一页 (第{page_num}/{total_pages}页)')
                    break
                
                # 尝试翻页
                if not self.go_to_next_page():
                    print('⚠ 已到最后一页或无法翻页')
                    break
                
                page_num += 1
                time.sleep(0.1)
            
            if page_num > max_pages:
                print(f'⚠ 已达到最大翻页次数限制({max_pages}页)')
            
            # 爬完该小区后,批量写入CSV
            total_saved = 0
            if all_items:
                for item in all_items:
                    self.csv_writer.writerow(item)
                    total_saved += 1
                    self.total_count += 1
                self.csv_file.flush()
                print(f'\n✓ 小区 [{community_info["community"]}] 完成,写入 {total_saved} 条有效数据')
            else:
                print(f'\n✓ 小区 [{community_info["community"]}] 完成,无有效数据')
            print(f'{"="*80}')
            
            return total_saved
            
        except Exception as e:
            print(f'✗ 解析小区详情失败: {e}')
            import traceback
            traceback.print_exc()
            return 0
    
    def get_total_pages(self):
        """获取总页数
        
        从页面的分页元素提取总页数
        
        Returns:
            int: 总页数,如果获取失败返回None
        """
        try:
            # 方式1: 使用XPath查找
            page_info_elem = None
            try:
                page_info_elem = self.driver.find_element(By.XPATH, '//*[@id="pages"]/div/span')
            except:
                pass
            
            # 方式2: 使用CSS选择器查找
            if not page_info_elem:
                try:
                    page_info_elem = self.driver.find_element(By.CSS_SELECTOR, '#pages div span.txt')
                except:
                    pass
            
            if page_info_elem:
                page_text = page_info_elem.text.strip()
                # 解析 "共22页" 格式
                match = re.search(r'共(\d+)页', page_text)
                if match:
                    total_pages = int(match.group(1))
                    return total_pages
        except:
            pass
        
        return None
    
    def get_community_info(self):
        """获取小区基本信息"""
        try:
            info = {}
            
            # 从 div.informid 提取小区名和区域
            info_lines = self.driver.find_elements(By.CSS_SELECTOR, "div.informid p")
            
            if not info_lines:
                print('  [调试] 未找到 div.informid p 元素')
                
                # 检查是否有验证页面
                page_source = self.driver.page_source
                if '滑动验证' in page_source or '请完成验证' in page_source or 'SliderTools' in page_source:
                    print('⚠ 检测到滑动验证,请手动完成验证...')
                    print('   验证完成后程序将自动继续')
                    
                    # 等待验证完成 - 持续检查直到元素出现
                    max_wait = 60  # 最多等待60秒
                    wait_count = 0
                    while wait_count < max_wait:
                        time.sleep(1)
                        wait_count += 1
                        
                        # 每5秒检查一次
                        if wait_count % 5 == 0:
                            info_lines = self.driver.find_elements(By.CSS_SELECTOR, "div.informid p")
                            
                            if info_lines:
                                print(f'✓ 验证完成! 找到小区信息元素')
                                break
                            else:
                                print(f'   等待中... ({wait_count}/{max_wait}秒)')
                    
                    if not info_lines:
                        print('  [调试] 验证后仍未找到元素')
                        return None
                else:
                    return None
            
            for line in info_lines:
                text = line.text.strip()
                if '小区：' in text:
                    links = line.find_elements(By.TAG_NAME, 'a')
                    if len(links) >= 1:
                        info['community'] = links[0].text.strip()
                    if len(links) >= 2:
                        info['district'] = links[1].text.strip()
                    if len(links) >= 3:
                        info['business_area'] = links[2].text.strip()
                    break
            
            if not info:
                print('  [调试] 未找到包含"小区："的行')
                return None
            
            if 'community' not in info:
                print('  [调试] 未提取到小区名称')
                return None
                
            return info
            
        except Exception as e:
            print(f'  [调试] 获取小区信息异常: {e}')
            return None
    
    def parse_current_page(self, community_info):
        """解析当前页面的成交数据 (优化版 - 使用JS批量提取)
        
        Returns:
            tuple: (数据列表, 是否应该停止翻页)
        """
        try:
            # 滚动到列表位置
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)
            
            # 使用JavaScript一次性提取所有数据，大幅减少浏览器通信次数
            js_code = """
            var items = [];
            var houses = document.querySelectorAll('div.houseList dl.list');
            houses.forEach(function(house) {
                var item = {};
                
                // 标题和链接
                var titleElem = house.querySelector('dd.info p.title a');
                item.title = titleElem ? titleElem.innerText.trim() : '';
                item.url = titleElem ? titleElem.href : '';
                
                // 朝向和楼层信息
                var infoP = house.querySelector('dd.info p');
                item.info_line = infoP ? infoP.innerText.trim() : '';
                
                // 成交日期
                var dateElem = house.querySelector('div.area p.time');
                item.deal_date = dateElem ? dateElem.innerText.trim() : '';
                
                // 来源标签
                var sourceElem = house.querySelector('div.area p.tag');
                item.source = sourceElem ? sourceElem.innerText.trim() : '';
                
                // 价格
                var priceElem = house.querySelector('div.moreInfo p.alignR span.price');
                item.total_price = priceElem ? priceElem.innerText.trim() : '';
                
                // 单价
                var unitElem = house.querySelector('div.moreInfo p.danjia b');
                item.unit_price = unitElem ? unitElem.innerText.trim() : '';
                
                items.push(item);
            });
            return items;
            """
            
            raw_items = self.driver.execute_script(js_code)
            
            if not raw_items or len(raw_items) == 0:
                print('未找到成交记录(0个房源)')
                
                # 检查是否有验证页面
                page_source = self.driver.page_source
                if '滑动验证' in page_source or '请完成验证' in page_source or 'SliderTools' in page_source:
                    print('⚠ 检测到滑动验证,请手动完成验证...')
                    print('   验证完成后程序将自动继续')
                    
                    max_wait = 60
                    wait_count = 0
                    while wait_count < max_wait:
                        time.sleep(1)
                        wait_count += 1
                        
                        if wait_count % 5 == 0:
                            raw_items = self.driver.execute_script(js_code)
                            if raw_items and len(raw_items) > 0:
                                print(f'✓ 验证完成! 找到 {len(raw_items)} 条记录')
                                break
                            else:
                                print(f'   等待中... ({wait_count}/{max_wait}秒)')
                    
                    if not raw_items or len(raw_items) == 0:
                        print('验证后仍未找到成交记录')
                        return [], False
                else:
                    return [], False
            
            page_items = []
            should_stop = False
            
            for idx, raw in enumerate(raw_items, 1):
                try:
                    item = {}
                    
                    item['title'] = raw.get('title', '')
                    item['url'] = raw.get('url', '')
                    
                    # 提取户型和面积
                    room_match = re.search(r'(\d+室\d+厅)', item['title'])
                    item['room_type'] = room_match.group(1) if room_match else ''
                    
                    area_match = re.search(r'([\d.]+)平米', item['title'])
                    item['area'] = area_match.group(1) if area_match else ''
                    
                    # 朝向和楼层
                    info_line = raw.get('info_line', '')
                    orientation_match = re.search(r'([东南西北]+向)', info_line)
                    item['orientation'] = orientation_match.group(1) if orientation_match else ''
                    
                    floor_match = re.search(r'([低中高顶底]+楼层).*?\(共\d+层\)', info_line)
                    item['floor_info'] = floor_match.group(0) if floor_match else ''
                    
                    # 成交日期
                    item['deal_date'] = raw.get('deal_date', '')
                    
                    # 检查日期是否早于2023年
                    if item['deal_date']:
                        year = self.parse_date(item['deal_date'])
                        if year and year < 2023:
                            print(f'  [{idx}] {item["deal_date"]} - 早于2023年,标记停止')
                            should_stop = True
                            continue
                    
                    # 来源标签
                    item['source'] = raw.get('source', '')
                    
                    # 价格信息
                    price_text = raw.get('total_price', '')
                    if price_text:
                        price_match = re.search(r'(\d+)', price_text)
                        if price_match:
                            price_value = int(price_match.group(1))
                            item['total_price'] = price_text
                            
                            if price_value == 0:
                                print(f'  [{idx}] {item["title"][:30]}... - 价格为0,跳过')
                                continue
                        else:
                            continue
                    else:
                        continue
                    
                    # 单价
                    item['unit_price'] = raw.get('unit_price', '')
                    
                    # 添加小区信息
                    item['community'] = community_info.get('community', '')
                    item['district'] = community_info.get('district', '')
                    item['business_area'] = community_info.get('business_area', '')
                    
                    page_items.append(item)
                    
                    print(f'  ✓ [{idx}] {item["title"][:30]}... | {item["deal_date"]} | {item["total_price"]}万')
                
                except Exception as e:
                    print(f'  ✗ [{idx}] 解析失败: {e}')
                    continue
            
            return page_items, should_stop
            
        except Exception as e:
            print(f'✗ 解析页面失败: {e}')
            return [], False
    
    def go_to_next_page(self):
        """翻页到下一页 (优化版 - 使用JS批量操作)
        
        Returns:
            bool: 是否翻页成功
        """
        try:
            # 使用JS一次性获取翻页前的状态和执行点击
            js_get_state = """
            var result = {pageNum: null, titles: []};
            
            // 获取当前页码
            var pageElem = document.querySelector('a.pageNow, div.page_al span.on, div.page_al a.on');
            if (pageElem) result.pageNum = pageElem.innerText.trim();
            
            // 获取前3条记录标题
            var titleElems = document.querySelectorAll('div.houseList dl.list dd.info p.title a');
            for (var i = 0; i < Math.min(3, titleElems.length); i++) {
                result.titles.push(titleElems[i].innerText.trim());
            }
            
            return result;
            """
            
            state_before = self.driver.execute_script(js_get_state)
            
            # 使用JS查找并点击下一页按钮
            js_click_next = """
            var nextBtn = document.getElementById('page_next');
            if (!nextBtn) {
                var links = document.querySelectorAll('a');
                for (var i = 0; i < links.length; i++) {
                    if (links[i].innerText.trim() === '下一页') {
                        nextBtn = links[i];
                        break;
                    }
                }
            }
            
            if (!nextBtn) return 'not_found';
            
            // 检查是否隐藏或禁用
            var style = nextBtn.getAttribute('style') || '';
            var className = nextBtn.className || '';
            if (style.indexOf('display') >= 0 && style.indexOf('none') >= 0) return 'hidden';
            if (className.indexOf('disable') >= 0) return 'disabled';
            
            // 滚动到按钮位置并点击
            nextBtn.scrollIntoView(false);
            nextBtn.click();
            return 'clicked';
            """
            
            click_result = self.driver.execute_script(js_click_next)
            
            if click_result == 'not_found':
                return False
            if click_result in ('hidden', 'disabled'):
                return False
            
            # 等待页面更新 - 轮询检查
            max_wait = 3  # 减少到3秒
            wait_interval = 0.2
            waited = 0
            
            while waited < max_wait:
                time.sleep(wait_interval)
                waited += wait_interval
                
                # 使用JS检查状态变化
                state_after = self.driver.execute_script(js_get_state)
                
                # 检查页码或内容是否变化
                if state_before['pageNum'] and state_after['pageNum']:
                    if state_after['pageNum'] != state_before['pageNum']:
                        return True
                
                if state_before['titles'] != state_after['titles']:
                    return True
            
            # 检查是否触发了验证码
            if '滑动验证' in self.driver.page_source:
                print('    ⚠ 翻页触发验证,等待手动处理...')
                time.sleep(30)
                return True  # 假设用户会处理验证码
            
            return False
            
        except Exception as e:
            print(f'    [调试] 翻页过程异常: {e}')
            return False
    
    def run(self, start_list_page=1, max_list_pages=1, max_communities=5):
        """
        运行爬虫
        
        Args:
            start_list_page: 列表页起始页码
            max_list_pages: 爬取的列表页数量
            max_communities: 最多爬取的小区数量
        """
        try:
            # 初始化
            if not self.init_driver():
                return
            
            if not self.init_csv():
                return
            
            print(f'{"="*80}')
            print(f'开始爬取房天下成交数据')
            print(f'列表页: 第{start_list_page}页 ~ 第{start_list_page + max_list_pages - 1}页')
            print(f'最多爬取小区数: {max_communities}')
            print(f'输出文件: {self.output_file}')
            print(f'{"="*80}\n')
            
            # 1. 从列表页提取详情链接
            detail_urls = self.extract_list_page_urls(start_list_page, max_list_pages)
            
            if not detail_urls:
                print('未找到任何详情页链接')
                return
            
            # 2. 逐个爬取小区数据
            community_count = 0
            for i, url in enumerate(detail_urls, 1):
                if community_count >= max_communities:
                    print(f'\n已达到最大小区数限制 ({max_communities})')
                    break
                
                print(f'\n[{i}/{len(detail_urls)}] 正在处理第 {i} 个小区...')
                saved = self.parse_community_deals(url)
                
                # 如果返回-1,表示浏览器窗口关闭,停止爬取
                if saved == -1:
                    print('\n⚠ 检测到浏览器窗口关闭,停止爬取')
                    break
                
                if saved > 0:
                    community_count += 1
                
                # 小区间隔
                time.sleep(0.5)
            
            print(f'\n{"="*80}')
            print(f'爬取完成!')
            print(f'处理小区数: {community_count}')
            print(f'总共保存: {self.total_count} 条有效数据')
            print(f'数据文件: {self.output_file}')
            print(f'{"="*80}')
            
        except Exception as e:
            print(f'\n✗ 爬虫运行失败: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            # 关闭CSV文件
            if self.csv_file:
                try:
                    self.csv_file.close()
                    print('\n✓ CSV文件已关闭')
                except:
                    pass
            
            # 关闭浏览器
            if self.driver:
                try:
                    self.driver.quit()
                    print('✓ 浏览器已关闭')
                except:
                    pass

if __name__ == '__main__':
    # ========== 配置参数 ==========
    # 基础URL - 不同城市的房天下网站
    # 北京: https://esf.fang.com
    # 天津: https://tj.esf.fang.com
    # 上海: https://sh.esf.fang.com
    # 广州: https://gz.esf.fang.com
    # 深圳: https://sz.esf.fang.com
    # 其他城市格式: https://{城市拼音}.esf.fang.com
    
    BASE_URL = 'https://tj.esf.fang.com'  # 修改这里切换城市
    OUTPUT_FILE = 'community_deals.csv'
    
    # 创建爬虫实例
    crawler = CombinedCrawler(
        base_url=BASE_URL,
        output_file=OUTPUT_FILE
    )
    
    # ========== 使用说明 ==========
    # 1. 从列表第1页开始，爬取3页列表，每页30个小区，最多100个小区
    #    crawler.run(start_list_page=1, max_list_pages=3, max_communities=100)
    #
    # 2. 从列表第5页开始，爬取2页
    #    crawler.run(start_list_page=5, max_list_pages=2, max_communities=50)
    #
    # 3. 爬取大量小区 (注意:会花费较长时间)
    #    crawler.run(start_list_page=1, max_list_pages=10, max_communities=300)
    # =============================
    
    crawler.run(
        start_list_page=1,
        max_list_pages=100,
        max_communities=3000
    )
