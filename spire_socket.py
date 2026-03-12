import socket
import json

class SpireSocketServer:
    def __init__(self, host='0.0.0.0', port=7777):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.server.settimeout(1.0) # Ctrl+C 감지를 위한 숨통
        self.conn = None
        self.addr = None
        self.buffer = ""

    def wait_for_connection(self):
        """슬더스 연결을 대기합니다. 타임아웃을 이용해 무한루프를 돌며 강제종료를 감지합니다."""
        print(f"=== 4090 본진 수신 대기 중 (포트 {self.port}) ===")
        while True:
            try:
                self.conn, self.addr = self.server.accept()
                print(f"\n[!] 슬더스 접속 완료! {self.addr} - 무한 런을 시작합니다.")
                self.conn.settimeout(0.5) 
                self.buffer = ""
                return
            except socket.timeout:
                pass 

    def read_messages(self):
        """소켓에서 데이터를 읽어와서 완성된 JSON(딕셔너리) 리스트로 반환합니다.
        연결이 끊어졌다면 None을 반환합니다."""
        try:
            chunk = self.conn.recv(4096).decode('utf-8')
            if not chunk: 
                return None # 빈 문자열이면 연결 끊김
            self.buffer += chunk
        except socket.timeout:
            return []
        except (ConnectionResetError, BrokenPipeError):
            return None

        messages = []
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            raw_data = line.strip()
            if not raw_data: continue
            
            try:
                messages.append(json.loads(raw_data))
            except json.JSONDecodeError:
                pass
                
        return messages

    def send_command(self, cmd):
        """게임으로 명령을 보내고, 남은 과거 버퍼를 깔끔하게 비웁니다."""
        if self.conn:
            self.conn.sendall(cmd.encode('utf-8'))
            self.buffer = "" 

    def close_connection(self):
        """현재 런 연결만 닫습니다."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def close_server(self):
        """서버 소켓 자체를 완전히 내립니다."""
        self.close_connection()
        self.server.close()