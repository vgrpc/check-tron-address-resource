import json

import requests

# 波场节点API
TRON_API = "https://api.trongrid.io"
API_KEY = "5xxxf"
# 充值能量功能参数
TRON_RES_BOT_API_KEY = "bxxx3a87"
# TelegramBot Token 用来发送通知
BOT_TOKEN = "6481111111:AAHxxxxxxxx"
ADMIN_CHAT_ID = 1405597912

# proxies = {'http': "socks5://127.0.0.1:7890", 'https': "socks5://127.0.0.1:7890"}
proxies = {}


class Check:
    def __init__(self, energy, bandwidth):
        self.energy = energy
        self.bandwidth = bandwidth


class Recharge:
    def __init__(self, energy, bandwidth):
        self.energy = energy
        self.bandwidth = bandwidth


class AddressInfo:
    def __init__(self, address, action, check, recharge):
        self.address = address
        self.action = action
        self.check = Check(**check)
        self.recharge = Recharge(**recharge)


def get_account_resource(address):
    url = TRON_API + "/wallet/getaccountresource"
    params = {"address": address, "visible": True}
    headers = {"Content-Type": "application/json", "TRON-PRO-API-KEY": API_KEY}
    response = requests.get(url, params=params, headers=headers, timeout=5, proxies=proxies)
    if response.status_code != 200:
        print(response.text)
        return None
    return response.json()


def recharge_energy_resource(address, resource_value):
    """
    充值能量
    :param address: 接收资源的地址
    :param resource_value: 充值数量
    :return:
    """
    # 租用时长-数量
    rent_duration = 1
    # 租用时长-单位 HOUR-小时 DAY-天
    rent_time_unit = "HOUR"
    url = "https://teba-api.vgrpc.com/orderResource"
    params = {
        "apiKey": TRON_RES_BOT_API_KEY,
        "rentDuration": rent_duration,
        "rentTimeUnit": rent_time_unit,
        "resourceValue": resource_value,
        "receiveAddress": address
    }
    response = requests.get(url, params=params, timeout=10, proxies=proxies)
    print("下单能量结果-" + response.text)


def check_energy(address_info: AddressInfo, account_resource):
    address = address_info.address
    if 'EnergyLimit' in account_resource:
        energy_limit = account_resource['EnergyLimit']
    else:
        energy_limit = 0

    if 'EnergyUsed' in account_resource:
        energy_used = account_resource['EnergyUsed']
    else:
        energy_used = 0

    remain_energy = energy_limit - energy_used
    print("剩余能量:" + str(remain_energy))
    if remain_energy < address_info.check.energy:
        # 获取需要执行的操作
        actions = address_info.action
        for action in actions:
            print(action)
            try:
                if action == "发送提示":
                    send_trigger_tips(address_info, resource_type="能量")
                elif action == "自动充值":
                    # 开始补充能量
                    recharge_energy_resource(address, address_info.recharge.energy)
            except Exception as e:
                print("处理出现异常了", e)


def check_bandwidth(address_info: AddressInfo, account_resource):
    if 'NetLimit' in account_resource:
        net_limit = account_resource['NetLimit']
    else:
        net_limit = 0

    if 'NetUsed' in account_resource:
        net_used = account_resource['NetUsed']
    else:
        net_used = 0

    remain_resource = net_limit - net_used
    print("剩余带宽:" + str(remain_resource))
    if remain_resource < address_info.check.bandwidth:
        # 获取需要执行的操作
        actions = address_info.action
        for action in actions:
            print(action)
            try:
                if action == "发送提示":
                    send_trigger_tips(address_info, resource_type="带宽")
                elif action == "自动充值":
                    # 开始补充能量
                    print("暂时未找到带宽api，手动充值吧")
            except Exception as e:
                print("处理出现异常了", e)


def send_trigger_tips(address_info: AddressInfo, resource_type):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"<b>地址剩余资源不足</b>\n地址:<code>{address_info.address}</code>\n资源类型:{resource_type}"
    params = {
        "chat_id": ADMIN_CHAT_ID,
        "parse_mode": "HTML",
        "text": text,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=params, headers=headers, timeout=5, proxies=proxies)
    print(response.text)


def check_address_resource(address_info: AddressInfo):
    address = address_info.address
    account_resource = get_account_resource(address=address)
    if account_resource is None:
        print(f"获取地址[{address}]资源失败")
        return
    # print(account_resource)
    # 检查能量
    try:
        check_energy(address_info, account_resource)
    except Exception as e:
        print("检查能量出现异常了", e)
        pass
    # 检查带宽
    try:
        check_bandwidth(address_info, account_resource)
    except Exception as e:
        print("检查带宽出现异常了", e)
        pass


if __name__ == '__main__':
    with open('./check_address.json', 'r', encoding='utf-8') as file:
        # 读取文件内容
        address_list_str = file.read()
    address_list = json.loads(address_list_str)
    infos = [AddressInfo(**item) for item in address_list]

    for address_obj in infos:
        check_address_resource(address_obj)
