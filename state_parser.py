import json
import os

def parse_state(parsed_data):
    # ai_server.py 의 턴 진행 로직이 에러나지 않도록 최소한의 구조만 흉내냅니다.
    game_state = parsed_data.get("game_state", {})
    combat_state = game_state.get("combat_state", {})
    
    return {
        "in_game": parsed_data.get("in_game", False),
        "combat": {
            "turn": combat_state.get("turn", 0)
        },
        "raw_data": parsed_data # 원본 데이터를 그대로 담아서 넘김
    }

def print_state_summary(state_dict):
    raw_data = state_dict.get("raw_data", {})
    file_name = "state_dump.json"
    
    try:
        # JSON 데이터를 보기 좋게 들여쓰기(indent=2)하여 파일로 저장
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
            
        print("\n" + "▼"*50)
        print(f"📥 [원본 JSON 데이터 저장 완료]")
        print(f"📁 파일 위치: {os.path.abspath(file_name)}")
        print("▼"*50 + "\n")
        
    except Exception as e:
        print(f"\n[!] 파일 저장 중 에러 발생: {e}")