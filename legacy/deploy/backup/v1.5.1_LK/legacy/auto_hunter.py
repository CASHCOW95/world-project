import cv2
import numpy as np
import mss
import pyautogui
import time
import random
import keyboard
import threading

# --- 설정 및 상수 ---
# 미니맵 캡처 영역 (x, y, width, height) - 사용자 환경에 맞게 수정 필요
MINIMAP_REGION = {"top": 100, "left": 100, "width": 200, "height": 150}

# 맵 활동 범위 (미니맵 기준 X 좌표)
X_MIN = 20
X_MAX = 180

# 키 설정
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_ATTACK = 'ctrl'
KEY_DASH = 'shift'
KEY_JUMP = 'space'

# 상태 및 전역 변수
is_running = False
current_direction = KEY_RIGHT
last_x_pos = -1
stuck_counter = 0

def human_delay(min_sec=0.05, max_sec=0.15):
    """인간다운 무작위성을 위한 미세 딜레이"""
    time.sleep(random.uniform(min_sec, max_sec))

def press_key(key, duration=0.1):
    """키 누름 (랜덤 딜레이 포함)"""
    pyautogui.keyDown(key)
    time.sleep(duration + random.uniform(-0.02, 0.02))
    pyautogui.keyUp(key)

def skill_combo():
    """스킬 콤보: 대시 + 공격"""
    # 이동 중 공격 시 잠시 방향키를 떼는 로직 (필요 시)
    # pyautogui.keyUp(current_direction) 
    
    # 대시/이동 스킬
    press_key(KEY_DASH, duration=0.05)
    human_delay(0.05, 0.1)
    
    # 공격 스킬
    press_key(KEY_ATTACK, duration=0.1)
    human_delay(0.1, 0.2)
    
    # 다시 방향키 유지 (메인 루프에서 처리)

def get_player_x_from_minimap(sct):
    """미니맵에서 캐릭터의 X 좌표를 추출 (템플릿 매칭 또는 색상 필터링)"""
    screenshot = sct.grab(MINIMAP_REGION)
    img = np.array(screenshot)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    
    # 실제 환경에서는 'minimap_player_dot.png' 템플릿 이미지를 사용하거나,
    # 캐릭터 점의 고유 색상(예: 노란색)을 필터링하여 좌표를 찾습니다.
    # 여기서는 예시로 가장 밝은 지점(캐릭터 점 가정)의 X 좌표를 반환하는 로직을 작성합니다.
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(img_gray)
    
    return maxLoc[0] # 캐릭터의 X 좌표

def main_loop():
    global is_running, current_direction, last_x_pos, stuck_counter
    
    print("자동사냥 매크로를 시작합니다. (F12: 종료)")
    is_running = True
    
    with mss.mss() as sct:
        while is_running:
            # 1. 위치 파악
            current_x = get_player_x_from_minimap(sct)
            
            # 2. 끼임 방지 (Stuck Check)
            if current_x == last_x_pos:
                stuck_counter += 1
            else:
                stuck_counter = 0
                last_x_pos = current_x
            
            if stuck_counter > 20: # 약 2~3초간 변화 없음
                print("[!] 끼임 감지 - 탈출 시퀀스 가동")
                pyautogui.keyUp(current_direction)
                press_key(KEY_JUMP, 0.1)
                reverse_dir = KEY_LEFT if current_direction == KEY_RIGHT else KEY_RIGHT
                press_key(reverse_dir, 0.5)
                stuck_counter = 0
                continue

            # 3. 방향 전환 루프
            if current_x >= X_MAX:
                print(">>> 우측 끝 도달 -> 좌회전")
                pyautogui.keyUp(KEY_RIGHT)
                current_direction = KEY_LEFT
            elif current_x <= X_MIN:
                print("<<< 좌측 끝 도달 -> 우회전")
                pyautogui.keyUp(KEY_LEFT)
                current_direction = KEY_RIGHT
            
            # 4. 이동 및 전투 연계
            pyautogui.keyDown(current_direction)
            
            # 콤보 실행 (랜덤 주기)
            if random.random() < 0.3: # 30% 확률로 스킬 사용
                skill_combo()
            
            human_delay(0.1, 0.3)

def stop_macro():
    global is_running
    print("\n매크로를 종료합니다.")
    is_running = False
    # 모든 키 떼기
    pyautogui.keyUp(KEY_LEFT)
    pyautogui.keyUp(KEY_RIGHT)

# 종료 단축키 설정
keyboard.add_hotkey('f12', stop_macro)

if __name__ == "__main__":
    # 준비 시간
    print("3초 후 시작합니다. 게임 화면을 활성화하세요.")
    time.sleep(3)
    
    try:
        main_loop()
    except KeyboardInterrupt:
        stop_macro()
