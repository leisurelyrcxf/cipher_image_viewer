#!/bin/bash

# 编译脚本 - 使用 PyInstaller 将 Python 脚本打包成可执行文件
# 用法: ./build.sh

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================"
echo "开始编译 cipher_image_viewer"
echo "================================"
echo ""

# 检查 pyinstaller 是否安装
if ! command -v pyinstaller &> /dev/null; then
    echo "错误: pyinstaller 未安装"
    echo "请运行: pip3 install pyinstaller"
    exit 1
fi

echo "pyinstaller 版本:"
pyinstaller --version
echo ""

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build/ dist/ *.spec
echo "清理完成"
echo ""

# 编译 encrypt.py
echo "================================"
echo "正在编译 encrypt.py..."
echo "================================"
pyinstaller --onefile --name encrypt encrypt.py
echo ""

# 编译 decrypt.py
echo "================================"
echo "正在编译 decrypt.py..."
echo "================================"
pyinstaller --onefile --name decrypt decrypt.py
echo ""

# 显示结果
echo "================================"
echo "编译完成！"
echo "================================"
echo ""
echo "生成的可执行文件:"
ls -lh dist/
echo ""
echo "测试 encrypt:"
./dist/encrypt --help
echo ""
echo "测试 decrypt:"
./dist/decrypt --help
echo ""
echo "================================"
echo "可执行文件位置: $SCRIPT_DIR/dist/"
echo "================================"

