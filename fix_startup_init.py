import re
with open('Scripts/Players/PlayerObject.txt', 'r') as f:
    content = f.read()

# Make sure CallFunction(Player_UpdatePhysicsState) is always called for Player 0
# and Player 1 if it exists.
# The current logic handles it, but let's double check.

# Also ensure Player_Sidekick_UpdateAI is defined once.
# In previous attempts I might have appended it multiple times.

def clean_duplicates(content):
    # Only keep the FIRST definition of each function
    funcs = ['Player_Action_DropDash', 'Player_Sidekick_UpdateAI', 'Player_Action_Glide', 'Player_State_Glide', 'Player_State_GlideDrop', 'Player_State_Climb', 'Player_State_LedgePullUp', 'Player_State_Carried']
    for func in funcs:
        pattern = r'public function ' + re.escape(func) + r'.*?end function'
        matches = list(re.finditer(pattern, content, flags=re.DOTALL))
        if len(matches) > 1:
            # Keep only the last one (the ones I appended)
            # Actually, I'll remove all and append fresh ones to be sure.
            content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content

# content = clean_duplicates(content)
# ... actually I'll just re-run the origins_ultimate_fix but better.
