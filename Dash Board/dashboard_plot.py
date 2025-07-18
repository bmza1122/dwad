#!/usr/bin/env python3
"""
dashboard_plot.py - สคริปต์แสดงกราฟคุณภาพเครือข่าย
รองรับการแสดงผลแบบหลายรูปแบบ
"""

import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os
import sys
from typing import List, Dict, Optional

# ตั้งค่าฟอนต์ไทย
plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma', 'Arial']
plt.rcParams['font.size'] = 10

class NetworkDashboard:
    def __init__(self, log_file: str = "network_log.csv"):
        """
        เริ่มต้น Dashboard
        
        Args:
            log_file: ชื่อไฟล์ CSV ที่มีข้อมูล
        """
        self.log_file = log_file
        self.data = None
        self.load_data()
    
    def load_data(self):
        """โหลดข้อมูลจากไฟล์ CSV"""
        if not os.path.exists(self.log_file):
            print(f"❌ ไม่พบไฟล์ {self.log_file}")
            return
        
        try:
            # อ่านข้อมูล
            self.data = pd.read_csv(self.log_file)
            
            # แปลงเวลาให้เป็น datetime
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            
            # กรองข้อมูลที่สำเร็จเท่านั้น
            self.data = self.data[self.data['status'] == 'success'].copy()
            
            print(f"📊 โหลดข้อมูลแล้ว: {len(self.data)} รายการ")
            
            if len(self.data) == 0:
                print("⚠️  ไม่มีข้อมูลที่ใช้ได้")
                return
            
            # แสดงสถิติข้อมูล
            print(f"📅 ระยะเวลา: {self.data['timestamp'].min()} ถึง {self.data['timestamp'].max()}")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
            self.data = None
    
    def create_summary_plot(self, days: int = 7):
        """
        สร้างกราฟสรุปคุณภาพเครือข่าย
        
        Args:
            days: จำนวนวันย้อนหลังที่จะแสดง
        """
        if self.data is None or len(self.data) == 0:
            print("❌ ไม่มีข้อมูลให้แสดง")
            return
        
        # กรองข้อมูลตามจำนวนวัน
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        filtered_data = self.data[self.data['timestamp'] >= cutoff_date].copy()
        
        if len(filtered_data) == 0:
            print(f"❌ ไม่มีข้อมูลใน {days} วันที่ผ่านมา")
            return
        
        # สร้างกราฟ
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f'Network Quality Dashboard - Last {days} Days', fontsize=16, fontweight='bold')
        
        # กราฟ Ping
        axes[0].plot(filtered_data['timestamp'], filtered_data['ping_ms'], 
                    color='red', marker='o', markersize=3, linewidth=1.5)
        axes[0].set_title('🏓 Ping (ms)', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Ping (ms)')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylim(0, max(filtered_data['ping_ms']) * 1.1)
        
        # กราฟ Download Speed
        axes[1].plot(filtered_data['timestamp'], filtered_data['download_mbps'], 
                    color='green', marker='o', markersize=3, linewidth=1.5)
        axes[1].set_title('⬇️ Download Speed (Mbps)', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Download (Mbps)')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim(0, max(filtered_data['download_mbps']) * 1.1)
        
        # กราฟ Upload Speed
        axes[2].plot(filtered_data['timestamp'], filtered_data['upload_mbps'], 
                    color='blue', marker='o', markersize=3, linewidth=1.5)
        axes[2].set_title('⬆️ Upload Speed (Mbps)', fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Upload (Mbps)')
        axes[2].set_xlabel('Time')
        axes[2].grid(True, alpha=0.3)
        axes[2].set_ylim(0, max(filtered_data['upload_mbps']) * 1.1)
        
        # ตั้งค่าการแสดงเวลา
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # บันทึกและแสดงผล
        filename = f'network_dashboard_{days}days.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 บันทึกกราฟแล้ว: {filename}")
        plt.show()
    
    def create_statistics_plot(self):
        """สร้างกราฟสถิติและการกระจายข้อมูล"""
        if self.data is None or len(self.data) == 0:
            print("❌ ไม่มีข้อมูลให้แสดง")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Network Statistics & Distribution', fontsize=16, fontweight='bold')
        
        # Histogram - Ping
        axes[0,0].hist(self.data['ping_ms'], bins=20, color='red', alpha=0.7, edgecolor='black')
        axes[0,0].set_title('🏓 Ping Distribution')
        axes[0,0].set_xlabel('Ping (ms)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].grid(True, alpha=0.3)
        
        # Histogram - Download
        axes[0,1].hist(self.data['download_mbps'], bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0,1].set_title('⬇️ Download Speed Distribution')
        axes[0,1].set_xlabel('Download (Mbps)')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].grid(True, alpha=0.3)
        
        # Histogram - Upload
        axes[0,2].hist(self.data['upload_mbps'], bins=20, color='blue', alpha=0.7, edgecolor='black')
        axes[0,2].set_title('⬆️ Upload Speed Distribution')
        axes[0,2].set_xlabel('Upload (Mbps)')
        axes[0,2].set_ylabel('Frequency')
        axes[0,2].grid(True, alpha=0.3)
        
        # Box Plot - Ping
        axes[1,0].boxplot(self.data['ping_ms'], patch_artist=True, 
                         boxprops=dict(facecolor='red', alpha=0.7))
        axes[1,0].set_title('🏓 Ping Box Plot')
        axes[1,0].set_ylabel('Ping (ms)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Box Plot - Download
        axes[1,1].boxplot(self.data['download_mbps'], patch_artist=True, 
                         boxprops=dict(facecolor='green', alpha=0.7))
        axes[1,1].set_title('⬇️ Download Box Plot')
        axes[1,1].set_ylabel('Download (Mbps)')
        axes[1,1].grid(True, alpha=0.3)
        
        # Box Plot - Upload
        axes[1,2].boxplot(self.data['upload_mbps'], patch_artist=True, 
                         boxprops=dict(facecolor='blue', alpha=0.7))
        axes[1,2].set_title('⬆️ Upload Box Plot')
        axes[1,2].set_ylabel('Upload (Mbps)')
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # บันทึกและแสดงผล
        filename = 'network_statistics.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 บันทึกกราฟสถิติแล้ว: {filename}")
        plt.show()
    
    def create_hourly_analysis(self):
        """วิเคราะห์คุณภาพเครือข่ายตามชั่วโมง"""
        if self.data is None or len(self.data) == 0:
            print("❌ ไม่มีข้อมูลให้แสดง")
            return
        
        # เพิ่มคอลัมน์ชั่วโมง
        self.data['hour'] = self.data['timestamp'].dt.hour
        
        # คำนวณค่าเฉลี่ยตามชั่วโมง
        hourly_stats = self.data.groupby('hour').agg({
            'ping_ms': ['mean', 'std'],
            'download_mbps': ['mean', 'std'],
            'upload_mbps': ['mean', 'std']
        }).round(2)
        
        # สร้างกราฟ
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Hourly Network Performance Analysis', fontsize=16, fontweight='bold')
        
        hours = range(24)
        
        # กราฟ Ping ตามชั่วโมง
        ping_means = [hourly_stats.loc[h, ('ping_ms', 'mean')] if h in hourly_stats.index else np.nan for h in hours]
        ping_stds = [hourly_stats.loc[h, ('ping_ms', 'std')] if h in hourly_stats.index else 0 for h in hours]
        
        axes[0].bar(hours, ping_means, yerr=ping_stds, color='red', alpha=0.7, capsize=5)
        axes[0].set_title('🏓 Average Ping by Hour')
        axes[0].set_xlabel('Hour of Day')
        axes[0].set_ylabel('Ping (ms)')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xticks(range(0, 24, 2))
        
        # กราฟ Download ตามชั่วโมง
        download_means = [hourly_stats.loc[h, ('download_mbps', 'mean')] if h in hourly_stats.index else np.nan for h in hours]
        download_stds = [hourly_stats.loc[h, ('download_mbps', 'std')] if h in hourly_stats.index else 0 for h in hours]
        
        axes[1].bar(hours, download_means, yerr=download_stds, color='green', alpha=0.7, capsize=5)
        axes[1].set_title('⬇️ Average Download Speed by Hour')
        axes[1].set_xlabel('Hour of Day')
        axes[1].set_ylabel('Download (Mbps)')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(0, 24, 2))
        
        # กราฟ Upload ตามชั่วโมง
        upload_means = [hourly_stats.loc[h, ('upload_mbps', 'mean')] if h in hourly_stats.index else np.nan for h in hours]
        upload_stds = [hourly_stats.loc[h, ('upload_mbps', 'std')] if h in hourly_stats.index else 0 for h in hours]
        
        axes[2].bar(hours, upload_means, yerr=upload_stds, color='blue', alpha=0.7, capsize=5)
        axes[2].set_title('⬆️ Average Upload Speed by Hour')
        axes[2].set_xlabel('Hour of Day')
        axes[2].set_ylabel('Upload (Mbps)')
        axes[2].grid(True, alpha=0.3)
        axes[2].set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        
        # บันทึกและแสดงผล
        filename = 'network_hourly_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 บันทึกกราฟวิเคราะห์รายชั่วโมงแล้ว: {filename}")
        plt.show()
    
    def print_summary_stats(self):
        """แสดงสถิติสรุป"""
        if self.data is None or len(self.data) == 0:
            print("❌ ไม่มีข้อมูลให้แสดง")
            return
        
        print("\n📊 สถิติสรุปคุณภาพเครือข่าย")
        print("=" * 50)
        
        # คำนวณสถิติ
        stats = {
            'Ping (ms)': self.data['ping_ms'].describe(),
            'Download (Mbps)': self.data['download_mbps'].describe(),
            'Upload (Mbps)': self.data['upload_mbps'].describe()
        }
        
        for metric, stat in stats.items():
            print(f"\n{metric}:")
            print(f"  📏 ค่าเฉลี่ย: {stat['mean']:.2f}")
            print(f"  📊 ค่ากลาง: {stat['50%']:.2f}")
            print(f"  📈 ค่าสูงสุด: {stat['max']:.2f}")
            print(f"  📉 ค่าต่ำสุด: {stat['min']:.2f}")
            print(f"  📋 ส่วนเบี่ยงเบนมาตรฐาน: {stat['std']:.2f}")
        
        # ช่วงเวลาข้อมูล
        time_range = self.data['timestamp'].max() - self.data['timestamp'].min()
        print(f"\n⏰ ช่วงเวลาข้อมูล: {time_range}")
        print(f"📅 จำนวนการทดสอบ: {len(self.data)} ครั้ง")
        
        # คุณภาพการเชื่อมต่อ
        avg_ping = self.data['ping_ms'].mean()
        avg_download = self.data['download_mbps'].mean()
        avg_upload = self.data['upload_mbps'].mean()
        
        print(f"\n🎯 การประเมินคุณภาพ:")
        
        # ประเมิน Ping
        if avg_ping < 50:
            ping_quality = "ดีเยี่ยม"
        elif avg_ping < 100:
            ping_quality = "ดี"
        elif avg_ping < 150:
            ping_quality = "ปานกลาง"
        else:
            ping_quality = "ต้องปรับปรุง"
        
        print(f"  🏓 Ping: {ping_quality} ({avg_ping:.1f} ms)")
        
        # ประเมิน Download
        if avg_download > 100:
            download_quality = "ดีเยี่ยม"
        elif avg_download > 50:
            download_quality = "ดี"
        elif avg_download > 25:
            download_quality = "ปานกลาง"
        else:
            download_quality = "ต้องปรับปรุง"
        
        print(f"  ⬇️ Download: {download_quality} ({avg_download:.1f} Mbps)")
        
        # ประเมิน Upload
        if avg_upload > 50:
            upload_quality = "ดีเยี่ยม"
        elif avg_upload > 25:
            upload_quality = "ดี"
        elif avg_upload > 10:
            upload_quality = "ปานกลาง"
        else:
            upload_quality = "ต้องปรับปรุง"
        
        print(f"  ⬆️ Upload: {upload_quality} ({avg_upload:.1f} Mbps)")
        
        # คำแนะนำ
        print(f"\n💡 คำแนะนำ:")
        if avg_ping > 100:
            print("  • Ping สูง - ตรวจสอบการเชื่อมต่อหรือเปลี่ยนเซิร์ฟเวอร์")
        if avg_download < 25:
            print("  • Download ช้า - ติดต่อผู้ให้บริการหรือเปลี่ยนแพ็คเกจ")
        if avg_upload < 10:
            print("  • Upload ช้า - อาจส่งผลต่อการประชุมออนไลน์")
        
        if avg_ping < 50 and avg_download > 50 and avg_upload > 25:
            print("  • เครือข่ายมีคุณภาพดี สามารถใช้งานได้อย่างมีประสิทธิภาพ")

def main():
    """ฟังก์ชันหลักสำหรับรันโปรแกรม"""
    print("🌐 Network Dashboard")
    print("=" * 30)
    
    # สร้าง Dashboard
    dashboard = NetworkDashboard()
    
    if dashboard.data is None:
        print("❌ ไม่สามารถโหลดข้อมูลได้")
        return
    
    # แสดงเมนู
    while True:
        print("\n📋 เลือกการทำงาน:")
        print("1. แสดงกราฟสรุป 7 วัน")
        print("2. แสดงกราฟสรุป 30 วัน")
        print("3. แสดงกราฟสถิติ")
        print("4. วิเคราะห์รายชั่วโมง")
        print("5. แสดงสถิติตัวเลข")
        print("6. ออกจากโปรแกรม")
        
        choice = input("\n🎯 เลือกหมายเลข (1-6): ").strip()
        
        if choice == '1':
            dashboard.create_summary_plot(7)
        elif choice == '2':
            dashboard.create_summary_plot(30)
        elif choice == '3':
            dashboard.create_statistics_plot()
        elif choice == '4':
            dashboard.create_hourly_analysis()
        elif choice == '5':
            dashboard.print_summary_stats()
        elif choice == '6':
            print("👋 ขอบคุณที่ใช้งาน!")
            break
        else:
            print("❌ กรุณาเลือกหมายเลข 1-6")

if __name__ == "__main__":
    main()
