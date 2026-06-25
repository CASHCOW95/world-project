import os
import shutil

def reorganize():
    workspace = os.path.abspath('.')
    
    coin_dir = os.path.join(workspace, 'coin')
    sung_dir = os.path.join(workspace, 'sung')
    
    # 1. Rename coin/코인진 to coin/책
    old_coinjin = os.path.join(coin_dir, '코인진')
    new_coin_book = os.path.join(coin_dir, '책')
    
    if os.path.exists(old_coinjin):
        if os.path.exists(new_coin_book):
            # merge contents
            for item in os.listdir(old_coinjin):
                s = os.path.join(old_coinjin, item)
                d = os.path.join(new_coin_book, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(old_coinjin)
            print("Merged coin/코인진 into coin/책")
        else:
            os.rename(old_coinjin, new_coin_book)
            print("Renamed coin/코인진 to coin/책")
            
    # 2. Move sung to coin/sung
    target_sung = os.path.join(coin_dir, 'sung')
    if os.path.exists(sung_dir):
        if os.path.exists(target_sung):
            # If target already exists, merge
            for item in os.listdir(sung_dir):
                s = os.path.join(sung_dir, item)
                d = os.path.join(target_sung, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(sung_dir)
            print("Merged sung into coin/sung")
        else:
            shutil.move(sung_dir, target_sung)
            print("Moved sung to coin/sung")
            
    # 3. Rename coin/sung/성정길 to coin/sung/책
    old_sung_gil = os.path.join(target_sung, '성정길')
    new_sung_book = os.path.join(target_sung, '책')
    if os.path.exists(old_sung_gil):
        if os.path.exists(new_sung_book):
            for item in os.listdir(old_sung_gil):
                s = os.path.join(old_sung_gil, item)
                d = os.path.join(new_sung_book, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)
            shutil.rmtree(old_sung_gil)
            print("Merged coin/sung/성정길 into coin/sung/책")
        else:
            os.rename(old_sung_gil, new_sung_book)
            print("Renamed coin/sung/성정길 to coin/sung/책")
            
    # 4. Remove coin/sung/코인진 if exists (it was a double copy)
    old_sung_coinjin = os.path.join(target_sung, '코인진')
    if os.path.exists(old_sung_coinjin):
        shutil.rmtree(old_sung_coinjin)
        print("Removed redundant coin/sung/코인진 directory")

if __name__ == '__main__':
    reorganize()
