import os
import time
import random
import ctypes
import pyautogui
import numpy as np

# --- Windows SendInput API & Logitech G HUB Driver Emulation ---
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION)
    ]

KEY_SCAN_CODES = {
    'left': 0x4B, 'right': 0x4D, 'space': 0x39, 'ctrl': 0x1D, 'alt': 0x38, 'shift': 0x2A,
    'insert': 0x52, 'del': 0x53, 'home': 0x47, 'end': 0x4F, 'pgup': 0x49, 'pgdn': 0x51,
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21, 'g': 0x22,
    'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31,
    'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14, 'u': 0x16,
    'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15, 'z': 0x2C, 'up': 0x48, 'down': 0x50,
    'enter': 0x1C
}

class LogitechInput:
    def __init__(self, base_dir):
        self.dll = None
        paths = [
            "lghub_device.dll",
            os.path.join(base_dir, "lghub_device.dll"),
            r"C:\Program Files\LGHUB\lghub_device.dll",
            r"C:\Program Files\Logitech Gaming Software\SDK\Keyboard\LogitechLed.dll"
        ]
        for p in paths:
            if os.path.exists(p) or p == "lghub_device.dll":
                try:
                    self.dll = ctypes.CDLL(p)
                    self.dll.device_open()
                    break
                except:
                    pass

    def move(self, dx, dy):
        if self.dll:
            try:
                self.dll.moveR(int(dx), int(dy))
            except:
                pass

    def mouse_down(self, btn=1):
        if self.dll:
            try:
                self.dll.mouse_down(btn)
            except:
                pass

    def mouse_up(self, btn=1):
        if self.dll:
            try:
                self.dll.mouse_up(btn)
            except:
                pass

    def key_down(self, key_name):
        if self.dll and key_name in KEY_SCAN_CODES:
            try:
                self.dll.key_down(KEY_SCAN_CODES[key_name])
            except:
                pass

    def key_up(self, key_name):
        if self.dll and key_name in KEY_SCAN_CODES:
            try:
                self.dll.key_up(KEY_SCAN_CODES[key_name])
            except:
                pass


class MovementController:
    def __init__(self, main_win):
        self.main_win = main_win
        self.logitech_input = LogitechInput(main_win.base_dir)
        
    def set_key_state(self, key, state):
        current_state = self.main_win.key_states.get(key, False)
        if current_state == state:
            return
        self.main_win.key_states[key] = state
        
        if key in ['left', 'right']:
            dir_str = "LEFT" if key == 'left' else "RIGHT"
            state_str = "DOWN" if state else "UP"
            self.main_win.logger.log(f"{dir_str} KEY {state_str}", "MOVEMENT")
        
        mode = self.main_win.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1  # Fallback to SendInput
            
        if mode == 0:
            if state:
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)
        elif mode == 1:
            scan_code = KEY_SCAN_CODES.get(key)
            if scan_code is not None:
                extra = ctypes.c_ulong(0)
                ii_ = INPUT_UNION()
                flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if not state else 0)
                ii_.ki = KEYBDINPUT(0, scan_code, flags, 0, ctypes.pointer(extra))
                x = INPUT(1, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            if state:
                self.logitech_input.key_down(key)
            else:
                self.logitech_input.key_up(key)

    def press_key(self, k):
        self.set_key_state(k, True)
        time.sleep(random.uniform(0.05, 0.1))
        self.set_key_state(k, False)
        self.main_win.actions_cnt += 1

    def drag_mouse_down(self):
        mode = self.main_win.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1
            
        if mode == 0:
            pyautogui.mouseDown()
        elif mode == 1:
            extra = ctypes.c_ulong(0)
            ii_ = INPUT_UNION()
            ii_.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            x = INPUT(0, ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            self.logitech_input.mouse_down(1)

    def drag_mouse_up(self):
        mode = self.main_win.input_mode
        if mode == 2 and not self.logitech_input.dll:
            mode = 1
            
        if mode == 0:
            pyautogui.mouseUp()
        elif mode == 1:
            extra = ctypes.c_ulong(0)
            ii_ = INPUT_UNION()
            ii_.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            x = INPUT(0, ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        elif mode == 2:
            self.logitech_input.mouse_up(1)

    def human_mouse_move(self, tx, ty):
        try:
            pyautogui.PAUSE = 0
            for _ in range(15):
                cx, cy = pyautogui.position()
                dist = np.hypot(tx-cx, ty-cy)
                if dist < 2: 
                    # 최종 위치로 보정 및 마크
                    mode = self.main_win.input_mode
                    if mode == 2 and not self.logitech_input.dll:
                        mode = 1
                    if mode == 0:
                        pyautogui.moveTo(tx, ty)
                    elif mode == 1:
                        ctypes.windll.user32.SetCursorPos(int(tx), int(ty))
                    elif mode == 2:
                        self.logitech_input.move(tx - cx, ty - cy)
                    break
                
                lerp = random.uniform(0.15, 0.45) if dist > 50 else random.uniform(0.5, 0.8)
                ox, oy = (random.uniform(-2, 2), random.uniform(-2, 2)) if dist < 20 else (0, 0)
                target_x = cx + (tx-cx)*lerp + ox
                target_y = cy + (ty-cy)*lerp + oy
                
                mode = self.main_win.input_mode
                if mode == 2 and not self.logitech_input.dll:
                    mode = 1
                    
                if mode == 0:
                    pyautogui.moveTo(target_x, target_y)
                elif mode == 1:
                    ctypes.windll.user32.SetCursorPos(int(target_x), int(target_y))
                elif mode == 2:
                    dx = int(target_x) - cx
                    dy = int(target_y) - cy
                    self.logitech_input.move(dx, dy)
                time.sleep(random.uniform(0.01, 0.02))
        except: 
            pass

    def perform_horizontal_move(self, dx, move_mode):
        teleport_key = self.main_win.key_teleport_cb.currentText()
        dir_key = 'left' if dx > 0 else 'right'
        
        self.set_key_state('left' if dir_key == 'right' else 'right', False)
        
        if move_mode == "TELEPORT":
            self.main_win.is_teleporting = True
            dir_str = "RIGHT" if dir_key == "right" else "LEFT"
            self.main_win.logger.log(f"TELEPORT {dir_str}", "MOVEMENT")
            self.set_key_state(dir_key, True)
            time.sleep(0.04)
            self.press_key(teleport_key)
            time.sleep(0.02)
            self.set_key_state(dir_key, False)
            time.sleep(0.15)
            self.main_win.is_teleporting = False
        elif move_mode == "JUMP":
            self.main_win.is_moving = True
            self.set_key_state(dir_key, True)
            time.sleep(0.04)
            jump_key = self.main_win.key_jump_cb.currentText()
            self.press_key(jump_key)
            time.sleep(0.15)
            self.set_key_state(dir_key, False)
            self.main_win.is_moving = False
        else: # WALK or DROP
            self.main_win.is_moving = True
            self.set_key_state(dir_key, True)
            time.sleep(0.08)
            if abs(dx) < 8:
                time.sleep(0.03)
                self.set_key_state(dir_key, False)
            self.main_win.is_moving = False

    def perform_vertical_move(self, dy, move_mode):
        teleport_key = self.main_win.key_teleport_cb.currentText()
        
        if dy > 0: # 수직 상승
            if move_mode == "TELEPORT":
                self.main_win.is_teleporting = True
                self.main_win.logger.log(f"수직 상승 기동 (TELEPORT, Y차이: {dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                self.set_key_state('up', True)
                time.sleep(0.04)
                self.press_key(teleport_key)
                time.sleep(0.02)
                self.set_key_state('up', False)
                time.sleep(0.2)
                self.main_win.is_teleporting = False
                time.sleep(0.05)
            elif move_mode == "JUMP":
                self.main_win.is_moving = True
                self.main_win.logger.log(f"수직 상승 기동 (JUMP, Y차이: {dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                jump_key = self.main_win.key_jump_cb.currentText()
                self.press_key(jump_key)
                time.sleep(0.2)
                self.main_win.is_moving = False
                time.sleep(0.05)
            else: # WALK or DROP
                self.main_win.logger.log(f"수직 상승 기동 (WALK/DROP up입력, Y차이: {dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                self.set_key_state('up', True)
                time.sleep(0.15)
                self.set_key_state('up', False)
                time.sleep(0.05)
        elif dy < 0: # 하단 낙하
            if move_mode == "DROP":
                self.main_win.is_moving = True
                self.main_win.logger.log(f"하단 낙하 기동 (DROP, Y차이: {-dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                jump_key = self.main_win.key_jump_cb.currentText()
                self.set_key_state('down', True)
                time.sleep(0.08)
                self.press_key(jump_key)
                time.sleep(0.02)
                self.set_key_state('down', False)
                time.sleep(0.25)
                self.main_win.is_moving = False
                time.sleep(0.05)
            elif move_mode == "WALK":
                self.main_win.is_moving = True
                self.main_win.logger.log(f"하단 낙하 기동 (WALK, Y차이: {-dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                self.set_key_state('down', True)
                time.sleep(0.15)
                self.set_key_state('down', False)
                time.sleep(0.1)
                self.main_win.is_moving = False
                time.sleep(0.05)
            else: # TELEPORT or JUMP (하향 낙하 시 DROP으로 폴백)
                self.main_win.is_moving = True
                self.main_win.logger.log(f"하단 낙하 폴백 기동 (DROP, Y차이: {-dy}px, 실패 카운트: {self.main_win.fall_count}/4)", "MOVEMENT")
                jump_key = self.main_win.key_jump_cb.currentText()
                self.set_key_state('down', True)
                time.sleep(0.08)
                self.press_key(jump_key)
                time.sleep(0.02)
                self.set_key_state('down', False)
                time.sleep(0.25)
                self.main_win.is_moving = False
                time.sleep(0.05)

    def execute_move_action(self, move_mode):
        teleport_key = self.main_win.key_teleport_cb.currentText()
        jump_key = self.main_win.key_jump_cb.currentText()
        
        if move_mode == "TELE_LEFT":
            self.main_win.is_teleporting = True
            self.set_key_state('right', False)
            self.set_key_state('left', True)
            time.sleep(0.04)
            self.press_key(teleport_key)
            time.sleep(0.02)
            self.set_key_state('left', False)
            time.sleep(0.15)
            self.main_win.is_teleporting = False
        elif move_mode == "TELE_RIGHT":
            self.main_win.is_teleporting = True
            self.set_key_state('left', False)
            self.set_key_state('right', True)
            time.sleep(0.04)
            self.press_key(teleport_key)
            time.sleep(0.02)
            self.set_key_state('right', False)
            time.sleep(0.15)
            self.main_win.is_teleporting = False
        elif move_mode == "TELE_UP":
            self.main_win.is_teleporting = True
            self.set_key_state('up', True)
            time.sleep(0.04)
            self.press_key(teleport_key)
            time.sleep(0.02)
            self.set_key_state('up', False)
            time.sleep(0.2)
            self.main_win.is_teleporting = False
        elif move_mode == "JUMP_LEFT":
            self.main_win.is_moving = True
            self.set_key_state('right', False)
            self.set_key_state('left', True)
            time.sleep(0.04)
            self.press_key(jump_key)
            time.sleep(0.15)
            self.set_key_state('left', False)
            self.main_win.is_moving = False
        elif move_mode == "JUMP_RIGHT":
            self.main_win.is_moving = True
            self.set_key_state('left', False)
            self.set_key_state('right', True)
            time.sleep(0.04)
            self.press_key(jump_key)
            time.sleep(0.15)
            self.set_key_state('right', False)
            self.main_win.is_moving = False
        elif move_mode == "JUMP_UP":
            self.main_win.is_moving = True
            self.press_key(jump_key)
            time.sleep(0.2)
            self.main_win.is_moving = False
        elif move_mode == "WALK_LEFT":
            self.main_win.is_moving = True
            self.set_key_state('right', False)
            self.set_key_state('left', True)
            time.sleep(0.15)
            self.set_key_state('left', False)
            self.main_win.is_moving = False
        elif move_mode == "WALK_RIGHT":
            self.main_win.is_moving = True
            self.set_key_state('left', False)
            self.set_key_state('right', True)
            time.sleep(0.15)
            self.set_key_state('right', False)
            self.main_win.is_moving = False
        elif move_mode == "DROP":
            self.main_win.is_moving = True
            self.set_key_state('down', True)
            time.sleep(0.08)
            self.press_key(jump_key)
            time.sleep(0.02)
            self.set_key_state('down', False)
            time.sleep(0.25)
            self.main_win.is_moving = False
        elif move_mode == "JUMP":
            self.main_win.is_moving = True
            self.press_key(jump_key)
            time.sleep(0.2)
            self.main_win.is_moving = False
        elif move_mode == "ROPE_UP":
            self.set_key_state('up', True)
            time.sleep(getattr(self.main_win, 'rope_climb_time', 1.5))
            self.set_key_state('up', False)
        elif move_mode == "TELEPORT":
            self.main_win.is_teleporting = True
            self.press_key(teleport_key)
            time.sleep(0.15)
            self.main_win.is_teleporting = False
        else:
            # Fallback (구버전 데이터 대응용)
            self.main_win.logger.log(f"[Movement] 미정의 이동 모드({move_mode}) -> 기본 텔레포트 시도", "MOVEMENT")
            self.perform_horizontal_move(1, "TELEPORT")

