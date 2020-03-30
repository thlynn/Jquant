
class OKExDM:

    def __init__(self, url, access_key, secret_key):
        self.__url = url
        self.__access_key = access_key
        self.__secret_key = secret_key
        
    def send_contract_order(self, client_oid, instrument_id, dir_off, order_type
                            price, size, match_price, leverage):
        """
        :client_oid     由您设置的订单ID来识别您的订单 ,类型为字母（大小写）+数字或者纯字母（大小写）， 1-32位字符
        :instrument_id  合约ID，如BTC-USD-180213
        :type(dir_off)  1:开多2:开空3:平多4:平空
        :order_type     参数填数字，0：普通委托（order type不填或填0都是普通委托） 1：只做Maker（Post only） 2：全部成交或立即取消（FOK） 3：立即成交并取消剩余（IOC)
        :price          每张合约的价格
        :size           买入或卖出合约的数量（以张计数）
        :match_price    是否以对手价下单(0:不是 1:是)，默认为0，当取值为1时。price字段无效，当以对手价下单，order_type只能选择0:普通委托
        :leverage       杠杆倍数，1-100的整数
        """
        
        params = {"instrument_id": instrument_id,
                  "type": dir_off,
                  "price": price,
                  "size": size,
                  "match_price": match_price
                  "leverage": leverage}
        if order_type:
            params['order_type'] = order_type
        if client_oid:
            params['client_oid'] = client_oid
    
        request_path = '/api/futures/v3/order'
        return api_key_post(self.__url, request_path, params, self.__access_key, self.__secret_key)