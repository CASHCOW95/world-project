import os
import shutil

def main():
    workspace = os.path.abspath('.')
    old_book_dir = os.path.join(workspace, 'coin', '코인진', '책')
    new_book_dir = os.path.join(workspace, 'coin', 'coinjin', '책')
    
    if os.path.exists(old_book_dir):
        print(f"Moving {old_book_dir} to {new_book_dir}...")
        shutil.copytree(old_book_dir, new_book_dir, dirs_exist_ok=True)
        shutil.rmtree(old_book_dir)
        print("Move completed successfully.")
        
    # Remove empty parent directory 'coin/코인진' if empty
    parent_dir = os.path.join(workspace, 'coin', '코인진')
    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
        os.rmdir(parent_dir)
        print("Removed empty parent directory coin/코인진")

if __name__ == '__main__':
    main()
