# DEV_RULES

## 크로스 플랫폼 필수

개발 환경:
- Windows

실행 환경:
- Mac Mini M4

## Python 원칙

권장:
- sys.executable

금지:
- python
- python3 직접 호출

## 경로 원칙

사용:
- pathlib.Path
- 상대 경로
- Base Directory 고정

금지:
- 절대 경로
- OS 종속 경로

예시:

BASE_DIR = Path(__file__).resolve().parent

## 프로세스 실행

사용:
- subprocess

금지:
- os.system

## 안정성 원칙

필수:
- 예외 처리
- 로그 기록
- 재시도 로직
- 상태 플래그
- 설정 저장/복원
- 장애 복구
- 장시간 무인 운영 안정성
- 입력 충돌 방지
