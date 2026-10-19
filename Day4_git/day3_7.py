#  [Codex] 기반 코드 개선 & 리팩토링 실전 1
# 리팩토링 - 전문가들에게 코드의 문제점을 지적받고 새로 구축하는것==> 지금은 AI가 대신해서 해준다

def calc_order_legacy(u_type, price, qty, coupon):
    # 문제점 1: u_type 1, 2, 3이 무슨 등급인지 작성자 외에는 알 수 없음 (매직 넘버)
    # 문제점 2: price나 qty에 음수가 들어와도 아무런 검증 없이 잘못된 금액을 계산함
    total = price * qty
    if u_type == 1:
       total = total * 0.95
    elif u_type == 2:
       total = total * 0.90
    elif u_type == 3:
      total = total * 0.80
    if coupon == "YES":
      total = total - 3000
    if total < 0:
      total = 0
    return int(total)

result = calc_order_legacy(1,100,20,"yes")
print(result)

