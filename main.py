import socket
import json
import sys

# 게임과 통신할 설정 (기본값)
HOST = '127.0.0.1'
PORT = 7777

def main():
    print(f"[{HOST}:{PORT}] 게임 연결 대기 중... (게임을 실행하세요)")
    
    try:
        # 소켓 생성 및 연결 시도
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("== 게임에 연결되었습니다! ==")

            buffer = ""
            while True:
                # 데이터 수신
                data = s.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # 데이터가 완전한지 확인 (줄바꿈 등으로 구분됨)
                if "\n" in buffer:
                    # 여러 메시지가 뭉쳐올 수 있으므로 분리
                    messages = buffer.split("\n")
                    buffer = messages[-1] # 처리 안 된 나머지 저장

                    for msg in messages[:-1]:
                        if not msg.strip(): continue
                        
                        try:
                            # JSON 파싱
                            game_state = json.loads(msg)

                            # 1. 현재 가능한 선택지 출력
                            if 'available_commands' in game_state:
                                print("\n" + "="*30)
                                print("[현재 가능한 행동]")
                                for i, cmd in enumerate(game_state['available_commands']):
                                    print(f" {i}: {cmd}")
                                print("="*30)
                            
                            # 2. 게임이 명령을 기다리는 중이라면?
                            # (주의: CommunicationMod가 켜져 있으면 마우스 클릭이 안 될 수 있습니다)
                            if game_state.get('ready_for_command'):
                                # 여기서 AI 로직을 넣거나, 임시로 입력을 받습니다.
                                user_input = input("명령어를 입력하세요 (예: choose 0): ")
                                s.sendall((user_input + "\n").encode('utf-8'))

                        except json.JSONDecodeError:
                            print(f"JSON 해석 오류: {msg}")
                            
    except ConnectionRefusedError:
        print("연결 실패: 게임이 켜져 있지 않거나 CommunicationMod가 로딩되지 않았습니다.")
        print("게임을 먼저 실행하고 메인 메뉴가 뜰 때까지 기다려보세요.")

if __name__ == "__main__":
    main()