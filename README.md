# 介绍
本项目为 Python3 版本的 LukSDK，可直接引入使用，其中提供了需接入接口的通用实现，仅需结合业务逻辑将其返回即可。

> 仅需将 HTTP 请求转换为对应结构体后调用相关函数并填充返回值即可，关于参数的校验等行为交由 SDK 内部处理。

# Go Mod
可通过以下方式引入依赖

```shell
go get -u github.com/kercylan98/project-luksdk-go
```

# 示例代码
```python
from typing import Optional
from sdk import GetChannelTokenRequest, SDK, GetChannelTokenResponse

def main():
    # 初始化 SDK
    sdk = SDK("123456")

    # 来自 SDK 请求的参数结构
    request = GetChannelTokenRequest(1000,"123456789", "",167456789, "")
    request.sign = sdk.generate_signature(request)

    # 处理请求
    def request_handler(_: GetChannelTokenRequest) -> tuple[Optional['GetChannelTokenResponse'], Optional['Exception']]:
        # 业务逻辑
        return GetChannelTokenResponse("token", 7200), None
        # return None, Exception("error")

    resp = sdk.get_channel_token(request, request_handler)

    # 将 resp 作为 JSON 写入 HTTP 响应
    print(resp.code)
    print(resp.msg)
    print(resp.data)

if __name__ == "__main__":
    main()
```