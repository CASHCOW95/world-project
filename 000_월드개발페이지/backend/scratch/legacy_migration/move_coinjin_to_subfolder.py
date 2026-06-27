import os
import shutil

def safe_rename(old_path, new_path):
    if not os.path.exists(old_path):
        return
    print(f"Moving {old_path} to {new_path}...")
    try:
        shutil.copytree(old_path, new_path, dirs_exist_ok=True)
        shutil.rmtree(old_path)
        print(f"Successfully moved {old_path}")
    except Exception as e:
        print(f"Error clean up {old_path}: {e}")

def main():
    workspace = os.path.abspath('.')
    coin_dir = os.path.join(workspace, 'coin')
    coinjin_dir = os.path.join(coin_dir, 'coinjin')
    
    os.makedirs(coinjin_dir, exist_ok=True)
    
    # Move coin/레거시(코인진) to coin/coinjin/레거시(코인진)
    old_legacy = os.path.join(coin_dir, '레거시(코인진)')
    new_legacy = os.path.join(coinjin_dir, '레거시(코인진)')
    safe_rename(old_legacy, new_legacy)
    
    # Move coin/책 to coin/coinjin/책
    old_book = os.path.join(coin_dir, '책')
    new_book = os.path.join(coinjin_dir, '책')
    safe_rename(old_book, new_book)

if __name__ == '__main__':
    main()
