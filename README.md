# 介绍
本项目为 Python3 版本的 LukSDK，可直接引入使用，其中提供了需接入接口的通用实现，仅需结合业务逻辑将其返回即可。

> 仅需将 HTTP 请求转换为对应结构体后调用相关函数并填充返回值即可，关于参数的校验等行为交由 SDK 内部处理。

# 安装
```shell
pip install luk-sdk
```

# 示例代码
```python
from luk_sdk.sdk import *
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


sdk = SDK("......", "https://......")

@app.route("/sdk/get_channel_token", methods=["POST"])
def get_channel_token():
    request_obj = GetChannelTokenRequest.model_validate(request.json)

    response = sdk.get_channel_token(request_obj,lambda _: (GetChannelTokenResponse(token="token", left_time=7200), None))

    logging.info("get_channel_token", extra={"request": request_obj, "response": response})
    return jsonify(response.model_dump())

@app.route("/sdk/refresh_channel_token", methods=["POST"])
def refresh_channel_token():
    request_obj = RefreshChannelTokenRequest.model_validate(request.json)

    response = sdk.refresh_channel_token(request_obj,
        lambda req: (RefreshChannelTokenResponse(
            token="my-token",
            left_time=7200
        ), None))

    logging.info("refresh_channel_token", extra={"request": request_obj, "response": response})
    return jsonify(response.model_dump())

@app.route("/sdk/get_channel_user_info", methods=["POST"])
def get_channel_user_info():
    request_obj = GetChannelUserInfoRequest.model_validate(request.json)

    response = sdk.get_channel_user_info(request_obj, lambda req: (GetChannelUserInfoResponse(
        c_uid=req.c_uid,
        name="my-name",
        avatar="",
        coins=100000
    ), None))

    logging.info("get_channel_user_info", extra={"request": request_obj, "response": response})
    return jsonify(response.model_dump())

@app.route("/sdk/create_channel_order", methods=["POST"])
def create_channel_order():
    request_obj = CreateChannelOrderRequest.model_validate(request.json)

    response = sdk.create_channel_order(request_obj, lambda req: ([
        CreateChannelOrderResponseEntry(
            c_uid=datum.c_uid,
            order_id=datum.game_order_id,
            coins=100000,
            status=1
        ) for datum in req.data
    ], None))

    logging.info("create_channel_order", extra={"request": request_obj, "response": response})
    return jsonify(response.model_dump())

@app.route("/sdk/notify_channel_order", methods=["POST"])
def notify_channel_order():
    request_obj = NotifyChannelOrderRequest.model_validate(request.json)

    response = sdk.notify_channel_order(request_obj, lambda req: ([
        NotifyChannelOrderResponseEntry(
            c_uid=datum.c_uid,
            order_id=datum.game_order_id,
            coins=100000,
            score=100000
        ) for datum in req.data
    ], None))

    return jsonify(response.model_dump())

@app.route("/sdk/notify_game", methods=["POST"])
def notify_game():
    request_obj = NotifyGameRequest.model_validate(request.json)

    response = sdk.notify_game(request_obj, lambda req: (NotifyGameResponse(), None))

    return jsonify(response.model_dump())

if __name__ == "__main__":
    app.run(port=8080)
```