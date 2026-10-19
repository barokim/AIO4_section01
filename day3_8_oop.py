"""점수 전처리를 객체지향 구조로 리팩토링한 예제. Python 3.9 이상.

기존: preprocess_scores(data) 함수 안에서 입력 검사, 점수 검사, 정규화를 수행.
변경: ScorePreprocessor 객체가 반올림 설정을 보관하고 메서드별로 일을 나눈다.
기본 설정의 계산 결과와 예외 종류 및 메시지는 day3_8_improved.py와 같다.
"""

import math
from collections.abc import Iterable, Mapping


class ScorePreprocessor:
    """
    0~100점 데이터를 검증하고 0~1 범위의 값으로 정규화한다.
    객체는 반올림 자릿수만 보관하고 입력 데이터와 처리 결과는 보관하지 않는다.
    따라서 같은 객체로 여러 데이터 묶음을 처리해도 이전 결과가 누적되지 않는다.
    기본값은 기존 함수와 같은 소수점 넷째 자리 반올림이다.
    """

    def __init__(self, decimal_places: int = 4) -> None:
        """객체 생성 시 사용할 반올림 자릿수를 검증하고 저장한다."""
        # [변경] 함수에 고정되어 있던 4를 객체별 설정으로 옮겼다.
        # bool도 int에 해당하므로 True를 자릿수로 받지 않도록 먼저 검사한다.
        if isinstance(decimal_places, bool) or not isinstance(decimal_places, int):
            raise TypeError("반올림 자릿수는 정수여야 합니다.")
        if decimal_places < 0:
            raise ValueError("반올림 자릿수는 0 이상이어야 합니다.")

        # self는 현재 객체를 뜻한다. 밑줄은 내부용 속성이라는 관례이며,
        # 파이썬이 외부 접근을 강제로 막는 접근 제한자는 아니다.
        self._decimal_places = decimal_places

    def preprocess(self, data: Iterable[Mapping[str, object]]) -> list[float]:
        """입력 검사 → 각 행의 점수 검사 → 정규화 순서로 처리한다.

        숫자 문자열, 리스트, 튜플, 제너레이터를 지원하며 빈 입력은 []를 반환한다.
        잘못된 행은 1부터 시작하는 행 번호와 함께 예외로 알린다.
        첫 오류에서 처리를 중단하고 부분 결과는 반환하지 않는다.
        제너레이터는 처리 중 소비되므로 다시 쓰려면 새로 생성해야 한다.
        """
        # [변경] 기존 함수의 전체 작업 순서를 담당하는 공개 메서드다.
        # 호출자는 내부 메서드 대신 이 메서드 하나를 사용하면 된다.
        self._validate_data(data)

        # 결과를 지역 변수로 두어 같은 객체를 재사용해도 값이 누적되지 않는다.
        normalized_scores = []
        for row_number, row in enumerate(data, start=1):
            score = self._parse_score(row, row_number)
            normalized_scores.append(self._normalize(score))
        return normalized_scores

    @staticmethod
    def _validate_data(data: object) -> None:
        """행 목록으로 사용할 수 있는 입력인지 검사한다."""
        # [변경] 객체 설정을 사용하지 않는 검사이므로 staticmethod로 분리했다.
        # 정적 메서드는 self를 받지 않는다. 메서드명 앞 밑줄은 내부용 표시다.
        if isinstance(data, (str, bytes, Mapping)) or not isinstance(data, Iterable):
            raise TypeError("data는 score 딕셔너리들을 담은 반복 가능한 객체여야 합니다.")

    @staticmethod
    def _parse_score(row: object, row_number: int) -> float:
        """한 행에서 점수를 꺼내 숫자로 변환하고 유효한 점수인지 검사한다."""
        # [변경] 여러 곳에 흩어질 수 있는 행 검증을 한 메서드에 모았다.
        # Mapping을 사용하므로 일반 dict와 호환되는 매핑 객체도 허용한다.
        if not isinstance(row, Mapping):
            raise TypeError(f"{row_number}번째 행: 딕셔너리 형태여야 합니다.")
        if "score" not in row:
            raise ValueError(f"{row_number}번째 행: score 키가 없습니다.")

        raw_score = row["score"]
        # 기존 방어 로직 유지: True/False가 1점/0점으로 바뀌는 것을 막는다.
        if isinstance(raw_score, bool):
            raise TypeError(f"{row_number}번째 행: score에 불리언은 사용할 수 없습니다.")

        try:
            score = float(raw_score)
        except (TypeError, ValueError, OverflowError) as error:
            # 원래 예외를 연결해 상세 오류 원인도 추적할 수 있도록 한다.
            raise ValueError(
                f"{row_number}번째 행: score는 숫자 또는 숫자 문자열이어야 합니다."
            ) from error

        # NaN과 무한대는 float 변환에 성공하므로 별도로 검사해야 한다.
        if not math.isfinite(score):
            raise ValueError(f"{row_number}번째 행: score는 유한한 숫자여야 합니다.")
        if not 0 <= score <= 100:
            raise ValueError(f"{row_number}번째 행: score는 0~100 범위여야 합니다.")
        return score

    def _normalize(self, score: float) -> float:
        """검증이 끝난 점수를 100으로 나누고 설정된 자릿수로 반올림한다."""
        # [변경] 객체의 설정을 사용하므로 self를 받는 인스턴스 메서드다.
        # 유효성 검사는 _parse_score에서 끝냈으므로 여기서는 계산만 담당한다.
        return round(score / 100.0, self._decimal_places)


if __name__ == "__main__":
    sample_data = [{"score": 80}, {"score": "50"}, {"score": 30}]
    sample_data_2 = [{"score": 120}, {"score": "50"}, {"score": 30}]

    # 이전: result = preprocess_scores(sample_data)
    # 이후: 설정을 가진 객체를 만들고 그 객체의 메서드를 호출한다.
    preprocessor = ScorePreprocessor()
    result = preprocessor.preprocess(sample_data)
    result_2 = preprocessor.preprocess(sample_data_2)
    print(result)
    print(result_2)

    # 같은 객체 재사용: 앞서 처리한 값은 이번 결과에 누적되지 않는다.
    print(preprocessor.preprocess([{"score": 0}, {"score": 100}]))

    # 객체마다 다른 설정 사용: 기본 객체와 독립적으로 두 자리 반올림을 적용한다.
    two_decimal_preprocessor = ScorePreprocessor(decimal_places=2)
    print(two_decimal_preprocessor.preprocess([{"score": 83.333333}]))
