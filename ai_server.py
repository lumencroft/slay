import sys
from spire_socket import SpireSocketServer
from state_parser import parse_state, print_state_summary
from combat_ai import CombatAI
from choice_ai import ChoiceAI

def main():
    print("=== 4090 AI 딥러닝 서버 (무한 자동화) ===")
    
    # 분리된 통신 모듈과 AI 모듈 장전
    server = SpireSocketServer(host='0.0.0.0', port=7777)
    combat_ai = CombatAI()
    choice_ai = ChoiceAI()

    try:
        import torch
        print(f"GPU 활성화 성공: {torch.cuda.get_device_name(0)}")
    except:
        pass

    while True:
        try:
            # 1. 게임 연결 대기
            server.wait_for_connection()
            
            # 2. 게임 시작 상태
            in_run = True
            while in_run:
                # 소켓에서 JSON 메시지 뭉치를 받아옴
                messages = server.read_messages()
                
                if messages is None:
                    break # 게임 연결 끊김 감지, 메인 루프로 돌아가서 다시 대기
                    
                for parsed_data in messages:
                    # 애니메이션 중이면 데이터 무시
                    if not parsed_data.get("ready_for_command", False):
                        continue
                        
                    # --- 1. 메인 메뉴 (죽었거나 새로 켰을 때) ---
                    if not parsed_data.get("in_game", False):
                        cmds = parsed_data.get("available_commands", [])
                        if "start" in cmds:
                            print(">>> [메인 메뉴] 새 게임을 시작합니다 (Ironclad)")
                            server.send_command("start ironclad\n")
                            break # 커맨드를 보냈으면 다음 메시지는 무시하고 통신 루프 재시작
                        continue

                    # --- 2. 게임 중 (파싱 및 상황별 AI 라우팅) ---
                    parsed_info = parse_state(parsed_data)
                    if not parsed_info: continue

                    action = None
                    room_phase = parsed_info.get("room_phase", "UNKNOWN")
                    
                    if room_phase == "COMBAT":
                        action = combat_ai.get_action(parsed_data, parsed_info)
                    else:
                        action = choice_ai.get_action(parsed_data, parsed_info)
                        
                    # AI가 결정을 내렸다면 게임에 전송
                    if action:
                        print(f"[{room_phase}] AI 결정 -> {action.strip()}")
                        server.send_command(action)
                        break 
                        
            print("\n[!] 런 종료. 새 게임 대기 중...")
            server.close_connection()
            
        except KeyboardInterrupt:
            print("\n[!] Ctrl+C 강제 종료 감지. 서버를 내립니다.")
            server.close_server()
            sys.exit(0)

if __name__ == "__main__":
    main()