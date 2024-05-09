# 导入所需的库
import time  # 处理时间相关操作的库
import re  # 正则表达式模块，用于文本匹配
import paramiko  # 用于SSH连接和SFTP传输的库
from ncclient import manager  # 用于NETCONF通信的库
from ncclient.xml_ import to_ele  # 用于构建XML元素的工具
from datetime import datetime  # 用于处理日期和时间的库
from threading import Thread  # 多线程模块，用于并发执行任务
from config import parameter_dict, netconf1  # 导入配置信息


class SwitchMonitor:
    def __init__(self):  #这里是   __init__  不是 int ！！！！！！！！！
        # 初始化方法，在类实例化时自动执行
        # 建立与设备的SSH连接
        self.ssh = paramiko.SSHClient()  # 创建SSH客户端对象
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 设置自动添加缺失的主机密钥策略
        self.ssh.connect("10.1.0.6", 22, "python", "Huawei@123", look_for_keys=False, allow_agent=False)
        # 上面这一句！！！！！后半截需要手敲！！！！！！！！
        # 连接到目标设备，指定IP地址、端口号、用户名、密码等参数
        self.vty = self.ssh.invoke_shell()  # 创建SSH shell对象，用于命令交互
        # 调用invoke_shell()方法，返回一个可交互的SSH shell
        self.send_command("screen-length 0 temporary")  # 发送命令，将屏幕长度临时设置为0
        print("SSH连接建立成功")  # 打印连接建立成功的提示信息
    # 变量含义：
    # self.ssh: SSH客户端对象，用于建立SSH连接。
    # paramiko.AutoAddPolicy(): 设置自动添加缺失的主机密钥策略，允许动态添加新的主机密钥。
    # self.ssh.connect(...): 连接到目标设备，指定设备的IP地址、端口号、用户名、密码等连接参数。
    # self.vty: SSH
    # shell对象，通过调用invoke_shell()
    # 方法创建，用于进行命令交互。
    # self.send_command(...): 发送命令到SSH
    # shell的方法，这里用于将屏幕长度临时设置为0。
    # print("SSH连接建立成功"): 打印连接建立成功的提示信息。

    def send_command(self, command):
        # 实例方法，用于向SSH shell发送命令并获取响应
        self.vty.send(command + "\n")  # 向SSH shell发送命令，添加换行符表示回车
        time.sleep(1)  # 等待1秒，确保命令执行完成并获取到完整的响应
        return self.vty.recv(65535).decode("utf-8")  # 从SSH shell接收响应，解码为UTF-8格式的字符串


    def netconf(self, xml):
        # 实例方法，用于执行NETCONF操作
        # 变量含义：
        # 连接到NETCONF服务器的配置参数：
        # - host: NETCONF服务器的IP地址
        # - port: NETCONF服务器的端口号，通常为830
        # - username: 连接的用户名
        # - password: 连接的密码
        # - allow_agent: 是否允许使用SSH代理进行认证
        # - hostkey_verify: 是否验证主机密钥
        # - device_params: 指定设备参数，这里使用了一个自定义的名称为"huaweiyang"的设备参数
        # 这里使用ncclient库提供的manager.connect()方法建立NETCONF连接，并使用rpc()方法发送XML RPC请求
        manager.connect(
            host="10.1.0.6",         # NETCONF服务器的IP地址
            port=830,                 # NETCONF服务器的端口号
            username="netconf",       # 连接的用户名
            password="Huawei@123",    # 连接的密码
            allow_agent=False,        # 不允许使用SSH代理进行认证
            hostkey_verify=False,     # 不验证主机密钥
            device_params={"name": "huaweiyang"}  # 自定义设备参数，名称为"huaweiyang"
        ).rpc(to_ele(xml))  # 使用rpc()方法发送XML RPC请求
        # 输出设置成功的提示信息
        print(xml, "设置成功")

    def monitor_parameters(self):
        # 实例方法，用于定时监控设备参数

        while True:
            parameter_data = []  # 用于存储每次监控的参数数据
            # 遍历配置中定义的参数
            for i in parameter_dict.keys():
                # 发送与参数关联的命令，并使用正则表达式提取结果
                pat = self.send_command(parameter_dict[i]["command"])
                res = re.compile(parameter_dict[i]["re"]).findall(pat)
                # 对于fan_state参数，处理特定情况
                if i == "fan_state":
                    res = res if res else "所有风扇故障"
                parameter_data.append(f"{i}:{res}")
            # 打印收集的参数数据
            print("\n".join(parametler_data))
            time.sleep(60 * 5)  # 每隔10秒进行一次参数监控,考试的时候将时间修改为 60 * 5

        # 变量含义：
        # - parameter_data: 用于存储每次监控的参数数据的列表
        # - parameter_dict: 包含设备参数配置的字典，定义了每个参数的相关信息
        # - i: 遍历parameter_dict字典时当前参数的键值
        # - self.send_command: 调用SwitchMonitor类中的send_command方法，用于向设备发送命令
        # - pat: 存储从设备返回的命令执行结果的字符串
        # - res: 存储通过正则表达式匹配提取出的参数值的列表

    def download(self):
        # 实例方法，用于定时从设备下载文件

        while True:
            # 通过SFTP从设备下载文件
            with paramiko.Transport(("10.1.0.6", 22)) as t:
                t.connect(username="python", password="Huawei@123")
                sftp = paramiko.SFTPClient.from_transport(t)
                # 从设备的/vrpcfg.zip路径下载文件，并以当前时间戳命名

                S_datatime = f""" <sys:set-current-datetime xmlns:sys="urn:ietf:params:xml:ns:yang:ietf-system">
  <sys:current-datetime>{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}</sys:current-datetime>
 </sys:set-current-datetime>"""
                self.netconf(xml=S_datatime)

                sftp.get("/vrpcfg.zip", f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_X_T1_AGG1.zip")
            time.sleep(60 * 60 *24)  # 每隔30秒进行一次文件下载 考试的时候将时间修改为 60 * 60 *24

        # 变量含义：
        # - paramiko.Transport: 创建SFTP传输通道的类
        # - t: SFTP传输通道的实例
        # - sftp: SFTP客户端的实例，通过from_transport()方法创建
        # - /vrpcfg.zip: 设备上的文件路径，即待下载的文件
        # - f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_X_T1_AGG1.zip": 以当前时间戳命名的本地文件名


    def start_monitoring(self):
        # 实例方法，用于启动监控参数和下载文件的两个线程

        Thread(target=self.monitor_parameters).start()  # 启动监控参数的线程
        Thread(target=self.download).start()  # 启动下载文件的线程

        # 变量含义：
        # - Thread: 多线程类，用于创建和管理线程
        # - target: 指定线程要执行的目标方法，这里分别为monitor_parameters和download
        # - self.monitor_parameters: 调用SwitchMonitor类中的monitor_parameters方法，用于参数监控
        # - self.download: 调用SwitchMonitor类中的download方法，用于文件下载


if __name__ == '__main__':
    # 主程序入口，当脚本被直接运行时执行以下代码

    # 为netconf1中的每个配置建立NETCONF连接
    for i in netconf1.values():
        SwitchMonitor().netconf(i)

    # 启动监控线程
    SwitchMonitor().start_monitoring()

    # 变量含义：
    # - __name__: Python特殊变量，表示当前模块的名称
    # - __main__: 当前模块的名称为__main__，表示脚本正在直接运行而非被导入
    # - netconf1.values(): 获取netconf1字典中的所有配置值（NETCONF连接配置）
    # - SwitchMonitor().netconf(i): 创建SwitchMonitor实例并为每个配置建立NETCONF连接
    # - SwitchMonitor().start_monitoring(): 创建SwitchMonitor实例并启动监控线程

