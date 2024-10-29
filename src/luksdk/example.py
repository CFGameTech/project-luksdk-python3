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
