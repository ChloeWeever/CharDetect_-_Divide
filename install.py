import os
import sys
import subprocess
import venv

# 项目根目录（假设脚本与 requirements.txt 在同一目录）
project_dir = os.path.dirname(os.path.abspath(__file__))
venv_dir = os.path.join(project_dir, ".venv")
req_file = os.path.join(project_dir, "requirements.txt")

def create_virtual_env():
    if not os.path.exists(venv_dir):
        print("[+] 创建虚拟环境...")
        venv.create(venv_dir, with_pip=True)
    else:
        print("[*] 虚拟环境已存在.")

def install_packages():
    print("[+] 安装依赖包...")
    pip_executable = os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "pip")
    try:
        subprocess.check_call([pip_executable, "install", "--upgrade", "pip"])
        subprocess.check_call([pip_executable, "install", "-r", req_file])
        print("[√] 所有依赖安装完成！")
    except subprocess.CalledProcessError as e:
        print(f"[!] 安装失败: {e}")
        sys.exit(1)

def main():
    create_virtual_env()
    install_packages()

if __name__ == "__main__":
    main()
