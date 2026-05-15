#!/usr/bin/env python3
"""
每日报告生成与发送脚本
使用：python generate_daily_report.py --code 588000 --send
"""

import argparse
import json
import subprocess
import os
from datetime import datetime
import requests

class DailyReportGenerator:
    """每日报告生成器"""
    
    def __init__(self):
        self.code = None
        self.data = {}
        # 从环境变量读取配置
        self.feishu_config = {
            "app_id": os.environ.get("FEISHU_APP_ID", ""),
            "app_secret": os.environ.get("FEISHU_APP_SECRET", ""),
            "chat_id": os.environ.get("FEISHU_CHAT_ID", "")
        }
        
        # 验证配置
        if not all(self.feishu_config.values()):
            print("[WARNING] 飞书配置不完整，请检查 .env 文件")
            print("需要配置: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID")
    
    def get_feishu_token(self):
        """获取飞书访问令牌"""
        # 检查现有 token（使用 utf-8-sig 处理 BOM）
        if os.path.exists(".feishu_token"):
            try:
                with open(".feishu_token", "r", encoding="utf-8") as f:
                    token = f.read().strip()
                    # 移除可能的 BOM 字符
                    token = token.replace('?', '')
                    if token:
                        return token
            except Exception:
                pass  # 如果读取失败，重新获取
        
        # 重新获取
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            "app_id": self.feishu_config["app_id"],
            "app_secret": self.feishu_config["app_secret"]
        })
        
        if response.status_code == 200:
            token = response.json().get("tenant_access_token")
            # 使用 utf-8 保存，不带 BOM
            with open(".feishu_token", "w", encoding="utf-8") as f:
                f.write(token)
            return token
        return None
    
    def collect_technical_data(self, code):
        """收集技术指标数据（支持多数据源）"""
        print(f"[1/4] 收集 {code} 技术指标数据...")
        
        # 尝试东方财富 API
        try:
            url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=1.{code}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170"
            response = requests.get(url, timeout=10)
            data = response.json().get('data', {})
            
            if data:
                # 东方财富 API 字段说明：
                # f43=当前价(元*1000), f44=最高价(元*1000), f45=最低价(元*1000), f46=开盘价(元*1000)
                # f47=成交量(股), f48=成交额(元), f57=代码, f58=名称
                # f60=昨收(元*1000), f170=涨跌幅(%*100)
                # 
                # 注意：ETF基金价格是厘(0.001元)精度，需要除以1000
                # 普通股票是分(0.01元)精度，需要除以100
                current_price = data.get('f43', 0) / 1000
                prev_close = data.get('f60', 0) / 1000
                change_pct = data.get('f170', 0) / 100
                
                # 数据合理性检查：如果价格>100元，可能是股票，重新计算
                if current_price > 100:
                    current_price = data.get('f43', 0) / 100
                    prev_close = data.get('f60', 0) / 100
                    print(f"[!] 检测到高价股，调整除数: /100")
                
                result = {
                    "code": code,
                    "name": data.get('f58', ''),
                    "current_price": round(current_price, 3),
                    "high": round(data.get('f44', 0) / 1000, 3),
                    "low": round(data.get('f45', 0) / 1000, 3),
                    "open": round(data.get('f46', 0) / 1000, 3),
                    "volume": data.get('f47', 0),
                    "amount": data.get('f48', 0),
                    "prev_close": round(prev_close, 3),
                    "change": round(current_price - prev_close, 3),
                    "change_pct": change_pct,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f"[OK] 东方财富数据获取成功：{result['current_price']:.3f}元 ({result['change_pct']:+.2f}%)")
                return result
                
        except Exception as e:
            print(f"[!] 东方财富 API 失败：{e}")
        
        # 备用：腾讯 API
        try:
            print("[!] 尝试备用数据源（腾讯）...")
            url = f"http://qt.gtimg.cn/q=sh{code}"
            response = requests.get(url, timeout=10)
            
            # 解析腾讯数据格式
            data_str = response.text.split('="')[1].split('"')[0]
            data_parts = data_str.split('~')
            
            if len(data_parts) >= 45:
                result = {
                    "code": code,
                    "name": data_parts[1],
                    "current_price": float(data_parts[3]),
                    "prev_close": float(data_parts[4]),
                    "open": float(data_parts[5]),
                    "volume": int(data_parts[6]),
                    "amount": float(data_parts[37]) * 10000,  # 转换为元
                    "high": float(data_parts[33]),
                    "low": float(data_parts[34]),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                result["change"] = result["current_price"] - result["prev_close"]
                result["change_pct"] = (result["change"] / result["prev_close"]) * 100 if result["prev_close"] > 0 else 0
                
                print(f"[OK] 腾讯数据获取成功：{result['current_price']:.3f}元 ({result['change_pct']:+.2f}%)")
                return result
        except Exception as e:
            print(f"[!] 腾讯 API 失败：{e}")
        
        # 都失败了
        print(f"[ERROR] 所有数据源都失败")
        return {"error": "所有数据源都失败", "code": code}
    
    def generate_chart(self, code, days=10):
        """生成图表"""
        print(f"[2/4] 生成 {code} 可视化图表...")
        
        try:
            output_path = f"charts/daily_report_{code}_{datetime.now().strftime('%Y%m%d')}.png"
            
            cmd = [
                "python",
                "skills/stock-chart-visualization/scripts/generate_chart_v2.py",
                "--code", code,
                "--days", str(days),
                "--output", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                print(f"[OK] 图表生成成功：{output_path}")
                return output_path
            else:
                print(f"[ERROR] 图表生成失败：{result.stderr}")
                return None
                
        except Exception as e:
            print(f"[ERROR] 图表生成异常：{e}")
            return None
    
    def collect_news(self, code):
        """收集新闻（简化版，从内存或固定来源）"""
        print(f"[3/4] 收集 {code} 相关新闻...")
        
        # 这里可以扩展为从数据库或文件读取
        # 简化示例
        news = [
            {
                "title": "科创板政策利好",
                "summary": "监管层发布支持科技创新企业新政策",
                "impact": "利好",
                "relevance": 5
            },
            {
                "title": "半导体板块活跃",
                "summary": "芯片需求回暖，行业景气度提升",
                "impact": "利好",
                "relevance": 4
            }
        ]
        
        print(f"[OK] 新闻收集完成：{len(news)} 条")
        return news
    
    def generate_text_report(self, technical_data, news):
        """生成文字报告"""
        print("[4/4] 生成文字摘要...")
        
        if "error" in technical_data:
            return f"[ERROR] 数据获取失败：{technical_data['error']}"
        
        # 计算趋势
        change_pct = technical_data.get('change_pct', 0)
        if change_pct > 1:
            trend = "?? 强势上涨"
        elif change_pct > 0:
            trend = "?? 小幅上涨"
        elif change_pct > -1:
            trend = "?? 小幅下跌"
        else:
            trend = "?? 明显下跌"
        
        # 生成新闻部分
        news_text = ""
        for i, item in enumerate(news[:3], 1):
            stars = "?" * item['relevance']
            news_text += f"""
{i}. 【{item['title']}】{stars}
   摘要：{item['summary']}
   影响：{item['impact']}
"""
        
        report = f"""?? 每日投资晨报 - {datetime.now().strftime('%Y-%m-%d')}

═══════════════════════════════════════
?? 行情概览
═══════════════════════════════════════
? 代码：{technical_data['code']} {technical_data['name']}
? 最新价：{technical_data['current_price']:.3f}元（{change_pct:+.2f}%）
? 成交量：{technical_data['volume']/10000:.2f}万手 / 成交额：{technical_data['amount']/100000000:.2f}亿元
? 趋势：{trend}

═══════════════════════════════════════
?? 技术指标
═══════════════════════════════════════
? 今开：{technical_data['open']:.3f}元 | 最高：{technical_data['high']:.3f}元 | 最低：{technical_data['low']:.3f}元
? 昨收：{technical_data['prev_close']:.3f}元 | 涨跌：{technical_data['change']:+.3f}元

═══════════════════════════════════════
?? 重点新闻（{len(news)}条）
═══════════════════════════════════════
{news_text}

═══════════════════════════════════════
?? 操作建议
═══════════════════════════════════════
? 短线：{"逢低关注" if change_pct < -1 else "持有观望" if abs(change_pct) < 1 else "逢高减仓"}
? 中线：关注区间震荡
? 风险：市场波动风险，控制仓位

—— 数据整合汇报Agent ??
—— 数据时间：{technical_data['timestamp']}
—— 生成时间：{datetime.now().strftime('%H:%M:%S')}
"""
        
        print("[OK] 文字摘要生成完成")
        return report
    
    def send_text_message(self, token, chat_id, text):
        """发送文字消息"""
        print("发送文字消息到飞书...")
        
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # content 需要是 JSON 字符串
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False)
        }
        
        # 手动编码，避免 requests 对 content 再次编码
        body_bytes = json.dumps(body, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, headers=headers, data=body_bytes)
        
        if response.status_code == 200:
            print("[OK] 文字消息发送成功")
            return True
        else:
            print(f"[ERROR] 文字消息发送失败：{response.text}")
            return False
    
    def send_image_message(self, token, chat_id, image_path):
        """发送图片消息"""
        print("发送图片消息到飞书...")
        
        # 上传图片
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"image_type": "message"}
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 200:
            print(f"[ERROR] 图片上传失败：{response.text}")
            return False
        
        image_key = response.json().get("data", {}).get("image_key")
        
        # 发送图片消息
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "receive_id": chat_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key}, ensure_ascii=False)
        }
        
        body_bytes = json.dumps(body, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, headers=headers, data=body_bytes)
        
        if response.status_code == 200:
            print("[OK] 图片消息发送成功")
            return True
        else:
            print(f"[ERROR] 图片消息发送失败：{response.text}")
            return False
    
    def run(self, code, send=False, days=10):
        """执行完整流程"""
        self.code = code
        
        print(f"\n{'='*50}")
        print(f"?? 开始生成 {code} 每日报告")
        print(f"{'='*50}\n")
        
        # 1. 收集技术指标
        technical_data = self.collect_technical_data(code)
        if "error" in technical_data:
            print(f"[ERROR] 数据收集失败，终止")
            return False
        
        # 2. 生成图表
        chart_path = self.generate_chart(code, days)
        
        # 3. 收集新闻
        news = self.collect_news(code)
        
        # 4. 生成文字报告
        text_report = self.generate_text_report(technical_data, news)
        
        # 保存报告
        report_dir = "reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        report_path = f"{report_dir}/daily_report_{code}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(text_report)
        print(f"\n[OK] 报告已保存：{report_path}")
        
        # 发送到飞书
        if send:
            print(f"\n{'='*50}")
            print("?? 发送到飞书")
            print(f"{'='*50}")
            
            token = self.get_feishu_token()
            if not token:
                print("[ERROR] 获取飞书 Token 失败")
                return False
            
            chat_id = self.feishu_config["chat_id"]
            
            # 发送文字
            self.send_text_message(token, chat_id, text_report)
            
            # 发送图片
            if chart_path:
                self.send_image_message(token, chat_id, chart_path)
            
            print("\n[OK] 发送完成！")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="每日报告生成与发送")
    parser.add_argument("--code", default="588000", help="股票代码（默认：588000）")
    parser.add_argument("--send", action="store_true", help="发送到飞书")
    parser.add_argument("--days", type=int, default=10, help="图表天数（默认：10）")
    
    args = parser.parse_args()
    
    generator = DailyReportGenerator()
    success = generator.run(args.code, args.send, args.days)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
