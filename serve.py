"""
PWA 로컬 서버 실행기
Usage: python serve.py
iPhone에서 접속: http://<이 PC의 IP>:8080
"""
import http.server, socketserver, socket, os, webbrowser

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    def log_message(self, fmt, *args):
        pass  # suppress request logs

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return 'localhost'

ip = get_local_ip()
print(f"\n수자원개발기술사 PWA 서버 시작")
print(f"{'─'*40}")
print(f"  PC 브라우저: http://localhost:{PORT}")
print(f"  아이폰 접속: http://{ip}:{PORT}")
print(f"{'─'*40}")
print(f"  [아이폰 설치 방법]")
print(f"  1. 위 주소를 Safari에서 열기")
print(f"  2. 공유 버튼 → '홈 화면에 추가'")
print(f"{'─'*40}")
print(f"  종료: Ctrl+C\n")

webbrowser.open(f'http://localhost:{PORT}')

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
