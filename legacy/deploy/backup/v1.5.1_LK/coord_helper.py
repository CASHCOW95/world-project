import pyautogui
import time
import keyboard

print("--- 마우스 좌표 및 영역 확인 도우미 ---")
print("1. 미니맵의 '왼쪽 상단' 끝에 마우스를 대고 'F1'을 누르세요.")
print("2. 미니맵의 '오른쪽 하단' 끝에 마우스를 대고 'F2'를 누르세요.")
print("3. 종료하려면 'ESC'를 누르세요.")

top_left = None
bottom_right = None

while True:
    if keyboard.is_pressed('f1'):
        top_left = pyautogui.position()
        print(f"[+] 왼쪽 상단 확정: {top_left}")
        time.sleep(0.5)
    
    if keyboard.is_pressed('f2'):
        bottom_right = pyautogui.position()
        print(f"[+] 오른쪽 하단 확정: {bottom_right}")
        time.sleep(0.5)
        
        if top_left:
            width = bottom_right.x - top_left.x
            height = bottom_right.y - top_left.y
            region = {"top": top_left.y, "left": top_left.x, "width": width, "height": height}
            print("\n" + "="*30)
            print("현재 미니맵 설정값 (MINIMAP_REGION):")
            print(region)
            print("="*30 + "\n")

    if keyboard.is_pressed('esc'):
        print("도우미를 종료합니다.")
        break
    
    time.sleep(0.1)
