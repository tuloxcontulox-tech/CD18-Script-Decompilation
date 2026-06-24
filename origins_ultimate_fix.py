import re
import os

# --- UTILS ---
def replace_event(content, event_name, replacement):
    pattern = r'event ' + re.escape(event_name) + r'.*?end event'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def replace_function(content, func_name, replacement):
    pattern = r'public function ' + re.escape(func_name) + r'.*?end function'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

# --- CORE DATA ---

physics_tables = """
// Physics Tables
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

update_physics_code = """public function Player_UpdatePhysicsState
	temp0 = 0
	switch player[currentPlayer].character
	case 0
		temp0 = 0
		break
	case 1
		temp0 = 0
		break
	case 2
		temp0 = 1
		break
	case 3
		temp0 = 2
		break
	end switch
	temp1 = 0
	if player[currentPlayer].ypos > stage.waterLevel
		temp1 = 8
		player[currentPlayer].gravityStrength = 4096
	else
		player[currentPlayer].gravityStrength = 14336
	end if
	switch temp0
	case 0
		GetTableValue(player[currentPlayer].topSpeed, temp1, Player_SonicPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].acceleration, temp1, Player_SonicPhysicsTable)
		temp1 += 5
		GetTableValue(player[currentPlayer].jumpStrength, temp1, Player_SonicPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].jumpCap, temp1, Player_SonicPhysicsTable)
		break
	case 1
		GetTableValue(player[currentPlayer].topSpeed, temp1, Player_TailsPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].acceleration, temp1, Player_TailsPhysicsTable)
		temp1 += 5
		GetTableValue(player[currentPlayer].jumpStrength, temp1, Player_TailsPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].jumpCap, temp1, Player_TailsPhysicsTable)
		break
	case 2
		GetTableValue(player[currentPlayer].topSpeed, temp1, Player_KnucklesPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].acceleration, temp1, Player_KnucklesPhysicsTable)
		temp1 += 5
		GetTableValue(player[currentPlayer].jumpStrength, temp1, Player_KnucklesPhysicsTable)
		temp1++
		GetTableValue(player[currentPlayer].jumpCap, temp1, Player_KnucklesPhysicsTable)
		break
	end switch
	player[currentPlayer].deceleration = player[currentPlayer].acceleration
end function"""

process_update_code = """public function Player_ProcessUpdate
	if player.isSidekick == true
		CallFunction(Player_Sidekick_UpdateAI)
	else
		ProcessObjectControl()
		if playerCount > 1
			if player.state == Player_State_Air
				if object[1].state == Player_State_Fly
					if object[1].value14 == false
						temp0 = player.xpos
						temp0 -= object[1].xpos
						Abs(temp0)
						if temp0 < 1048576
							temp0 = player.ypos
							temp0 -= object[1].ypos
							Abs(temp0)
							if temp0 < 1572864
								player.state = Player_State_Carried
								object[1].value14 = true
							end if
						end if
					end if
				end if
			end if
		end if
		if player.entityPos == 0
			temp0 = saveRAM[1200]
			temp1 = 1000
			temp1 += temp0
			saveRAM[temp1] = player.xpos
			temp1 = 1100
			temp1 += temp0
			saveRAM[temp1] = player.ypos
			temp0++
			temp0 &= 63
			saveRAM[1200] = temp0
		end if
	end if
end function"""

extra_logic_code = """
public function Player_Action_DropDash
	if player.character < 2
		if player.animation == 2
			if player.jumpHold == true
				player.abilityTimer++
				if player.abilityTimer >= 20
					player.animation = ANI_DROPDASH
					if player.abilityTimer == 20
						PlaySfx(SfxName[Charge], 0)
					end if
				end if
			else
				player.abilityTimer = 0
			end if
		end if
	end if
end function

public function Player_Sidekick_UpdateAI
	if player.carrying == true
		player.up = object[0].up
		player.down = object[0].down
		player.left = object[0].left
		player.right = object[0].right
		player.jumpHold = object[0].jumpHold
		player.jumpPress = object[0].jumpPress
		return
	end if
	temp0 = saveRAM[1200]
	temp0 -= 32
	temp0 &= 63
	temp1 = saveRAM[1000 + temp0]
	temp2 = saveRAM[1100 + temp0]
	player.left = false
	player.right = false
	player.jumpPress = false
	if player.xpos < temp1
		player.right = true
	else
		if player.xpos > temp1
			player.left = true
		end if
	end if
	if player.gravity == 0
		if player.ypos > temp2
			player.jumpPress = true
		end if
	else
		if player.ypos > temp2
			player.jumpHold = true
		else
			player.jumpHold = false
		end if
	end if
end function

public function Player_Action_Glide
	if player.jumpPress == true
		player.state = Player_State_Glide
		player.animation = ANI_GLIDING
		player.yvel = 32768
		if player.direction == 0
			player.speed = 262144
		else
			player.speed = -262144
		end if
		player.xvel = player.speed
	end if
end function

public function Player_State_Glide
	player.yvel = 32768
	player.xvel = player.speed
	if player.jumpHold == false
		player.state = Player_State_GlideDrop
		player.animation = ANI_GLIDE_DROP
	end if
	if player.direction == 0
		temp0 = 10
	else
		temp0 = -10
	end if
	ObjectTileCollision(2, temp0, 0, player.collisionPlane)
	if checkResult == true
		player.state = Player_State_Climb
		player.animation = ANI_CLIMBING
		player.speed = 0
		player.xvel = 0
	end if
	if player.gravity == 0
		player.state = Player_State_Ground
		player.animation = 0
	end if
end function

public function Player_State_GlideDrop
	player.yvel += player.gravityStrength
	player.xvel = 0
	if player.gravity == 0
		player.state = Player_State_Ground
		player.animation = 0
	end if
end function

public function Player_State_Climb
	player.xvel = 0
	player.yvel = 0
	if player.up == true
		player.ypos -= 65536
	else
		if player.down == true
			player.ypos += 65536
		end if
	end if
	if player.direction == 0
		temp0 = 10
	else
		temp0 = -10
	end if
	ObjectTileCollision(2, temp0, -16, player.collisionPlane)
	if checkResult == false
		player.state = Player_State_LedgePullUp
		player.animation = ANI_LEDGE_PULLUP
		player.timer = 0
	end if
	if player.jumpPress == true
		player.state = Player_State_Air
		player.yvel = -262144
	end if
end function

public function Player_State_LedgePullUp
	player.timer++
	if player.timer > 20
		player.state = Player_State_Ground
		player.ypos -= 1572864
		if player.direction == 0
			player.xpos += 1048576
		else
			player.xpos -= 1048576
		end if
	end if
end function

public function Player_State_Carried
	player.xpos = object[1].xpos
	player.ypos = object[1].ypos
	player.ypos += 1048576
	player.direction = object[1].direction
	if player.jumpPress == true
		player.state = Player_State_Air
		player.yvel = -262144
		object[1].value14 = false
	end if
	if object[1].state != Player_State_Fly
		player.state = Player_State_Air
		object[1].value14 = false
	end if
end function
"""

# --- PLAYER OBJECT PATCH ---

with open('Scripts/Players/PlayerObject.txt', 'r') as f:
    p_code = f.read().replace('\r\n', '\n')

# Pre-clean duplicates from previous attempts
rsdk_load_pos = p_code.find('event RSDKLoad')
if rsdk_load_pos != -1:
    end_event_pos = p_code.find('end event', rsdk_load_pos)
    if end_event_pos != -1:
        p_code = p_code[:end_event_pos + 9]

# Inject Tables & Constants
p_code = p_code.replace('public value Mini_PlayerFlag = 0;', physics_tables + '\npublic value Mini_PlayerFlag = 0;')

p_code = replace_function(p_code, 'Player_UpdatePhysicsState', update_physics_code)
p_code = replace_function(p_code, 'Player_ProcessUpdate', process_update_code)

# Inject Startup
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
			object[0].groupID = GROUP_PLAYERS
			player[0].state = Player_State_Air
			player[0].priority = 1
			player[0].drawOrder = 4
			switch stage.playerListPos
			case 0 // Duo
				LoadSpriteSheet("Players/Sonic1.gif")
				LoadAnimation("Sonic.ani")
				player[0].character = 0
				player[0].jumpAbility = Player_Action_DblJumpSonic
				playerCount = 2
				ResetObjectEntity(1, TypeName[Player 2 Object], 0, object[0].xpos, object[0].ypos)
				object[1].xpos -= 1048576
				object[1].groupID = GROUP_PLAYERS
				player[1].character = 2
				player[1].isSidekick = true
				player[1].jumpAbility = Player_Action_DblJumpTails
				saveRAM[1200] = 0
				break
			case 1 // Sonic
				LoadSpriteSheet("Players/Sonic1.gif")
				LoadAnimation("Sonic.ani")
				player[0].character = 1
				player[0].jumpAbility = Player_Action_DblJumpSonic
				playerCount = 1
				break
			case 2 // Tails
				player[0].character = 2
				LoadSpriteSheet("Players/Tails1.gif")
				LoadAnimation("Tails.ani")
				player[0].jumpAbility = Player_Action_DblJumpTails
				playerCount = 1
				break
			case 3 // Knuckles
				player[0].character = 3
				LoadSpriteSheet("Players/Knuckles1.gif")
				LoadAnimation("Knuckles.ani")
				player[0].jumpAbility = Player_Action_Glide
				playerCount = 1
				GetAnimationByName(ANI_GLIDING, "Gliding")
				GetAnimationByName(ANI_GLIDE_DROP, "Glide Drop")
				GetAnimationByName(ANI_CLIMBING, "Climbing")
				GetAnimationByName(ANI_LEDGE_PULLUP, "Ledge Pull Up")
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
	GetAnimationByName(ANI_DROPDASH, "Drop Dash")
end event"""
p_code = replace_event(p_code, 'ObjectStartup', new_startup)

# Inject Triggers (carefully)
p_code = re.sub(r'if player\.animation == 2.*?if player\.jumpAbilityState == 1.*?CallFunction\(player\.jumpAbility\).*?end if.*?end if',
                """if player.animation == 2
			if player.jumpAbilityState == 1
				if player.yvel >= player.jumpCap
					CallFunction(player.jumpAbility)
				end if
			end if
			CallFunction(Player_Action_DropDash)
		end if""", p_code, flags=re.DOTALL)

landing_logic = """if player.collisionDisabled == false
				temp0 = player.prevGravity
				player.prevGravity = player.gravity
				ProcessObjectMovement()
				player.prevGravity ^= 1
				CheckEqual(player.gravity, 0)
				player.prevGravity |= checkResult
				player.prevGravity ^= 1
				if temp0 == 1
					if player.prevGravity == 0
						if player.animation == ANI_DROPDASH
							player.state = Player_State_Roll
							player.animation = 2
							PlaySfx(SfxName[Release], 0)
							if player.direction == 0
								player.speed = 786432
							else
								player.speed = -786432
							end if
							player.xvel = player.speed
						else
							if player.animation == 2
								if player.down == false
									player.animation = 1
									player.iypos += player.jumpOffset
								end if
							end if
						end if
					end if
				end if
			else
				player.collisionDisabled = false
			end if"""
p_code = re.sub(r'if player\.collisionDisabled == false.*?else.*?player\.collisionDisabled = false.*?end if', landing_logic, p_code, flags=re.DOTALL)

p_code += "\n\n" + extra_logic_code
with open('Scripts/Players/PlayerObject.txt', 'w') as f:
    f.write(p_code)

# --- SHARED SCRIPTS ---

shared_aliases = """//-------Aliases-------//
private alias object.type : player.type
private alias object.entityPos : player.entityPos
private alias object.state : player.state
private alias object.xpos : player.xpos
private alias object.ypos : player.ypos
private alias object.xvel : player.xvel
private alias object.yvel : player.yvel
private alias object.speed : player.speed
private alias object.direction : player.direction
private alias object.gravity : player.gravity
private alias object.animation : player.animation
private alias object.prevAnimation : player.prevAnimation
private alias object.animationSpeed : player.animationSpeed
private alias object.animationTimer : player.animationTimer
private alias object.drawOrder : player.drawOrder
private alias object.collisionDisabled : player.collisionDisabled
private alias object.propertyValue : player.character
private alias object.value14 : player.carrying
private alias object.value15 : player.isSidekick
private alias object.jumpHold : player.jumpHold
private alias object.jumpPress : player.jumpPress
private alias object.up : player.up
private alias object.down : player.down
private alias object.left : player.left
private alias object.right : player.right
private alias object.value19 : player.topSpeed
private alias object.value20 : player.acceleration
private alias object.value21 : player.deceleration
private alias object.value22 : player.airAcceleration
private alias object.value23 : player.airDeceleration
private alias object.value24 : player.gravityStrength
private alias object.value26 : player.jumpStrength
private alias object.value27 : player.jumpCap
private alias object.value28 : player.rollingFriction
private alias object.value29 : player.jumpOffset

public alias arrayPos6 : currentPlayer
public alias arrayPos7 : playerCount

public alias 44 : ANI_GLIDING
public alias 45 : ANI_GLIDE_DROP
public alias 46 : ANI_CLIMBING
public alias 47 : ANI_LEDGE_PULLUP
public alias 48 : ANI_DROPDASH
"""

def build_ent(sheet, anim):
    return shared_aliases + physics_tables + """
event ObjectUpdate
    CallFunction(Player_ProcessUpdate)
    CallFunction(player.state)
    ProcessAnimation()
end event
event ObjectDraw
    DrawObjectAnimation()
end event
event ObjectStartup
    LoadSpriteSheet(\"Players/""" + sheet + """\")
    LoadAnimation(\"""" + anim + """\")
end event
""" + update_physics_code + "\n" + process_update_code + "\n" + extra_logic_code

with open('Scripts/Players/Player2Object.txt', 'w') as f: f.write(build_ent("Tails1.gif", "Tails.ani"))
with open('Scripts/Players/TailsObject.txt', 'w') as f: f.write(build_ent("Tails1.gif", "Tails.ani"))

# --- HUD FIX ---
with open('Scripts/Global/HUD.txt', 'r') as f: h_code = f.read().replace('\r\n', '\n')
h_startup = """event ObjectStartup
	LoadSpriteSheet("Global/Display.gif")
	SpriteFrame(0, 0, 8, 11, 1, 50)  // 0-9
	SpriteFrame(0, 0, 8, 11, 10, 50)
	SpriteFrame(0, 0, 8, 11, 19, 50)
	SpriteFrame(0, 0, 8, 11, 28, 50)
	SpriteFrame(0, 0, 8, 11, 1, 62)
	SpriteFrame(0, 0, 8, 11, 10, 62)
	SpriteFrame(0, 0, 8, 11, 19, 62)
	SpriteFrame(0, 0, 8, 11, 28, 62)
	SpriteFrame(0, 0, 8, 11, 1, 74)
	SpriteFrame(0, 0, 8, 11, 10, 74)
	SpriteFrame(0, 0, 39, 43, 1, 1)   // 10
	SpriteFrame(0, 0, 31, 11, 1, 119) // 11
	SpriteFrame(0, 0, 39, 11, 1, 131) // 12
	SpriteFrame(0, 0, 29, 4, 1, 45)   // 13
	SpriteFrame(0, 0, 8, 8, 1, 98)    // 14
	SpriteFrame(0, 0, 32, 16, 90, 67) // 15
	SpriteFrame(0, 0, 32, 16, 123, 67)// 16
	SpriteFrame(0, 0, 16, 16, 1, 143) // 17 - Sonic

	LoadSpriteSheet("Global/Display_t.gif")
	SpriteFrame(0, 0, 16, 16, 1, 143) // 18 - Tails

	LoadSpriteSheet("Global/Display_k.gif")
	SpriteFrame(0, 0, 16, 16, 1, 143) // 19 - Knuckles
end event"""
h_code = replace_event(h_code, 'ObjectStartup', h_startup)
h_draw_logic = """	switch player[0].character
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
h_code = h_code.replace('temp0 = object.propertyValue\n\ttemp0 += 17\n\tDrawSpriteScreenXY(temp0, 16, 212)', h_draw_logic)
with open('Scripts/Global/HUD.txt', 'w') as f: f.write(h_code)

print("Engine Rebuild Complete.")
