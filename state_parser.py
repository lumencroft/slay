def parse_state(parsed_data):
    game_state = parsed_data.get("game_state", {})
    if not game_state:
        return None
        
    in_game = parsed_data.get("in_game", False)
    room_phase = game_state.get("room_phase", "UNKNOWN")
    
    player_stats = {
        "class": game_state.get("class", "UNKNOWN"),
        "hp": game_state.get("current_hp", 0),
        "max_hp": game_state.get("max_hp", 0),
        "gold": game_state.get("gold", 0),
        "floor": game_state.get("floor", 0),
        "ascension": game_state.get("ascension_level", 0),
        "relics": [r.get("id", "Unknown") for r in game_state.get("relics", [])],
        "potions": [p.get("id", "Empty") for p in game_state.get("potions", [])]
    }
    
    state_dict = {
        "in_game": in_game,
        "room_phase": room_phase,
        "player_stats": player_stats,
        "combat": None
    }

    combat_state = game_state.get("combat_state")
    if combat_state and room_phase == "COMBAT":
        player = combat_state.get("player", {})
        
        hand = []
        for c in combat_state.get("hand", []):
            hand.append({
                "id": c.get("id", "Unknown"),
                "cost": c.get("cost", 0),
                "type": c.get("type", "UNKNOWN"),
                "is_playable": c.get("is_playable", False),
                "has_target": c.get("has_target", False)
            })
            
        monsters = []
        for m in combat_state.get("monsters", []):
            if not m.get("is_gone"):
                monsters.append({
                    "id": m.get("id", "Unknown"),
                    "hp": m.get("current_hp", 0),
                    "max_hp": m.get("max_hp", 0),
                    "block": m.get("block", 0),
                    "intent": m.get("intent", "UNKNOWN"),
                    "damage": m.get("move_adjusted_damage", 0), # 추가됨
                    "hits": m.get("move_hits", 1)               # 추가됨
                })

        state_dict["combat"] = {
            "turn": combat_state.get("turn", 0),
            "energy": player.get("energy", 0),
            "block": player.get("block", 0),
            "hand": hand,
            "draw_pile_count": len(combat_state.get("draw_pile", [])),
            "discard_pile_count": len(combat_state.get("discard_pile", [])),
            "monsters": monsters
        }

    return state_dict

def print_state_summary(state_dict):
    if not state_dict or not state_dict["in_game"]:
        return

    p_stats = state_dict["player_stats"]
    print(f"\n========== [게임 상황 요약 (Floor {p_stats['floor']})] ==========")
    print(f"클래스: {p_stats['class']} | 승천: {p_stats['ascension']}")
    print(f"🩸 HP: {p_stats['hp']}/{p_stats['max_hp']} | 💰 골드: {p_stats['gold']}")
    
    combat = state_dict.get("combat")
    if combat:
        if combat['turn'] == 0 or not combat['hand']:
            print("⏳ 전투 초기화 중... (대기)")
            print("=========================================================\n")
            return

        print(f"\n⚔️ [전투 상세 정보 (Turn {combat['turn']})]")
        print(f"⚡ 에너지: {combat['energy']} | 🛡️ 방어도: {combat['block']}")
        
        print("\n🃏 내 손패:")
        for i, card in enumerate(combat['hand']):
            playable_mark = "⭕" if card['is_playable'] else "❌"
            print(f"  [{i+1}] {card['id']} (비용: {card['cost']}) [{playable_mark}]")
            
        print("\n👾 적 정보:")
        for m in combat['monsters']:
            dmg_str = f" (공격: {m['damage']}x{m['hits']})" if "ATTACK" in m['intent'] else ""
            print(f"  - {m['id']} (HP: {m['hp']}/{m['max_hp']} | 방어도: {m['block']}) | 의도: {m['intent']}{dmg_str}")
    print("=========================================================\n")