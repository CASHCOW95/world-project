# 회수 탭 UI 개선 및 시퀀스 전면 제어 전환

## 목표
1. 회수 탭 UI 가독성 대폭 개선 (관련 필드 그룹핑)
2. 회수/복귀 이동을 100% 시퀀스로 사용자가 설계
3. 자동 drop-jump (`perform_vertical_move`) 로직 제거

---

## 현재 문제점

### UI 문제
- 12개 입력 필드가 동일한 스타일로 나열 → 가독성 최악
- 관련 필드끼리 그룹핑 없음

### 로직 문제 (자동 이동)
현재 상태머신이 시퀀스를 무시하고 자체 판단으로 이동하는 부분:

1. **`moving_to_recovery_start`**: 회수 시작좌표 X,Y로 이동 시 `perform_vertical_move()` 자동 호출
2. **`moving_to_recovery_y`**: 회수층 시퀀스가 비어있으면 자동 drop-jump
3. **`moving_to_return_start`**: 복귀 전 시작좌표/텔포포인트로 이동 시 `perform_vertical_move()` 자동 호출

→ 이들을 모두 **시퀀스 기반**으로 전환

---

## Proposed Changes

### 1. UI 재설계 ([ui_v2.py](file:///c:/Users/ydh24/Desktop/밋업/python/core/game_auto/modules/ui_v2.py))

현재 → 변경:

```
[회수 모드 활성화 체크박스]

┌─ 회수 주기/시간 ──────────────────┐
│ 회수 주기 (초):          [60]     │
│ 회수 시간 (초):          [10]     │
└───────────────────────────────────┘

┌─ 좌표 설정 (F2 등록) ────────────┐
│ 사냥층 Y:    [67]  회수층 Y: [81] │
│ 회수시작 X:  [-1]  Y:       [-1]  │
│ 복귀텔포 X:  [-1]  Y:       [-1]  │
│ 복귀범위 X:  [45]  ~        [50]  │
└───────────────────────────────────┘

┌─ 시퀀스 설정 ─────────────────────┐
│ 회수층 이동:  [JUMP_DOWN, ...]    │
│ 복귀 시퀀스:  [TELE_UP, ...]      │
│ 액션 간 지연: [1.0]               │
└───────────────────────────────────┘

[회수 시 텔레포트 적용 체크]
```

- "복귀 시퀀스 지연", "회수 시퀀스 지연" → **"액션 간 지연"** 하나로 통합
- 좌표 필드들을 한 행에 2개씩 배치하여 공간 절약

### 2. 상태머신 단순화 ([AUTOmaple_v2.0.0_LK.py](file:///c:/Users/ydh24/Desktop/밋업/python/core/game_auto/AUTOmaple_v2.0.0_LK.py))

상태 전이 단순화:

```
사냥 중 → 회수 트리거
  ├─ [회수층 이동 시퀀스 실행] → 회수 수집 (핑퐁)
  └─ 수집 완료 → [복귀 시퀀스 실행] → 사냥층 Y 검증 → 사냥 재개
```

**제거 대상:**
- `moving_to_recovery_start` 상태 (시작좌표로 자동 이동) → 시퀀스로 흡수
- `moving_to_recovery_y` 내 자동 `perform_vertical_move()` → 시퀀스만 실행
- `moving_to_return_start` 내 자동 좌표 이동 → 시퀀스로 흡수

**최종 상태 3개:**
1. `executing_recovery_seq` - 회수층 이동 시퀀스 실행
2. `collecting` - 회수 수집 (기존 유지)
3. `executing_return_seq` - 복귀 시퀀스 실행 → 사냥층 Y 검증

### 3. 설정 저장/로드 ([settings_v2.py](file:///c:/Users/ydh24/Desktop/밋업/python/core/game_auto/modules/settings_v2.py))

- `return_delay` + `recovery_delay` → `seq_delay` 하나로 통합
- 기존 필드는 하위호환을 위해 로드 시 fallback

---

## Open Questions

> [!IMPORTANT]
> **시퀀스 지연 통합**: 복귀 시퀀스 지연과 회수 시퀀스 지연을 하나로 통합해도 괜찮은지? 아니면 각각 따로 유지?

> [!IMPORTANT]
> **복귀 시 사냥층 Y 검증**: 복귀 시퀀스 실행 후 사냥층 Y에 도달했는지 확인 → 실패 시 시퀀스를 재실행하는 기존 로직을 유지할지?

---

## Verification Plan

### Manual Verification
- 사냥 탭/회수 탭 UI 확인
- 프로필 저장/로드 후 값 유지 확인
- 시퀀스만으로 회수/복귀 이동이 완전히 제어되는지 실행 테스트
