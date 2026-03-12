class ChoiceAI:
    def __init__(self):
        pass

    def get_action(self, parsed_data, parsed_info):
        cmds = parsed_data.get("available_commands", [])
        
        # 1순위: 선택할 게 있으면 무조건 먼저 고른다 (보상 줍기, 맵 경로 선택, 카드 고르기 등)
        if "choose" in cmds:
            return "choose 0\n"
            
        # 2순위: 선택이 다 끝났거나 다음 화면으로 넘어가야 할 때
        # proceed(진행), confirm(확인), leave(상점/모닥불 떠나기), skip(카드 보상 넘기기)
        for cmd in ["proceed", "confirm", "leave", "skip"]:
            if cmd in cmds:
                return f"{cmd}\n"
                
        # 3순위: 정말 다른 선택지가 없고 뒤로 가야만 할 때 (최하위 짬처리)
        if "return" in cmds:
            return "return\n"
            
        return None