import re

def replace_event(content, event_name, replacement):
    pattern = r'event ' + re.escape(event_name) + r'.*?end event'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def replace_function(content, func_name, replacement):
    pattern = r'public function ' + re.escape(func_name) + r'.*?end function'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

# --- CHARACTER ABILITIES & AI ---
# We use RAW properties to ensure the parser never fails.
# propertyValue = character
# value15 = isSidekick, value14 = carrying
# value1, value2 = timers
# value24 = gravityStrength
# value19, value20, value21 = physics

reservations = """
reserve function Player_UpdatePhysicsState
reserve function Player_ProcessUpdate
reserve function Player_Action_DropDash
reserve function Player_Sidekick_UpdateAI
reserve function Player_Action_Glide
reserve function Player_State_Glide
reserve function Player_State_GlideDrop
reserve function Player_State_Climb
reserve function Player_State_LedgePullUp
reserve function Player_State_Carried
"""

logic = """
public function Player_UpdatePhysicsState
	temp0 = 0
	switch object[currentPlayer].propertyValue
	case 0: temp0 = 0; break
	case 1: temp0 = 0; break
	case 2: temp0 = 1; break
	case 3: temp0 = 2; break
	end switch
	temp1 = 0
	if object[currentPlayer].ypos > stage.waterLevel
		temp1 = 8
		object[currentPlayer].value24 = 4096
	else
		object[currentPlayer].value24 = 14336
	end if
	switch temp0
	case 0
		GetTableValue(object[currentPlayer].value19, temp1, Player_SonicPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value20, temp1, Player_SonicPhysicsTable)
		temp1 += 5
		GetTableValue(object[currentPlayer].value26, temp1, Player_SonicPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value27, temp1, Player_SonicPhysicsTable)
		break
	case 1
		GetTableValue(object[currentPlayer].value19, temp1, Player_TailsPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value20, temp1, Player_TailsPhysicsTable)
		temp1 += 5
		GetTableValue(object[currentPlayer].value26, temp1, Player_TailsPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value27, temp1, Player_TailsPhysicsTable)
		break
	case 2
		GetTableValue(object[currentPlayer].value19, temp1, Player_KnucklesPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value20, temp1, Player_KnucklesPhysicsTable)
		temp1 += 5
		GetTableValue(object[currentPlayer].value26, temp1, Player_KnucklesPhysicsTable)
		temp1++
		GetTableValue(object[currentPlayer].value27, temp1, Player_KnucklesPhysicsTable)
		break
	end switch
	object[currentPlayer].value21 = object[currentPlayer].value20
end function

public function Player_Sidekick_UpdateAI
	if object.value14 == true
		object.up = keyDown[0].up
		object.down = keyDown[0].down
		object.left = keyDown[0].left
		object.right = keyDown[0].right
		object.jumpHold = keyDown[0].jumpHold
		object.jumpPress = keyPress[0].jumpPress
		return
	end if
	temp0 = saveRAM[1200]
	temp0 -= 32
	temp0 &= 63
	temp1 = 1000 + temp0
	temp3 = saveRAM[temp1]
	temp1 = 1100 + temp0
	temp4 = saveRAM[temp1]
	object.left = false
	object.right = false
	object.jumpPress = false
	if object.xpos < temp3
		object.right = true
	else
		if object.xpos > temp3
			object.left = true
		end if
	end if
	if object.gravity == 0
		if object.ypos > temp4
			object.jumpPress = true
		end if
	else
		if object.ypos > temp4
			object.jumpHold = true
		else
			object.jumpHold = false
		end if
	end if
end function

public function Player_Action_DropDash
	if object.propertyValue < 2
		if object.animation == 2
			if object.jumpHold == true
				object.value2++
				if object.value2 >= 20
					object.animation = 48
					if object.value2 == 20
						PlaySfx(SfxName[Charge], 0)
					end if
				end if
			else
				object.value2 = 0
			end if
		end if
	end if
end function

public function Player_Action_Glide
	if object.jumpPress == true
		object.state = Player_State_Glide
		object.animation = 44
		object.yvel = 32768
		if object.direction == 0
			object.speed = 262144
		else
			object.speed = -262144
		end if
		object.xvel = object.speed
	end if
end function

public function Player_State_Glide
	object.yvel = 32768
	object.xvel = object.speed
	if object.jumpHold == false
		object.state = Player_State_GlideDrop
		object.animation = 45
	end if
	temp0 = 10
	if object.direction != 0
		temp0 = -10
	end if
	ObjectTileCollision(2, temp0, 0, object.value33)
	if checkResult == true
		object.state = Player_State_Climb
		object.animation = 46
		object.speed = 0
		object.xvel = 0
	end if
	if object.gravity == 0
		object.state = Player_State_Ground
		object.animation = 0
	end if
end function

public function Player_State_GlideDrop
	object.yvel += object.value24
	object.xvel = 0
	if object.gravity == 0
		object.state = Player_State_Ground
		object.animation = 0
	end if
end function

public function Player_State_Climb
	object.xvel = 0
	object.yvel = 0
	if object.up == true
		object.ypos -= 65536
	else
		if object.down == true
			object.ypos += 65536
		end if
	end if
	temp0 = 10
	if object.direction != 0
		temp0 = -10
	end if
	ObjectTileCollision(2, temp0, -16, object.value33)
	if checkResult == false
		object.state = Player_State_LedgePullUp
		object.animation = 47
		object.value1 = 0
	end if
	if object.jumpPress == true
		object.state = Player_State_Air
		object.yvel = -262144
	end if
end function

public function Player_State_LedgePullUp
	object.value1++
	if object.value1 > 20
		object.state = Player_State_Ground
		object.ypos -= 1572864
		if object.direction == 0
			object.xpos += 1048576
		else
			object.xpos -= 1048576
		end if
	end if
end function

public function Player_State_Carried
	object.xpos = object[0].xpos
	object.ypos = object[0].ypos
	object.ypos += 1048576
	object.direction = object[0].direction
	if object.jumpPress == true
		object.state = Player_State_Air
		object.yvel = -262144
		object[0].value14 = false
	end if
	if object[0].state != Player_State_Fly
		object.state = Player_State_Air
		object[0].value14 = false
	end if
end function

public function Player_ProcessUpdate
	if object.value15 == true
		CallFunction(Player_Sidekick_UpdateAI)
	else
		ProcessObjectControl()
		if playerCount > 1
			if object.state == Player_State_Air
				if object[1].state == Player_State_Fly
					if object[1].value14 == false
						temp0 = object.xpos
						temp0 -= object[1].xpos
						Abs(temp0)
						if temp0 < 1048576
							temp0 = object.ypos
							temp0 -= object[1].ypos
							Abs(temp0)
							if temp0 < 1572864
								object.state = Player_State_Carried
								object[1].value14 = true
							end if
						end if
					end if
				end if
			end if
		end if
		if object.entityPos == 0
			temp0 = saveRAM[1200]
			temp1 = 1000 + temp0
			saveRAM[temp1] = object.xpos
			temp1 = 1100 + temp0
			saveRAM[temp1] = object.ypos
			temp0++
			temp0 &= 63
			saveRAM[1200] = temp0
		end if
	end if
end function
"""

physics_tables = """
private table Player_SonicPhysicsTable
	0x60000, 0x0C00, 0x1800, 0x0600, 0x08000, 0x0600, -0x68000, -0x40000
	0x30000, 0x0600, 0x0C00, 0x0300, 0x04000, 0x0300, -0x38000, -0x20000
end table
private table Player_TailsPhysicsTable
	0x60000, 0x0C00, 0x1800, 0x0600, 0x08000, 0x0600, -0x68000, -0x40000
	0x30000, 0x0600, 0x0C00, 0x0300, 0x04000, 0x0300, -0x38000, -0x20000
end table
private table Player_KnucklesPhysicsTable
	0x60000, 0x0C00, 0x1800, 0x0600, 0x08000, 0x0600, -0x60000, -0x40000
	0x30000, 0x0600, 0x0C00, 0x0300, 0x04000, 0x0300, -0x30000, -0x20000
end table
"""

# --- 1. PLAYER OBJECT ---
with open('Scripts/Players/PlayerObject.txt', 'r') as f:
    p_code = f.read()

# Update Header
p_code = p_code.replace('public alias 0 : PLAYER_SONIC\npublic alias 1 : PLAYER_TAILS\npublic alias 2 : PLAYER_KNUCKLES\npublic alias 3 : PLAYER_SONIC_TAILS',
                        'public alias 0 : PLAYER_SONIC_TAILS\npublic alias 1 : PLAYER_SONIC\npublic alias 2 : PLAYER_TAILS\npublic alias 3 : PLAYER_KNUCKLES')
p_code = p_code.replace('// Variables', '// Animation Aliases\npublic alias 44 : ANI_GLIDING\npublic alias 45 : ANI_GLIDE_DROP\npublic alias 46 : ANI_CLIMBING\npublic alias 47 : ANI_LEDGE_PULLUP\npublic alias 48 : ANI_DROPDASH\n\n// Variables')
p_code = p_code.replace('reserve function Player_ProcessUpdate // Function0', reservations)
p_code = p_code.replace('public value Mini_PlayerFlag = 0;', physics_tables + '\npublic value Mini_PlayerFlag = 0;')

# Update Startup
new_startup = """event ObjectStartup
	playerCount = 0
	foreach (TypeName[Player Object], arrayPos0, ALL_ENTITIES)
		if playerCount == 0
			screen[0].cameraEnabled = true
			screen[0].cameraStyle = options.originalControls
			screen[0].cameraTarget = 0
			currentPlayer = 0
			ResetObjectEntity(0, TypeName[Player Object], 0, object[arrayPos0].xpos, object[arrayPos0].ypos)
			screen[0].cameraX = object[0].ixpos
			screen[0].cameraY = object[0].iypos
			object[0].groupID = 256
			object[0].state = Player_State_Air
			object[0].priority = 1
			object[0].drawOrder = 4
			switch stage.playerListPos
			case 0 // Duo
				LoadSpriteSheet("Players/Sonic1.gif")
				LoadAnimation("Sonic.ani")
				object[0].propertyValue = 0
				object[0].value30 = Player_Action_DblJumpSonic
				playerCount = 2
				ResetObjectEntity(1, TypeName[Player 2 Object], 0, object[0].xpos, object[0].ypos)
				object[1].xpos -= 1048576
				object[1].groupID = 256
				object[1].propertyValue = 2
				object[1].value15 = true
				object[1].value30 = Player_Action_DblJumpTails
				saveRAM[1200] = 0
				break
			case 1 // Sonic
				LoadSpriteSheet("Players/Sonic1.gif")
				LoadAnimation("Sonic.ani")
				object[0].propertyValue = 1
				object[0].value30 = Player_Action_DblJumpSonic
				playerCount = 1
				break
			case 2 // Tails
				object[0].propertyValue = 2
				LoadSpriteSheet("Players/Tails1.gif")
				LoadAnimation("Tails.ani")
				object[0].value30 = Player_Action_DblJumpTails
				playerCount = 1
				break
			case 3 // Knuckles
				object[0].propertyValue = 3
				LoadSpriteSheet("Players/Knuckles1.gif")
				LoadAnimation("Knuckles.ani")
				object[0].value30 = Player_Action_Glide
				playerCount = 1
				GetAnimationByName(44, "Gliding")
				GetAnimationByName(45, "Glide Drop")
				GetAnimationByName(46, "Climbing")
				GetAnimationByName(47, "Ledge Pull Up")
				break
			end switch
			CallFunction(Player_UpdatePhysicsState)
			if playerCount > 1
				currentPlayer = 1
				CallFunction(Player_UpdatePhysicsState)
				currentPlayer = 0
			end if
		end if
		ResetObjectEntity(arrayPos0, TypeName[Blank Object], 0, 0, 0)
	next
	GetAnimationByName(48, "Drop Dash")
end event"""
p_code = replace_event(p_code, 'ObjectStartup', new_startup)

# Update Triggers
p_code = re.sub(r'if player\.animation == 2.*?if player\.jumpAbilityState == 1.*?CallFunction\(player\.jumpAbility\).*?end if.*?end if',
                """if object.animation == 2
			if object.value34 == 1
				if object.yvel >= object.value27
					CallFunction(object.value30)
				end if
			end if
			CallFunction(Player_Action_DropDash)
		end if""", p_code, flags=re.DOTALL)

# Re-build file
rsdk_load_pos = p_code.find('event RSDKLoad')
end_rsdk = p_code.find('end event', rsdk_load_pos) + 9
p_final = p_code[:end_rsdk] + "\n\n" + logic

with open('Scripts/Players/PlayerObject.txt', 'w') as f:
    f.write(p_final)

# --- 2. TAILS & PLAYER 2 ---
shared_aliases = """//-------Aliases-------//
public alias arrayPos6 : currentPlayer
public alias arrayPos7 : playerCount
public alias 44 : ANI_GLIDING
public alias 45 : ANI_GLIDE_DROP
public alias 46 : ANI_CLIMBING
public alias 47 : ANI_LEDGE_PULLUP
public alias 48 : ANI_DROPDASH
"""
shared_script = shared_aliases + physics_tables + reservations + """
event ObjectUpdate
    CallFunction(Player_ProcessUpdate)
    CallFunction(object.state)
    ProcessAnimation()
end event
event ObjectDraw
    DrawObjectAnimation()
end event
event ObjectStartup
    LoadSpriteSheet("Players/Tails1.gif")
    LoadAnimation("Tails.ani")
end event
""" + logic

with open('Scripts/Players/Player2Object.txt', 'w') as f: f.write(shared_script)
with open('Scripts/Players/TailsObject.txt', 'w') as f: f.write(shared_script)

# --- 3. HUD.txt ---
with open('Scripts/Global/HUD.txt', 'r') as f:
    h_code = f.read()

h_draw = """	switch object[0].propertyValue
	case 1
		DrawSpriteScreenXY(17, 16, 212)
		break
	case 2
		DrawSpriteScreenXY(18, 16, 212)
		break
	case 3
		DrawSpriteScreenXY(19, 16, 212)
		break
	case 0
		DrawSpriteScreenXY(17, 16, 212)
		break
	end switch"""
# Use regex to find ANY character icon drawing logic and replace it
h_code = re.sub(r'switch (object|player)\[0\].(propertyValue|character).*?end switch', h_draw, h_code, flags=re.DOTALL)
h_code = h_code.replace('temp0 = object.propertyValue\n\ttemp0 += 17\n\tDrawSpriteScreenXY(temp0, 16, 212)', h_draw)

# Reset global stats to original syntax
h_code = h_code.replace('object.lives', 'player.lives').replace('object.score', 'player.score').replace('warp.value1', 'warp.timer')

with open('Scripts/Global/HUD.txt', 'w') as f:
    f.write(h_code)

print("SUCCESS.")
