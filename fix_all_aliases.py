import os

new_aliases = """private alias object.value0  : player.rings
private alias object.value1  : player.timer
private alias object.value2  : player.abilityTimer
private alias object.value34 : player.jumpAbilityState
private alias object.collisionPlane : player.collisionPlane
"""

def patch_script(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Pre-clean
    content = content.replace('private alias object.value0  : player.rings\n', '')
    content = content.replace('private alias object.value1  : player.timer\n', '')
    content = content.replace('private alias object.value2  : player.abilityTimer\n', '')
    content = content.replace('private alias object.value34 : player.jumpAbilityState\n', '')
    content = content.replace('private alias object.collisionPlane : player.collisionPlane\n', '')

    # Insert new aliases
    if 'private alias object.value29 : player.jumpOffset' in content:
        content = content.replace('private alias object.value29 : player.jumpOffset', 'private alias object.value29 : player.jumpOffset\n' + new_aliases)

    with open(filepath, 'w') as f:
        f.write(content)

patch_script('Scripts/Players/TailsObject.txt')
patch_script('Scripts/Players/Player2Object.txt')

print("Aliases updated.")
