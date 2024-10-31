import hashlib
import json
from typing import List, Dict, Any, Optional, TypeVar, Callable, Tuple

from pydantic import BaseModel

NotifyType = int
Action = int

Q = TypeVar('Q')  # Request 泛型类型
T = TypeVar('T')  # Response 泛型类型

RequestHandler = Callable[[Q], tuple[Optional[T], Optional[Exception]]]

class SDK:
    def __init__(self, sign_secret: str):
        self.sign_secret = sign_secret

    def verify_signature(self, sign: str, params: Any) -> None:
        """验证签名"""
        verify = signature(self.sign_secret, params)
        if verify != sign:
            raise ValueError("Invalid signature")

    def generate_signature(self, params: Any) -> str:
        """生成签名"""
        return signature(self.sign_secret, params)

    def get_channel_token(self, request: 'GetChannelTokenRequest', *success_handler: 'RequestHandler') -> 'Response':
        """CFGame向接入方获取用户令牌"""
        return self.generate_handler(request.sign, request, *success_handler)

    def refresh_channel_token(self, request: 'RefreshChannelTokenRequest', *success_handler: 'RequestHandler') -> 'Response':
        """刷新用户令牌过期时间"""
        return self.generate_handler(request.sign, request, *success_handler)

    def get_channel_user_info(self, request: 'GetChannelUserInfoRequest', *success_handler: 'RequestHandler') -> 'Response':
        """获取渠道用户信息"""
        return self.generate_handler(request.sign, request, *success_handler)

    def create_channel_order(self, request: 'CreateChannelOrderRequest', *success_handler: 'RequestHandler') -> 'Response':
        """向渠道下订单"""
        return self.generate_handler(request.sign, request, *success_handler)

    def notify_channel_order(self, request: 'NotifyChannelOrderRequest', *success_handler: 'RequestHandler') -> 'Response':
        """下注开奖通知结果"""
        return self.generate_handler(request.sign, request, *success_handler)

    def notify_game(self, request: 'NotifyGameRequest', *success_handler: 'RequestHandler') -> 'Response':
        """向渠道通知游戏状态"""
        return self.generate_handler(request.sign, request, *success_handler)

    def generate_handler(self, sign: str, request: Any, *success_handler: 'RequestHandler') -> 'Response':
        verify = signature(self.sign_secret, request)
        response = Response()
        if verify != sign:
            return response.with_error(ErrInvalidSignature, request.sign + " <=> " + verify)

        response.data, err = success_handler[0](request)
        if err is not None:
            return response.with_error(ErrChannelDataException, err.__str__())

        return response.with_data(response.data)

def signature(sign_secret: str, params: Any) -> str:
    params_map = cast_to_signature_params(params)
    return generate_signature(sign_secret, params_map)


def generate_signature(sign_secret: str, params: Dict[str, str]) -> str:
    keys = sorted(params.keys())

    signature_parts = []
    for k in keys:
        value = params[k]
        if value:
            signature_parts.append(f"{k}={value}")

    signature_string = "&".join(signature_parts) + f"&key={sign_secret}"

    hash_result = hashlib.md5(signature_string.encode('utf-8')).hexdigest().upper()

    return hash_result


def cast_to_signature_params(obj: Any) -> Dict[str, str]:
    result = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            result[str(key)] = str(value)
    else:
        # 遍历对象的属性
        for attr, value in obj.dict(exclude_unset=True).items():
            if value and attr != "sign":  # 跳过 "sign" 字段和空字段
                if isinstance(value, (dict, list, tuple, set, type)) or callable(value):
                    continue  # 跳过复杂类型
                result[attr] = str(value)

    return result


class NotifyTypes:
    NOTIFY_TYPE_START_BEFORE = 1  # 游戏开始前状态
    NOTIFY_TYPE_GAMING = 2         # 游戏开始中状态
    NOTIFY_TYPE_END = 3            # 游戏结束状态

class Actions:
    ACTION_JOIN_GAME = 1          # 加入游戏操作
    ACTION_EXIT_GAME = 2          # 退出游戏操作
    ACTION_SETTING_GAME = 3       # 设置游戏操作
    ACTION_KICK_OUT = 4           # 踢人操作
    ACTION_START_GAME = 5         # 开始游戏操作
    ACTION_PREPARE = 6             # 准备操作
    ACTION_CANCEL_PREPARE = 7     # 取消准备操作
    ACTION_GAME_END = 8           # 游戏结束操作

class GetChannelTokenRequest(BaseModel):
    c_id: int = 0
    c_uid: str = ""
    code: str = ""
    timestamp: int = 0
    sign: str = ""

class GetChannelTokenResponse(BaseModel):
    token: str = ""
    left_time: int = 0

class RefreshChannelTokenRequest(BaseModel):
    c_id: int = 0
    c_uid: str = ""
    token: str = ""
    timestamp: int = 0
    sign: str = ""
    left_time: int = 0

class RefreshChannelTokenResponse(BaseModel):
    token: str = ""
    left_time: int = 0

class GetChannelUserInfoRequest(BaseModel):
    g_id: int = 0
    c_id: int = 0
    c_uid: str = ""
    token: str = ""
    timestamp: int = 0
    sign: str = ""

class GetChannelUserInfoResponse(BaseModel):
    c_uid: str = ""
    name: str = ""
    avatar: str = ""
    coins: int = 0

class CreateChannelOrderRequestEntry(BaseModel):
    c_id: int = 0
    c_uid: str = ""
    c_room_id: str = ""
    g_id: int = 0
    coins_cost: int = 0
    score_cost: int = 0
    game_order_id: str = ""
    token: str = ""
    timestamp: int = 0

class CreateChannelOrderRequest(BaseModel):
    sign: str = ""
    data: List[CreateChannelOrderRequestEntry] = []
    timestamp: int = 0
    nonce: str = ""

class CreateChannelOrderResponseEntry(BaseModel):
    c_uid: str = ""
    order_id: str = ""
    coins: int = 0
    status: int = 0

CreateChannelOrderResponse = List[CreateChannelOrderResponseEntry]

class NotifyChannelOrderRequestEntry(BaseModel):
    c_id: int = 0
    c_uid: str = ""
    g_id: int = 0
    game_order_id: str = ""
    token: str = ""
    coins_cost: int = 0
    coins_award: int = 0
    score_cost: int = 0
    score_award: int = 0
    timestamp: int = 0

class NotifyChannelOrderRequest(BaseModel):
    sign: str = ""
    data: List[NotifyChannelOrderRequestEntry] = []
    timestamp: int = 0
    nonce: str = ""

class NotifyChannelOrderResponseEntry(BaseModel):
    c_uid: str = ""
    order_id: str = ""
    coins: int = 0
    score: int = 0

NotifyChannelOrderResponse = List[NotifyChannelOrderResponseEntry]

class NotifyGameRequest(BaseModel):
    c_id: int = 0
    g_id: int = 0
    notify_type: NotifyType = 0
    ext: str = ""
    data: str = ""
    timestamp: int = 0
    sign: str = ""

    def get_start_before(self) -> Optional['NotifyGameRequestStartBefore']:
        return json.loads(self.data, object_hook=lambda d: NotifyGameRequestStartBefore(**d))

    def get_gaming(self) -> Optional['NotifyGameRequestGaming']:
        return json.loads(self.data, object_hook=lambda d: NotifyGameRequestGaming(**d))

    def get_end(self) -> Optional['NotifyGameRequestEnd']:
        return json.loads(self.data, object_hook=lambda d: NotifyGameRequestEnd(**d))

class NotifyGameRequestStartBefore(BaseModel):
    room_id: str = ""
    round_id: str = ""
    player_ready_status: Dict[str, bool] = {}
    notify_action: Action = 0
    game_setting: str = ""

class NotifyGameRequestGaming(BaseModel):
    room_id: str = ""
    round_id: str = ""
    player_num: int = 0
    player_uids: List[str] = []
    notify_action: Action = 0

class NotifyGameRequestEnd(BaseModel):
    room_id: str = ""
    round_id: str = ""
    rank: List[str] = []
    is_force_end: bool = False
    notify_action: Action = 0

class NotifyGameResponse(BaseModel):
    pass

class Response(BaseModel):
    code: int = 0
    msg: str = ""
    data: Optional[T] = None

    def with_error(self, err: Exception, msg: Optional[str] = None) -> 'Response':
        self.code = -1  # Default error code
        self.msg = str(err) if msg is None else f"{str(err)}, {msg}"
        return self

    def with_data(self, data: T) -> 'Response':
        self.data = data
        if self.code == 0:
            self.msg = "成功"
        return self

    def suc(self) -> bool:
        return self.code == 0

Req = TypeVar('Req')
Res = TypeVar('Res')

def generate_handler(sign_secret: str, request_sign: str, request: Req, *success_handler: Callable[[Req], Tuple[Res, Optional[Exception]]]) -> Response:
    verify = signature(sign_secret, request)
    response = Response()

    if verify != request_sign:
        return response.with_error(ErrInvalidSignature, f"Expected {request_sign}, got {verify}")

    for handler in success_handler:
        data, err = handler(request)
        if err:
            return response.with_error(ErrChannelDataException, str(err))

        response.data = data

    return response


class CustomError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code

error_map = {}

def reg_error(code, msg):
    err = CustomError(code, msg)
    error_map[err] = code
    return err

ErrInvalidParams = reg_error(1000, "invalid params")          # 参数有误
ErrInvalidChannel = reg_error(1001, "invalid channel")          # 渠道有误
ErrInvalidChannelOrder = reg_error(1002, "invalid channel request")  # 渠道请求异常
ErrInvalidSignature = reg_error(1003, "invalid signature")    # 签名有误
ErrInvalidGame = reg_error(1004, "invalid game")              # 游戏有误
ErrChannelDataException = reg_error(1005, "channel data exception")  # 渠道返回数据异常
ErrRepeatOrder = reg_error(1006, "repeat order")              # 重复下订单
ErrOrderFailed = reg_error(1007, "order failed")              # 下单失败
ErrOrderNotExist = reg_error(1008, "order not exist")         # 订单不存在

