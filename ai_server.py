import socket
import json
import sys
import time
from state_parser import parse_state, print_state_summary

def main():
    HOST = '127.0.0.1'
    PORT = 7777
    
    print("=== 4090 AI 서버 예열 중... ===")
    try:
        import torch
        print(f"GPU 활성화 성공: {torch.cuda.get_device_name(0)}")
    except:
        pass

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    server.settimeout(1.0) 
    
    print(f"=== 4090 본진 수신 대기 중 (포트 {PORT}) ===")
    
    while True:
        try:
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue 
            
            print(f"\n[!] 슬더스 게임 접속 완료! {addr}")
            
            # [핵심] makefile()을 빼고, 0.5초 타임아웃을 걸어 숨통을 틔웁니다.
            conn.settimeout(0.5) 
            buffer = ""
            
            last_command_time = 0
            command_cooldown = 0.5  
            
            waiting_for_next_turn = False
            last_turn = -1
            need_to_print_state = True 
            
            with conn:
                while True:
                    try:
                        # 통째로 데이터를 받아서 버퍼에 이어 붙입니다.
                        chunk = conn.recv(4096).decode('utf-8')
                        if not chunk:
                            break # 빈 문자열이면 연결이 끊긴 것
                        buffer += chunk
                    except socket.timeout:
                        # 0.5초 동안 새 데이터가 없으면 여기로 옵니다. (Ctrl+C 감지 가능!)
                        continue
                    except ConnectionResetError:
                        break # 게임이 강제 종료되었을 때

                    # 버퍼에 쌓인 데이터를 줄바꿈(\n) 기준으로 하나씩 꺼내서 안전하게 처리
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        raw_data = line.strip()
                        if not raw_data: 
                            continue
                        
                        try:
                            parsed_data = json.loads(raw_data)
                            
                            # [스팸 방지 1] 쿨다운
                            if time.time() - last_command_time < command_cooldown:
                                continue
                                
                            parsed_info = parse_state(parsed_data)
                            
                            if parsed_info and parsed_info.get("in_game"):
                                combat = parsed_info.get("combat")
                                current_turn = combat.get("turn", 0) if combat else 0
                                
                                # [스팸 방지 2] 턴 잠금 해제
                                if waiting_for_next_turn:
                                    if current_turn != last_turn:
                                        print(f"\n[!] 새로운 턴 시작 감지! (Turn: {current_turn}) - 잠금 해제")
                                        waiting_for_next_turn = False
                                        need_to_print_state = True
                                    else:
                                        continue 
                                
                                # 상태 출력
                                if need_to_print_state and combat and current_turn > 0:
                                    print_state_summary(parsed_info)
                                    need_to_print_state = False 
                                
                                # AI 명령 하달
                                if "available_commands" in parsed_data:
                                    cmds = parsed_data["available_commands"]
                                    if "end" in cmds and current_turn > 0:
                                        print(">>> AI 판단: 턴 종료 (end) 발사!")
                                        conn.sendall(b"end\n")
                                        
                                        last_command_time = time.time()
                                        waiting_for_next_turn = True
                                        last_turn = current_turn
                                        
                        except json.JSONDecodeError:
                            pass
                            
            print("\n[!] 게임 종료/연결 끊김. 다음 게임 접속 대기 중...")
            
        except KeyboardInterrupt:
            print("\n[!] Ctrl+C 강제 종료 감지: 4090 서버를 완전히 셧다운합니다.")
            server.close()
            sys.exit(0)
        except Exception as e:
            print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()