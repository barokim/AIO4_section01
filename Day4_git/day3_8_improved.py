"""0~100점의 점수 데이터를 검증하고 0~1 범위로 정규화한다."""

import math
from collections.abc import Iterable, Mapping


def preprocess_scores(data: Iterable[Mapping[str, object]]) -> list[float]:
    """score를 가진 행들을 받아 소수점 넷째 자리로 반올림한 값을 반환한다.

    숫자 문자열도 허용하며, 빈 입력에는 빈 리스트를 반환한다.
    잘못된 입력은 TypeError 또는 ValueError로 알린다. 행 번호는 1부터 센다.
    오류가 발생하면 전체 처리를 중단하고 부분 결과는 반환하지 않는다.
    """
    # [수정] 문자열이나 딕셔너리 자체를 행 목록으로 잘못 전달하지 않도록 검사한다.
    # 리스트 외에 튜플과 제너레이터도 사용할 수 있다.
    if isinstance(data, (str, bytes, Mapping)) or not isinstance(data, Iterable):
        raise TypeError("data는 score 딕셔너리들을 담은 반복 가능한 객체여야 합니다.")

    normalized_scores = []
    for row_number, row in enumerate(data, start=1):
        # [수정] 오류에 행 번호를 포함해 원본 데이터에서 문제 위치를 찾기 쉽게 한다.
        if not isinstance(row, Mapping):
            raise TypeError(f"{row_number}번째 행: 딕셔너리 형태여야 합니다.")
        if "score" not in row:
            raise ValueError(f"{row_number}번째 행: score 키가 없습니다.")

        raw_score = row["score"]
        # [수정] bool은 float(True) == 1.0으로 변환되므로 별도로 거부한다.
        if isinstance(raw_score, bool):
            raise TypeError(f"{row_number}번째 행: score에 불리언은 사용할 수 없습니다.")

        # [수정] None, N/A 등 변환 불가능한 값에도 원인과 위치를 안내한다.
        try:
            score = float(raw_score)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                f"{row_number}번째 행: score는 숫자 또는 숫자 문자열이어야 합니다."
            ) from error

        # [수정] float 변환에 성공하는 NaN과 무한대도 유효한 점수가 아니다.
        if not math.isfinite(score):
            raise ValueError(f"{row_number}번째 행: score는 유한한 숫자여야 합니다.")

        # [수정] 음수와 100점 초과 값을 거부해 결과가 0~1 범위에 있도록 한다.
        if not 0 <= score <= 100:
            raise ValueError(f"{row_number}번째 행: score는 0~100 범위여야 합니다.")

        # 기존의 소수점 넷째 자리 반올림 규칙은 유지한다.
        normalized_scores.append(round(score / 100.0, 4))

    return normalized_scores


# [수정] 직접 실행할 때만 예제를 실행하므로 import 시 부작용이 없다.
if __name__ == "__main__":
    # [수정] 함수의 입력 규칙에 맞게 각 점수를 score 딕셔너리로 전달한다.
    sample_data = [{"score": 100}, {"score": "50"}, {"score": 25}]
    result = preprocess_scores(sample_data)
    print(result)
