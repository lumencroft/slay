CARD_DB = {
    "Strike_R": {"block": 0, "damage": 6},
    "Defend_R": {"block": 5, "damage": 0},
    "Bash": {"block": 0, "damage": 8}
}

class CombatAI:
    def __init__(self):
        pass

    def get_best_action_sequence(self, hand, current_energy, current_block, incoming_damage):
        valid_sequences = []
        
        def find_combinations(energy_left, remaining_hand, current_seq):
            added = False
            for i, card in enumerate(remaining_hand):
                if card['is_playable'] and card['cost'] <= energy_left:
                    added = True
                    next_hand = remaining_hand[:i] + remaining_hand[i+1:]
                    find_combinations(energy_left - card['cost'], next_hand, current_seq + [card])
            
            if not added and current_seq:
                valid_sequences.append(current_seq)

        hand_with_indices = [dict(c, hand_index=i+1) for i, c in enumerate(hand)]
        find_combinations(current_energy, hand_with_indices, [])
        
        if not valid_sequences: return None
            
        best_seq = None
        best_score = (float('inf'), float('inf')) 
        
        for seq in valid_sequences:
            total_block = sum(CARD_DB.get(c['id'], {"block":0})['block'] for c in seq)
            total_dmg = sum(CARD_DB.get(c['id'], {"damage":0})['damage'] for c in seq)
                
            net_damage_taken = max(0, incoming_damage - (current_block + total_block))
            score = (net_damage_taken, -total_dmg)
            
            if score < best_score:
                best_score = score
                best_seq = seq
        return best_seq

    def get_action(self, parsed_data, parsed_info):
        cmds = parsed_data.get("available_commands", [])
        if "play" not in cmds and "end" not in cmds:
            return None

        combat = parsed_info.get("combat")
        if not combat: return "end\n"

        hand = combat.get("hand", [])
        monsters = combat.get("monsters", [])
        alive_monsters = [m for m in monsters if m['hp'] > 0 and not m.get("is_gone")]
        
        if not alive_monsters:
            return None # 몹 다 죽었으면 ChoiceAI가 넘기길 기다림
            
        incoming_damage = sum(m.get("damage", 0) * m.get("hits", 1) for m in alive_monsters if "ATTACK" in m.get("intent", ""))
        
        best_sequence = self.get_best_action_sequence(hand, combat.get("energy", 0), combat.get("block", 0), incoming_damage)
        
        if best_sequence and "play" in cmds:
            chosen_card = best_sequence[0]
            action_str = f"play {chosen_card['hand_index']}"
            if chosen_card["has_target"]:
                target_idx = 0
                for i, m in enumerate(monsters):
                    if m["hp"] > 0 and not m.get("is_gone"):
                        target_idx = i
                        break
                action_str += f" {target_idx}"
            return f"{action_str}\n"
            
        elif "end" in cmds:
            return "end\n"
            
        return None