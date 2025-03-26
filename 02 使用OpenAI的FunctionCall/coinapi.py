import time
import requests
import config


def coin_current_rates(coin_id: str) -> str:
    """获取指定币种的美元汇率

    Args:
        coin_id (str): 资产ID 例如 BTC

    Returns:
        str: 自然语言描述
    """
    current_timezone = time.tzname[time.daylight]

    route = f"/exchangerate/{coin_id}/USD"
    url = f"{config.COINAPI_BASE_URL}{route}"
    response = requests.get(
        url=url,
        headers={"X-CoinAPI-Key": config.COINAPI_API_KEY, "Accept": "application/json"},
    )

    response_json = response.json()

    USD_rate = response_json["rate"]

    return f"UTC时间：{response_json["time"].split(".")[0]} 需要考虑到用户时区{current_timezone}, {coin_id}比美元的汇率为 1/{coin_id}={USD_rate}/USD"


def test():
    res = coin_current_rates("BTC")
    print(res)


if __name__ == "__main__":
    test()
