#!/usr/bin/env python3
"""
collect_data.py - สคริปต์เก็บข้อมูลคุณภาพเครือข่ายอินเทอร์เน็ต
รองรับการทำงานแบบตั้งเวลาอัตโนมัติ
"""

import csv
import datetime
import os
import sys
import time
import subprocess
import json
from typing import Dict, Optional

class NetworkQualityCollector:
    def __init__(self, log_file: str = "network_log.csv"):
        """
        เริ่มต้นระบบเก็บข้อมูล
        
        Args:
            log_file: ชื่อไฟล์ CSV สำหรับบันทึกข้อมูล
        """
        self.log_file = log_file
        self.setup_csv()
    
    def setup_csv(self):
        """สร้างไฟล์ CSV และใส่ header ถ้ายังไม่มี"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp',
                    'ping_ms',
                    'download_mbps',
                    'upload_mbps',
                    'server_name',
                    'server_location',
                    'status'
                ])
    
    def run_speedtest(self) -> Dict:
        """
        ทำการทดสอบความเร็วเครือข่าย
        
        Returns:
            Dict: ผลการทดสอบ
        """
        try:
            print("🔍 กำลังทดสอบความเร็วเครือข่าย...")
            
            # รัน speedtest-cli และรับผลในรูปแบบ JSON
            result = subprocess.run(
                ['speedtest-cli', '--json'],
                capture_output=True,
                text=True,
                timeout=120  # timeout 2 นาที
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # แปลงข้อมูลเป็น Mbps
                download_mbps = round(data['download'] / 1_000_000, 2)
                upload_mbps = round(data['upload'] / 1_000_000, 2)
                ping_ms = round(data['ping'], 2)
                
                return {
                    'ping_ms': ping_ms,
                    'download_mbps': download_mbps,
                    'upload_mbps': upload_mbps,
                    'server_name': data['server']['name'],
                    'server_location': f"{data['server']['country']}, {data['server']['name']}",
                    'status': 'success'
                }
            else:
                print(f"❌ เกิดข้อผิดพลาด: {result.stderr}")
                return {
                    'ping_ms': 0,
                    'download_mbps': 0,
                    'upload_mbps': 0,
                    'server_name': 'N/A',
                    'server_location': 'N/A',
                    'status': 'failed'
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ การทดสอบหมดเวลา")
            return {
                'ping_ms': 0,
                'download_mbps': 0,
                'upload_mbps': 0,
                'server_name': 'N/A',
                'server_location': 'N/A',
                'status': 'timeout'
            }
        except Exception as e:
            print(f"💥 เกิดข้อผิดพลาด: {str(e)}")
            return {
                'ping_ms': 0,
                'download_mbps': 0,
                'upload_mbps': 0,
                'server_name': 'N/A',
                'server_location': 'N/A',
                'status': 'error'
            }
    
    def save_to_csv(self, data: Dict):
        """
        บันทึกข้อมูลลงไฟล์ CSV
        
        Args:
            data: ข้อมูลที่จะบันทึก
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                data['ping_ms'],
                data['download_mbps'],
                data['upload_mbps'],
                data['server_name'],
                data['server_location'],
                data['status']
            ])
    
    def collect_once(self):
        """เก็บข้อมูลหนึ่งครั้ง"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n📊 [{timestamp}] เริ่มเก็บข้อมูลเครือข่าย")
        
        # ทำการทดสอบ
        result = self.run_speedtest()
        
        # แสดงผล
        if result['status'] == 'success':
            print(f"✅ ผลการทดสอบ:")
            print(f"   🏓 Ping: {result['ping_ms']} ms")
            print(f"   ⬇️  Download: {result['download_mbps']} Mbps")
            print(f"   ⬆️  Upload: {result['upload_mbps']} Mbps")
            print(f"   🖥️  Server: {result['server_location']}")
        else:
            print(f"❌ การทดสอบล้มเหลว: {result['status']}")
        
        # บันทึกลง CSV
        self.save_to_csv(result)
        print(f"💾 บันทึกข้อมูลแล้ว -> {self.log_file}")
        
        return result
    
    def collect_continuous(self, interval_minutes: int = 30):
        """
        เก็บข้อมูลต่อเนื่อง
        
        Args:
            interval_minutes: ช่วงเวลาระหว่างการเก็บข้อมูล (นาที)
        """
        print(f"🔄 เริ่มเก็บข้อมูลต่อเนื่องทุก {interval_minutes} นาที")
        print("⏹️  กด Ctrl+C เพื่อหยุด")
        
        try:
            while True:
                self.collect_once()
                print(f"⏰ รอ {interval_minutes} นาที...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 หยุดการเก็บข้อมูล")
    
    def show_recent_data(self, lines: int = 10):
        """
        แสดงข้อมูลล่าสุด
        
        Args:
            lines: จำนวนบรรทัดที่จะแสดง
        """
        if not os.path.exists(self.log_file):
            print("📂 ยังไม่มีข้อมูล")
            return
        
        print(f"\n📈 ข้อมูล {lines} ครั้งล่าสุด:")
        print("-" * 80)
        
        with open(self.log_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = list(reader)
            
            if len(data) <= 1:
                print("📂 ยังไม่มีข้อมูล")
                return
            
            # แสดง header
            header = data[0]
            print(f"{'เวลา':<20} {'Ping':<8} {'Down':<8} {'Up':<8} {'สถานะ':<10}")
            print("-" * 80)
            
            # แสดงข้อมูลล่าสุด
            recent_data = data[-lines:] if len(data) > lines else data[1:]
            for row in recent_data:
                if len(row) >= 7:
                    print(f"{row[0]:<20} {row[1]:<8} {row[2]:<8} {row[3]:<8} {row[6]:<10}")


def main():
    """ฟังก์ชันหลักสำหรับรันสคริปต์"""
    collector = NetworkQualityCollector()
    
    if len(sys.argv) == 1:
        # ถ้าไม่มี argument แสดง help
        print("🌐 Dashboard ตรวจสอบคุณภาพเครือข่ายอินเทอร์เน็ต")
        print("=" * 50)
        print("\nการใช้งาน:")
        print("  python collect_data.py once           - เก็บข้อมูล 1 ครั้ง")
        print("  python collect_data.py continuous     - เก็บข้อมูลต่อเนื่องทุก 30 นาที")
        print("  python collect_data.py continuous 15  - เก็บข้อมูลต่อเนื่องทุก 15 นาที")
        print("  python collect_data.py show          - แสดงข้อมูลล่าสุด")
        print("  python collect_data.py show 20       - แสดงข้อมูล 20 ครั้งล่าสุด")
        print("\n📋 ข้อมูลจะถูกบันทึกในไฟล์ 'network_log.csv'")
        return
    
    command = sys.argv[1].lower()
    
    if command == "once":
        collector.collect_once()
        
    elif command == "continuous":
        interval = 30
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                print("❌ ช่วงเวลาต้องเป็นตัวเลข")
                return
        collector.collect_continuous(interval)
        
    elif command == "show":
        lines = 10
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
            except ValueError:
                print("❌ จำนวนบรรทัดต้องเป็นตัวเลข")
                return
        collector.show_recent_data(lines)
        
    else:
        print("❌ คำสั่งไม่ถูกต้อง ใช้: once, continuous, หรือ show")


if __name__ == "__main__":
    main()