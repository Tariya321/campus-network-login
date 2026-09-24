import os
import configparser
import requests
from bs4 import BeautifulSoup
import time
import ddddocr
from typing import Optional

ocr = ddddocr.DdddOcr(show_ad=False)

max_attempt = 5
request_timeout = (5, 15)  # (connect timeout, read timeout), in seconds
username = None
password = None
u_ips = []  # 支持多个IP

ac_ip = "10.13.7.59"
pushPageId = "5bf74194-d2a8-4bb8-ac6b-8ff3e855f6a7"
ssid = "PUxzd1NzaWRQbGFjZWhvbGRlcj0="
url_prefix = "https://net-auth.shanghaitech.edu.cn:19008/portalpage/04b92f0a808c4d10b572642e3be564b2/20221024095238/pc/auth.html"

def get_user_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    username = config.get('UserConfig', 'username')
    password = config.get('UserConfig', 'password')
    
    # 读取所有的u_ip配置（支持以u_ip开头的字串, 例如u_ip_2, u_ip_3等），保留配置项名称
    u_ips = []
    for key in sorted(config.options('UserConfig')):
        if key.startswith('u_ip'):
            ip = config.get('UserConfig', key).strip()
            if ip:
                u_ips.append({'ip': ip, 'name': key})
    
    return username, password, u_ips

def set_user_config(username, password, u_ips):
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if(not config.has_section('UserConfig')):
        config.add_section('UserConfig')
    config.set('UserConfig', 'username', username)
    config.set('UserConfig', 'password', password)
    
    # 支持多个IP地址
    if isinstance(u_ips, str):
        u_ips = [u_ips]
    
    for i, ip in enumerate(u_ips):
        ip_value = ip if isinstance(ip, str) else ip['ip']
        if i == 0:
            config.set('UserConfig', 'u_ip', ip_value)
        else:
            config.set('UserConfig', f'u_ip_{i+1}', ip_value)
    
    with open('config.ini', 'w') as config_file:
        config.write(config_file)



def AcquireInternet(validcode: Optional[str], u_ip: str) -> bool:
    if not validcode:
        return False

    refer_url = url_prefix + "?ac-ip={acip}&uaddress={uip}&umac=null&authType=1&lang=zh_CN&ssid={sid}&pushPageId={pid}".format(acip=ac_ip, uip=u_ip, sid=ssid, pid=pushPageId)
    
    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'DNT': '1',
    'Origin': 'https://net-auth.shanghaitech.edu.cn:19008',
    'Pragma': 'no-cache',
    'Referer': refer_url,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    data = {
    'pushPageId': pushPageId,
    'userPass': password,
    'esn': '',
    'apmac': '',
    'armac': '',
    'authType': '1',
    'ssid': ssid,
    'uaddress': u_ip,
    'umac': 'null',
    'accessMac': '',
    'businessType': '',
    'acip': ac_ip,
    'agreed': '1',
    'registerCode': '',
    'questions': '',
    'dynamicValidCode': '',
    'dynamicRSAToken': '',
    'validCode': validcode,
    'userName': username,
    }
    try:
        response = requests.post(
            'https://net-auth.shanghaitech.edu.cn:19008/portalauth/login',
            headers=headers,
            data=data,
            timeout=request_timeout,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Login request failed for {u_ip}: {e}")
        return False

    time.sleep(3)
    return testInternet()

def getValidCode(u_ip: str) -> Optional[str]:
    refer_url = url_prefix + "?ac-ip={acip}&uaddress={uip}&umac=null&authType=1&lang=zh_CN&ssid={sid}&pushPageId={pid}".format(acip=ac_ip, uip=u_ip, sid=ssid, pid=pushPageId)
    timestamp = int(round(time.time() * 1000))
    # url = "https://net-auth.shanghaitech.edu.cn:19008/portalauth/verificationcode?date={t}&uaddress={uip}&umac=null&acip={acip}".format(t=timestamp,uip=u_ip,acip=ac_ip)

    img_headers = {
    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'PSESSIONID=',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Referer': refer_url,
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    params = {
    'date': timestamp,
    'uaddress': u_ip,
    'umac': 'null',
    'acip': ac_ip,
}

    try:
        img_response = requests.get(
            'https://net-auth.shanghaitech.edu.cn:19008/portalauth/verificationcode',
            params=params,
            headers=img_headers,
            timeout=request_timeout,
        )
        img_response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Verification-code request failed for {u_ip}: {e}")
        return None

    img = img_response.content
    if not img:
        print(f"  Verification-code response was empty for {u_ip}")
        return None

    try:
        validcode = ocr.classification(img).strip()
    except Exception as e:
        print(f"  Verification-code OCR failed for {u_ip}: {e}")
        return None

    if not validcode:
        print(f"  Verification-code OCR returned an empty result for {u_ip}")
        return None

    # print(validcode)
    return validcode

def testInternet() -> bool:
    try:
        r = requests.get('https://www.baidu.com', timeout=5)
        return True if r.status_code < 400 else False
    except Exception:
        return False


def main():
    '''
    if(testInternet() == True):
        print("Internet Connected")
        exit(0)
    else:
    '''
    if not u_ips:
        print("No IP addresses configured in config.ini")
        exit(-1)
    
    ip_list = [f"{item['ip']} ({item['name']})" for item in u_ips]
    print(f"Found {len(u_ips)} IP address(es) to login: {', '.join(ip_list)}")
    
    # 为每个IP尝试登录
    all_success = True
    for idx, u_ip_item in enumerate(u_ips, 1):
        u_ip = u_ip_item['ip']
        ip_name = u_ip_item['name']
        print(f"\n[{idx}/{len(u_ips)}] Attempting to login for IP: {u_ip} ({ip_name})")
        connection_flag = False
        attempt_count = 0
        
        while((not connection_flag) and (attempt_count < max_attempt)):
            if(AcquireInternet(getValidCode(u_ip), u_ip) == True):
                connection_flag = True
            else:
                print(f"  Attempt {attempt_count+1} failed for {u_ip} ({ip_name}). Try again later!")
                attempt_count += 1
                if attempt_count < max_attempt:
                    time.sleep(10)
        
        if connection_flag:
            print(f"  ✓ Successfully connected for IP: {u_ip} ({ip_name})")
        else:
            print(f"  ✗ Failed to connect for IP: {u_ip} ({ip_name}) after {max_attempt} attempts")
            all_success = False
    
    # 最终总结
    print("\n" + "="*50)
    if all_success:
        print("All IP addresses successfully connected!")
        exit(0)
    else:
        print("Some IP addresses failed to connect.")
        exit(-1)


if __name__ == '__main__':
    if(os.path.exists('config.ini')):
        username, password, u_ips = get_user_config()
    
    if(not username or not password or not u_ips):
        print("please edit config.ini to use")
        username = input("your student id: ")
        password = input("Password: ")
        
        # 支持输入多个IP地址
        print("(提示：可以从认证网页中的uaddress参数找到本机IP地址)")
        print("请输入IP地址，多个IP用逗号分隔，例如: 10.19.133.80,10.19.133.81")
        u_ip_input = input("IP address(es): ")
        u_ips = [ip.strip() for ip in u_ip_input.split(',') if ip.strip()]
        
        set_user_config(username, password, u_ips)
    main()
