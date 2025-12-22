"""
文件操作工具模块
提供文件移动、trash 等公共功能
"""
import os
import shutil
from send2trash import send2trash


def safe_move_to_trash(path, trash_dir=''):
    """
    安全地将文件移动到 trash 目录
    
    如果 trash_dir 为空，使用系统回收站
    如果目标文件已存在，自动添加 .copy 后缀
    
    Args:
        path: 要移动的文件路径
        trash_dir: trash 目录路径，为空则使用系统回收站
        
    Returns:
        实际移动到的目标路径
    """
    if trash_dir == '':
        send2trash(path)
        return None
    else:
        # 移动到 trash 目录，如果文件已存在则添加 .copy 后缀
        dest_path = os.path.join(trash_dir, os.path.basename(path))
        if os.path.exists(dest_path):
            # 文件已存在，添加 .copy 后缀
            copy_num = 1
            while True:
                new_dest_path = dest_path + '.copy' * copy_num
                if not os.path.exists(new_dest_path):
                    shutil.move(path, new_dest_path)
                    print(f"Warning: Destination already exists, moved to: {new_dest_path}")
                    return new_dest_path
                copy_num += 1
                if copy_num > 100:  # 防止无限循环
                    raise Exception(f"Failed to move file after 100 attempts: {path}")
        else:
            shutil.move(path, dest_path)
            return dest_path

