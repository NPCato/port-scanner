import socket
from IPy import IP
import threading
import queue
import time

class PortScanner:
    def __init__(self, target, start_port, end_port, max_threads=100):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.max_threads = max_threads
        self.open_ports = []
        self.thread_queue = queue.Queue()

    def check_ip(self):
        try:
            IP(self.target)
            return self.target
        except ValueError:
            try:
                return socket.gethostbyname(self.target)
            except socket.gaierror:
                print(f"Invalid target: {self.target}")
                return None

    def scan_port(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                
                if result == 0:
                    try:
                        sock.send(b'Hello\r\n')
                        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                        
                        self.open_ports.append({
                            'port': port,
                            'banner': banner if banner else 'No banner retrieved'
                        })
                        
                        print(f"port {port} is open: {banner if banner else 'no details'}")
                    except Exception as e:
                        print(f"port {port} is open but unable to retirive banner")
        except Exception as e:
            pass

    def worker(self, ip):
        while not self.thread_queue.empty():
            port = self.thread_queue.get()
            self.scan_port(ip, port)
            self.thread_queue.task_done()

    def scan(self):
        ip = self.check_ip()
        if not ip:
            return

        for port in range(self.start_port, self.end_port + 1):
            self.thread_queue.put(port)

        threads = []
        for _ in range(min(self.max_threads, self.thread_queue.qsize())):
            thread = threading.Thread(target=self.worker, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        self.thread_queue.join()
        for thread in threads:
            thread.join()

        print("\n--- Scan Complete ---")
        print(f"total open ports: {len(self.open_ports)}")
        for port_info in sorted(self.open_ports, key=lambda x: x['port']):
            print(f"port {port_info['port']}: {port_info['banner']}")

def main():
    try:
        print("port scanner")
        target = input("enter target:")
        start_port = int(input("enter start port: "))
        end_port = int(input("enter end port: "))

        if start_port > end_port:
            print("start port must be less than or equal to end port")
            return

        scanner = PortScanner(target, start_port, end_port)
        start_time = time.time()
        scanner.scan()
        end_time = time.time()
        
        print(f"scan completed in {end_time - start_time:.2f} seconds")

    except ValueError:
        print("invalid port")
    except KeyboardInterrupt:
        print("scan stopped by user")

if __name__ == "__main__":
    main()