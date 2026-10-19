"""주문 금액 계산 개선 예제: 입력 검증, 정확한 금액 계산, 쿠폰 정규화."""

from decimal import Decimal, ROUND_DOWN, localcontext


# 변경: 등급별 할인율과 쿠폰 금액을 한곳에 모아 의미와 수정 위치를 명확히 합니다.
# 실제 등급 명칭은 주어지지 않았으므로 임의로 VIP 등의 이름을 붙이지 않습니다.
DISCOUNT_RATES = {
    1: Decimal("0.05"),
    2: Decimal("0.10"),
    3: Decimal("0.20"),
}
COUPON_AMOUNT = Decimal("3000")


def calc_order(
    u_type: int,
    price: int | float | Decimal,
    qty: int,
    coupon: str,
) -> int:
    """회원 할인 후 쿠폰을 차감한 최종 금액을 정수로 반환합니다.
    | 표시는 or을 의미
    
    등급은 1/2/3, 단가는 0 이상의 유한한 숫자, 수량은 양의 정수입니다.
    쿠폰은 YES/NO를 받으며 대소문자와 앞뒤 공백을 무시합니다.
    최종 금액은 최소 0원이며, 소수점 이하는 마지막에 한 번 버립니다.
    잘못된 자료형은 TypeError, 허용 범위 밖의 값은 ValueError로 알립니다.
    """
    # 변경: bool도 int의 하위 타입이므로 True가 1등급으로 처리되지 않게 합니다.
    if isinstance(u_type, bool) or not isinstance(u_type, int):
        raise TypeError("회원 등급은 정수여야 합니다.")
    if u_type not in DISCOUNT_RATES:
        raise ValueError("회원 등급은 1, 2, 3 중 하나여야 합니다.")

    # 변경: 계산 전에 단가와 수량을 각각 검증하여 음수끼리의 곱도 차단합니다.
    if isinstance(price, bool) or not isinstance(price, (int, float, Decimal)):
        raise TypeError("단가는 int, float 또는 Decimal이어야 합니다.")
    # float를 직접 Decimal로 바꾸지 않고 문자열을 거쳐 이진 소수 오차를 줄입니다.
    decimal_price = Decimal(str(price))
    if not decimal_price.is_finite() or decimal_price < 0:
        raise ValueError("단가는 0 이상의 유한한 숫자여야 합니다.")

    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("수량은 정수여야 합니다.")
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")

    # 변경: 'yes', ' YES '도 적용하되 오타는 조용히 무시하지 않습니다.
    if not isinstance(coupon, str):
        raise TypeError("쿠폰은 YES 또는 NO 문자열이어야 합니다.")
    normalized_coupon = coupon.strip().upper()
    if normalized_coupon not in {"YES", "NO"}:
        raise ValueError("쿠폰은 YES 또는 NO여야 합니다.")

    # 변경: Decimal로 계산하고 큰 금액도 중간에 반올림되지 않도록 정밀도를 확보합니다.
    price_parts = decimal_price.as_tuple()
    required_precision = (
                           len(price_parts.digits) + len(str(qty)) + max(0, price_parts.exponent) + 4
                          )
    with localcontext() as context:
        context.prec = max(28, required_precision)
        total = decimal_price * qty
        total *= Decimal("1") - DISCOUNT_RATES[u_type]
        if normalized_coupon == "YES":
            total -= COUPON_AMOUNT

        # 유지/명확화: 쿠폰 초과 할인은 0원으로, 소수점은 최종 단계에서 버립니다.
        total = max(total, Decimal("0"))
        return int(total.to_integral_value(rounding=ROUND_DOWN))


# 변경: 다른 파일에서 import할 때 예제 계산과 출력이 실행되지 않게 합니다.
if __name__ == "__main__":
    result = calc_order(1, 100, 20, "yes")
    print(f"최종 결제 금액: {result:,}원")
