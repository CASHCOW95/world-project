import os
import shutil

def safe_rename(old_path, new_path):
    if not os.path.exists(old_path):
        return
    print(f"Moving {old_path} to {new_path}...")
    try:
        shutil.copytree(old_path, new_path, dirs_exist_ok=True)
        # Try removing old path
        shutil.rmtree(old_path)
        print(f"Successfully moved and cleaned up {old_path}")
    except Exception as e:
        print(f"Warning/Error during cleanup of {old_path}: {e}")
        print("Note: The copy was successful, but some locked files could not be deleted immediately.")

def rename_legacy():
    workspace = os.path.abspath('.')
    
    coin_dir = os.path.join(workspace, 'coin')
    sung_dir = os.path.join(coin_dir, 'sung')
    
    # 1. coin/레거시 -> coin/레거시(코인진)
    old_coin_legacy = os.path.join(coin_dir, '레거시')
    new_coin_legacy = os.path.join(coin_dir, '레거시(코인진)')
    safe_rename(old_coin_legacy, new_coin_legacy)
            
    # 2. coin/sung/레거시 -> coin/sung/레거시(성정길)
    old_sung_legacy = os.path.join(sung_dir, '레거시')
    new_sung_legacy = os.path.join(sung_dir, '레거시(성정길)')
    safe_rename(old_sung_legacy, new_sung_legacy)

if __name__ == '__main__':
    rename_legacy()
