# 检测地址剩余资源

> 使用计划任务定时执行

```shell
pip3 install requests -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
```

### `check_address.json` 配置说明

> 使用JSON数组格式

|字段名|说明|其他备注|
|:----|:----|:----|
|action|触发后动作 字符串列表|目前只支持: `发送提示` `自动充值`|

#### 示例
```json5
[
  {
    // 监听地址
    "address": "TTxxxxxxxxxxxxxxxxxxxxxx",
    "action": [
      "发送提示",
      "自动充值"
    ],
    "check": {
      // 能量低于这个值就触发action
      "energy": 65000,
      // 带宽低于这个值就触发action
      "bandwidth": 500,
    },
    "recharge": {
      // 充值能量数量
      "energy": 65000,
      // 充值带宽数量
      "bandwidth": 500
    }
  }
]
```
