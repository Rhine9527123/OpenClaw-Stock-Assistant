#!/usr/bin/env python3
"""
股票晨报系统自检修复脚本
使用：python system_check.py --fix --report
"""

import os
import sys
import subprocess
import requests
from datetime import datetime, timedelta

class SystemChecker:
    """系统自检器"""
    
    def __init__(self):
        self.checks = []
        self.fixes = []
        self.errors = []
        
        # 从环境变量读取配置
        self.feishu_config = {
            "app_id": os.environ.get("FEISHU_APP_ID", ""),
            "app_secret": os.environ.get("FEISHU_APP_SECRET", ""),
            "chat_id": os.environ.get("FEISHU_CHAT_ID", "")
        }
    
    def check_feishu_token(self):
        """检查飞书 Token"""
        print("[检查] 飞书 Token...")
        
        token_file = ".feishu_token"
        if os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    token = f.read().strip()
                    token = token.replace('?', '')
                    if len(token) > 10:
                        self.checks.append(("飞书 Token", True, "有效"))
                        return True
            except Exception as e:
                self.errors.append(f"Token 读取失败: {e}")
        
        self.checks.append(("飞书 Token", False, "不存在或无效"))
        return False
    
    def fix_feishu_token(self):
        """修复飞书 Token"""
        print("[修复] 重新获取飞书 Token...")
        
        if not all(self.feishu_config.values()):
            print("[ERROR] 飞书配置不完整，无法获取 Token")
            return False
        
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            response = requests.post(url, json={
                "app_id": self.feishu_config["app_id"],
                "app_secret": self.feishu_config["app_secret"]
            }, timeout=10)
            
            if response.status_code == 200:
                token = response.json().get("tenant_access_token")
                with open(".feishu_token", "w", encoding="utf-8") as f:
                    f.write(token)
                self.fixes.append("重新获取飞书 Token")
                return True
            else:
                self.errors.append(f"Token 获取失败: {response.text}")
                return False
        except Exception as e:
            self.errors.append(f"Token 获取异常: {e}")
            return False
    
    def check_python_deps(self):
        """检查 Python 依赖"""
        print("[检查] Python 依赖...")
        
        required = ["pandas", "matplotlib", "requests"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        if missing:
            self.checks.append(("Python 依赖", False, f"缺失: {', '.join(missing)}"))
            return missing
        else:
            self.checks.append(("Python 依赖", True, "全部已安装"))
            return []
    
    def fix_python_deps(self, missing):
        """修复 Python 依赖"""
        print(f"[修复] 安装缺失依赖: {', '.join(missing)}...")
        
        for pkg in missing:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], 
                             check=True, timeout=60)
                self.fixes.append(f"安装依赖: {pkg}")
            except Exception as e:
                self.errors.append(f"安装 {pkg} 失败: {e}")
    
    def check_directories(self):
        """检查目录结构"""
        print("[检查] 目录结构...")
        
        required_dirs = ["charts", "reports", "logs", "skills"]
        missing = []
        
        for d in required_dirs:
            if not os.path.exists(d):
                missing.append(d)
        
        if missing:
            self.checks.append(("目录结构", False, f"缺失: {', '.join(missing)}"))
            return missing
        else:
            self.checks.append(("目录结构", True, "完整"))
            return []
    
    def fix_directories(self, missing):
        """修复目录结构"""
        print(f"[修复] 创建缺失目录: {', '.join(missing)}...")
        
        for d in missing:
            os.makedirs(d, exist_ok=True)
            self.fixes.append(f"创建目录: {d}")
    
    def check_chart_generation(self):
        """检查图表生成能力"""
        print("[检查] 图表生成能力...")
        
        try:
            # 尝试导入 matplotlib
            import matplotlib
            matplotlib.use('Agg')  # 无头模式
            import matplotlib.pyplot as plt
            
            # 简单测试
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            plt.close(fig)
            
            self.checks.append(("图表生成", True, "正常"))
            return True
        except Exception as e:
            self.checks.append(("图表生成", False, str(e)))
            return False
    
    def check_network(self):
        """检查网络连通性"""
        print("[检查] 网络连通性...")
        
        checks = []
        
        # 检查东方财富
        try:
            r = requests.get("https://push2.eastmoney.com", timeout=5)
            checks.append(("东方财富 API", True))
        except:
            checks.append(("东方财富 API", False))
        
        # 检查飞书
        try:
            r = requests.get("https://open.feishu.cn", timeout=5)
            checks.append(("飞书 API", True))
        except:
            checks.append(("飞书 API", False))
        
        all_ok = all(c[1] for c in checks)
        status = ", ".join([f"{'?' if c[1] else '?'} {c[0]}" for c in checks])
        self.checks.append(("网络连通", all_ok, status))
        return all_ok
    
    def cleanup_old_files(self):
        """清理旧文件"""
        print("[清理] 旧数据文件...")
        
        cleaned = 0
        retention_days = int(os.environ.get("REPORT_RETENTION_DAYS", "7"))
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for folder in ["charts", "reports"]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    path = os.path.join(folder, f)
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(path))
                        if mtime < cutoff:
                            os.remove(path)
                            cleaned += 1
                    except:
                        pass
        
        if cleaned > 0:
            self.fixes.append(f"清理旧文件: {cleaned} 个")
        return cleaned
    
    def generate_report(self):
        """生成自检报告"""
        passed = sum(1 for c in self.checks if c[1])
        total = len(self.checks)
        
        report = f"""?? 晨报系统自检报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════
? 检查项目 ({passed}/{total} 通过)
═══════════════════════════════════════
"""
        for name, status, detail in self.checks:
            icon = "?" if status else "?"
            report += f"{icon} {name}: {detail}\n"
        
        if self.fixes:
            report += """
═══════════════════════════════════════
?? 自动修复记录
═══════════════════════════════════════
"""
            for fix in self.fixes:
                report += f"? {fix}\n"
        
        if self.errors:
            report += """
═══════════════════════════════════════
?? 未修复错误
═══════════════════════════════════════
"""
            for err in self.errors:
                report += f"? {err}\n"
        
        status_icon = "?" if passed == total else "??" if passed >= total // 2 else "?"
        report += f"""
═══════════════════════════════════════
?? 系统状态：{status_icon} {"就绪" if passed == total else "部分就绪" if passed >= total // 2 else "未就绪"}
? 预计晨报发送时间：08:00
═══════════════════════════════════════
"""
        return report
    
    def send_report(self, report):
        """发送报告到飞书"""
        if not all(self.feishu_config.values()):
            print("[WARNING] 飞书配置不完整，跳过发送")
            return
        
        try:
            # 获取 token
            token_file = ".feishu_token"
            if not os.path.exists(token_file):
                print("[WARNING] Token 不存在，尝试获取...")
                self.fix_feishu_token()
            
            with open(token_file, "r", encoding="utf-8") as f:
                token = f.read().strip().replace('?', '')
            
            # 发送消息
            url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            body = {
                "receive_id": self.feishu_config["chat_id"],
                "msg_type": "text",
                "content": json.dumps({"text": report}, ensure_ascii=False)
            }
            body_bytes = json.dumps(body, ensure_ascii=False).encode('utf-8')
            
            response = requests.post(url, headers=headers, data=body_bytes)
            if response.status_code == 200:
                print("[OK] 报告已发送到飞书")
            else:
                print(f"[ERROR] 发送失败: {response.text}")
        except Exception as e:
            print(f"[ERROR] 发送异常: {e}")
    
    def run(self, fix=False, report=False):
        """执行自检"""
        print(f"\n{'='*50}")
        print("?? 股票晨报系统自检")
        print(f"{'='*50}\n")
        
        # 执行检查
        token_ok = self.check_feishu_token()
        missing_deps = self.check_python_deps()
        missing_dirs = self.check_directories()
        chart_ok = self.check_chart_generation()
        network_ok = self.check_network()
        
        # 自动修复
        if fix:
            print(f"\n{'='*50}")
            print("?? 自动修复")
            print(f"{'='*50}\n")
            
            if not token_ok:
                self.fix_feishu_token()
            if missing_deps:
                self.fix_python_deps(missing_deps)
            if missing_dirs:
                self.fix_directories(missing_dirs)
            
            self.cleanup_old_files()
        
        # 生成报告
        check_report = self.generate_report()
        print(f"\n{'='*50}")
        print(check_report)
        
        # 发送报告
        if report:
            self.send_report(check_report)
        
        # 返回状态
        passed = sum(1 for c in self.checks if c[1])
        return passed == len(self.checks)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="股票晨报系统自检修复")
    parser.add_argument("--fix", action="store_true", help="自动修复问题")
    parser.add_argument("--report", action="store_true", help="发送报告到飞书")
    
    args = parser.parse_args()
    
    checker = SystemChecker()
    success = checker.run(fix=args.fix, report=args.report)
    
    return 0 if success else 1


if __name__ == "__main__":
    import json
    exit(main())
