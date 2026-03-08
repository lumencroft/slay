import sys
import socket
import threading
import os

def receive_from_server(s):
    try:
        # 4090 서버에서 온 명령("end", "play 1" 등)을 게임으로 쏨
        for line in s.makefile('r', encoding='utf-8'):
            print(line.strip())
            sys.stdout.flush()
    except:
        pass
    finally:
        os._exit(0)

def main():
    try:
        # 네가 켜둔 4090 본진 서버에 접속
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 7777))
    except Exception:
        # 서버 안 켜져 있으면 게임 먹통 안 되게 조용히 자폭
        os._exit(0)

    # 핵심: 게임한테 "나 준비됐어! 데이터 내놔!" 라고 외침
    print("ready")
    sys.stdout.flush()

    # 서버 명령 대기 스레드 실행
    t = threading.Thread(target=receive_from_server, args=(s,))
    t.daemon = True
    t.start()

    # 게임에서 나오는 JSON 데이터를 4090 서버로 전부 전달
    try:
        for line in sys.stdin:
            s.sendall(line.encode('utf-8'))
    except:
        pass

if __name__ == "__main__":
    main()