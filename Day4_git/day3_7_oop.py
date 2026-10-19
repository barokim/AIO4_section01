"""함수형 주문 계산 예제를 객체지향 구조로 리팩토링한 버전.

기존: calc_order(u_type, price, qty, coupon)가 검증과 계산을 모두 수행.
변경: Order는 주문 데이터와 검증, OrderCalculator는 금액 계산을 담당.
계산 규칙은 day3_7_improved.py와 같습니다. Python 3.10 이상에서 실행합니다.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, localcontext
from enum import IntEnum


class MemberGrade(IntEnum):
    """숫자로 전달하던 회원 등급을 이름으로 표현합니다.

    실제 등급 명칭이 없으므로 VIP 같은 업무상 의미를 임의로 부여하지 않습니다.
    IntEnum을 사용하여 기존의 정수 1, 2, 3도 계속 입력할 수 있습니다.
    """

    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3


@dataclass(frozen=True)
class Order:
    """주문 한 건을 표현하고, 생성할 때 잘못된 입력을 거부합니다.

    dataclass가 필드에 맞는 __init__과 __repr__ 등을 자동 생성합니다.
    frozen=True는 생성 후 일반적인 필드 대입을 막습니다.
    따라서 검증된 수량을 나중에 order.qty = -1처럼 바꾸지 못합니다.
    타입 힌트는 설명을 위한 것이므로 실제 입력 검증은 아래에서 수행합니다.
    """

    u_type: int
    price: int | float | Decimal
    qty: int
    coupon: str

    def __post_init__(self) -> None:
        """자동 생성된 __init__ 직후 실행되는 검증 및 정규화 단계입니다."""
        # self는 지금 생성 중인 주문 객체입니다.
        # bool은 int의 하위 타입이므로 True가 1등급으로 통과하지 않게 합니다.
        if isinstance(self.u_type, bool) or not isinstance(self.u_type, int):
            raise TypeError("회원 등급은 정수여야 합니다.")
        try:
            grade = MemberGrade(self.u_type)
        except ValueError:
            raise ValueError("회원 등급은 1, 2, 3 중 하나여야 합니다.") from None

        if isinstance(self.price, bool) or not isinstance(
            self.price, (int, float, Decimal)
        ):
            raise TypeError("단가는 int, float 또는 Decimal이어야 합니다.")
        # Decimal(2.3) 대신 Decimal(str(2.3))으로 이진 소수 오차 유입을 줄입니다.
        decimal_price = Decimal(str(self.price))
        if not decimal_price.is_finite() or decimal_price < 0:
            raise ValueError("단가는 0 이상의 유한한 숫자여야 합니다.")

        if isinstance(self.qty, bool) or not isinstance(self.qty, int):
            raise TypeError("수량은 정수여야 합니다.")
        if self.qty <= 0:
            raise ValueError("수량은 1 이상이어야 합니다.")

        if not isinstance(self.coupon, str):
            raise TypeError("쿠폰은 YES 또는 NO 문자열이어야 합니다.")
        normalized_coupon = self.coupon.strip().upper()
        if normalized_coupon not in {"YES", "NO"}:
            raise ValueError("쿠폰은 YES 또는 NO여야 합니다.")

        # 생성 중에만 검증된 값으로 정규화합니다.
        # frozen 객체이므로 이 초기화 단계에서는 object.__setattr__을 사용합니다.
        # 생성이 끝나면 외부에서는 일반 대입으로 값을 바꿀 수 없습니다.
        object.__setattr__(self, "u_type", grade)
        object.__setattr__(self, "price", decimal_price)
        object.__setattr__(self, "coupon", normalized_coupon)


class OrderCalculator:
    """검증된 Order 객체를 받아 할인과 쿠폰 정책에 따라 금액을 계산합니다.

    주문 정보를 직접 보관하지 않으므로 계산기 하나로 여러 주문을 처리합니다.
    단순히 함수를 클래스로 감싸는 데 그치지 않고 데이터 검증과 계산을 분리합니다.
    """

    # 클래스 속성: 모든 계산기 객체가 공통으로 사용하는 계산 정책입니다.
    DISCOUNT_RATES = {
        MemberGrade.GRADE_1: Decimal("0.05"),
        MemberGrade.GRADE_2: Decimal("0.10"),
        MemberGrade.GRADE_3: Decimal("0.20"),
    }
    COUPON_AMOUNT = Decimal("3000")

    def calculate(self, order: Order) -> int:
        """회원 할인 → 쿠폰 차감 → 최소 0원 → 최종 소수점 버림 순서입니다."""
        if not isinstance(order, Order):
            raise TypeError("계산 대상은 Order 객체여야 합니다.")

        # Order 생성 시 price는 Decimal로 정규화되어 있습니다.
        # 큰 금액도 중간 반올림 없이 계산하도록 기존 정밀도 확보 방식을 유지합니다.
        price_parts = order.price.as_tuple()
        required_precision = (
            len(price_parts.digits)
            + len(str(order.qty))
            + max(0, price_parts.exponent)
            + 4
        )
        # localcontext의 설정은 이 블록에만 적용되고 전역 Decimal 설정은 유지됩니다.
        with localcontext() as context:
            context.prec = max(28, required_precision)
            total = order.price * order.qty
            total *= Decimal("1") - self.DISCOUNT_RATES[order.u_type]
            if order.coupon == "YES":
                total -= self.COUPON_AMOUNT

            # 쿠폰이 주문 금액보다 커도 음수 결제 금액이 나오지 않게 합니다.
            # 반올림으로 정책을 바꾸지 않고 기존처럼 마지막에 소수점을 버립니다.
            total = max(total, Decimal("0"))
            return int(total.to_integral_value(rounding=ROUND_DOWN))


if __name__ == "__main__":
    # 이전: result = calc_order(1, 100, 20, "yes")
    # 이후: 주문 객체를 생성한 뒤 계산기 객체의 메서드에 전달합니다.
    order = Order(u_type=MemberGrade.GRADE_1, price=100, qty=20, coupon="yes")
    calculator = OrderCalculator()
    result = calculator.calculate(order)
    print(f"최종 결제 금액: {result:,}원")

    # 같은 계산기를 다른 주문에 재사용합니다. 정수 등급 입력도 호환됩니다.
    another_order = Order(u_type=2, price=10000, qty=1, coupon="NO")
    print(f"두 번째 주문 금액: {calculator.calculate(another_order):,}원")
