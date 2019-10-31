SMKScreen = {}

ConfigParams = {
	"ScreenWidth",
	"ScreenHeight",
	"ExtraInputs",
	"NumButtons",
	"Skew",
	"TiltShift",
	"InputResolution",
}
cfg = {}

cfg.ScreenWidth = 15
cfg.ScreenHeight = 15
ScreenSize = nil
HalfWidth = nil
cfg.Skew = 1.05
cfg.TiltShift = 0.3
cfg.InputResolution = 24
TileSize = 32
FirstMap = 0x00
LastMap = 0x13
NumMaps = LastMap - FirstMap + 1
ExtraInputNames = {
	"Speed",
	"Backwards",
	"Item Box",
}
cfg.ExtraInputs = NumMaps + #ExtraInputNames

map = nil
kartX = nil
kartY = nil
direction = nil
map = nil
currentCourse = -1

function configUpdated()
	HalfWidth = math.floor(cfg.ScreenWidth/2)
	ScreenSize = cfg.ScreenWidth*cfg.ScreenHeight
end

configUpdated()


function getPositions(player)
	if player == 1 then
		kartX = mainmemory.read_s16_le(0x88)
		kartY = mainmemory.read_s16_le(0x8C)
			
		direction = mainmemory.readbyte(0x95)
		kartSpeed = mainmemory.read_s16_le(0x10EA)
	else
		kartX = mainmemory.read_s16_le(0x8A)
		kartY = mainmemory.read_s16_le(0x8E)
			
		direction = mainmemory.readbyte(0x112B)
		kartSpeed = mainmemory.read_s16_le(0x11EA)
	end
end

function SMKScreen.getPosition()
	return {kartX, kartY, direction}
end

function getLap()
	return mainmemory.readbyte(0x10C1)-128
end

function getSurface()
	if mainmemory.readbyte(0x10AE) == 64 then
		return 1
	end
	if mainmemory.readbyte(0x10AE) == 84 then
		return 0
	end
	if mainmemory.readbyte(0x10AE) == 128 then
		return -1
	end
end

function getPhysics(physics)
	if physics == 0x54 then --dirt
		return 0
	elseif physics == 0x5A then --lily pads/grass
		return 0
	elseif physics == 0x5C then --shallow water
		return 0
	elseif physics == 0x58 then --snow
		return 0
	elseif physics == 0x56 then --chocodirt
		return -0.5
	elseif physics == 0x40 then --road
		return 1
	elseif physics == 0x46 then --dirt road
		return 0.75
	elseif physics == 0x52 then --loose dirt
		return 0.5
	elseif physics == 0x42 then --ghost road
		return 1
	elseif physics == 0x10 then --jump pad
		return 1.5
	elseif physics == 0x4E then --light ghost road
		return 1
	elseif physics == 0x50 then --wood bridge
		return 1
	elseif physics == 0x1E then --starting line
		return 1
	elseif physics == 0x44 then --castle road
		return 1
	elseif physics == 0x16 then --speed boost
		return 2
	elseif physics == 0x80 then --wall
		return -1.5
	elseif physics == 0x26 then	--oob grass
		return -1.5
	elseif physics == 0x22 then --deep water
		return -1
	elseif physics == 0x20 then --pit
		return -2
	elseif physics == 0x82 then --ghost house border
		return -1.5
	elseif physics == 0x24 then --lava
		return -2
	elseif physics == 0x4C then --choco road
		return 1
	elseif physics == 0x12 then --choco bump
		return 0.75
	elseif physics == 0x1C then --choco bump
		return 0.75
	elseif physics == 0x5E then --mud
		return 0.5
	elseif physics == 0x48 then --wet sand
		return 0.75
	elseif physics == 0x4A then --sand road
		return 1
	elseif physics == 0x84 then --ice blocks
		return -1.5
	elseif physics == 0x28 then --unsure
		return -1
	elseif physics == 0x14 then --? box
		return 1.5
	elseif physics == 0x1A then --coin
		return 1.25
	elseif physics == 0x18 then --oil spill
		return -0.75
	else
		print("Error reading physics type " .. bizstring.hex(physics) .. " for tile " .. bizstring.hex(tile) .. " at x=" .. x .. ", y=" .. y)
		return 0
	end
end

function getItemBox()
	return mainmemory.readbyte(0xD70)
end

function isTurnedAround()
	if bit.band(mainmemory.readbyte(0x10B), 0x10) ~= 0 then
		return 1
	else
		return 0
	end
end
	
function readMap()
	map = {}

	for x=1,128 do
		map[x] = {}
		for y=1,128 do
			local tile = mainmemory.readbyte(0x10000+((x-1)+(y-1)*128)*1)

			map[x][y] = getPhysics(memory.readbyte(0xB00+tile))
		end
	end
end

function SMKScreen.displayMap()
	for x=1,128 do
		for y=1,128 do
			local tile = mainmemory.readbyte(0x10000+((x-1)+(y-1)*128)*1)
			local c = getPhysics(memory.readbyte(0xB00+tile))
			local color
			
			if c == 3 then
				color = 0xFFFF0000
			elseif c == 4 then
				color = 0xFF00FF00
			elseif c == 5 then
				color = 0xFF0000FF
			else
				local g = math.floor((c+2)/4*255)
				
				color = g + g*0x100 + g*0x10000 + 0xFF*0x1000000
			end
			gui.drawPixel(x+5, y+5, color)
		end
	end
	
	for k=1,8 do
		local base = 0xF00+0x100*k
		local x = math.floor(mainmemory.read_s16_le(base+0x18) / 8)
		local y = math.floor(mainmemory.read_s16_le(base+0x1C) / 8)
		gui.drawBox(x+3, y+3, x+7, y+7)
	end
end

function getCourse()
	return mainmemory.readbyte(0x124)
end

function getGameMode()
	return mainmemory.readbyte(0xB5)
end

function getTile(parallelDist, orthDist, facingVec)
	if map == nil then
		readMap()
	end

	local dir = facingVec
	local orth = {-dir[2], dir[1]}
	
	if cfg.TiltShift ~= 0 then
		parallelDist = parallelDist * parallelDist * cfg.TiltShift
	end
	
	orthDist = orthDist * (parallelDist * (cfg.Skew - 1) + 1)
	
	local dx = parallelDist*dir[1]+orthDist*orth[1]
	local dy = parallelDist*dir[2]+orthDist*orth[2]
	
	local worldX = math.floor((kartX+TileSize/2+dx*cfg.InputResolution)/TileSize)+1
	local worldY = math.floor((kartY+TileSize/2+dy*cfg.InputResolution)/TileSize)-1

	if worldX >= 1 and worldX <= 128 and worldY >= 1 and worldY <= 128 then
		return map[worldX][worldY]
	else
		return -1
	end
end
	
function SMKScreen.getScreen(player)
	if map == nil or getGameMode() == 0x1C and getCourse() ~= currentCourse then
		currentCourse = getCourse()
		readMap()
	end
	
	getPositions(player)
	
	local angel = direction * 1.40625
	local dir = {math.sin(math.rad(angel)), -math.cos(math.rad(angel))}
	local orth = {-dir[2], dir[1]}
	
	local inputs = {}

	-- Add base tiles
	for tileRow = cfg.ScreenHeight, 1, -1 do
		for tileCol = -HalfWidth, HalfWidth do
			inputs[#inputs+1] = getTile(tileRow, tileCol, dir)
		end
	end

	-- Add enemy karts
	for k=1,8 do
		if k ~= player then
			local base = 0xF00+0x100*k
			local kX = math.floor(mainmemory.read_s16_le(base+0x18) * 4)
			local kY = math.floor(mainmemory.read_s16_le(base+0x1C) * 4)
			local dx = kX - kartX
			local dy = kY - kartY
			local row = math.floor((dx*dir[1] + dy*dir[2]) / cfg.InputResolution)
			local col = math.floor((dx*orth[1] + dy*orth[2]) / cfg.InputResolution)
			
			col = col / (row * (cfg.Skew - 1) + 1)
			if cfg.TiltShift ~= 0 then
				row = math.sqrt(row / cfg.TiltShift)
			end
			
			col = math.floor(col + HalfWidth + 1)
			row = math.floor(cfg.ScreenHeight - row + 1)
			
			if row >= 1 and row <= cfg.ScreenHeight and col >= 1 and col <= cfg.ScreenWidth then
				inputs[(row - 1)*cfg.ScreenWidth+col] = -0.5
			end
		end
	end
	
	-- Add items
	for i=1,6 do
		local base = 0x1a00 + 0x80*(i-1)
		local alive = mainmemory.readbyte(base + 0x13)
		if alive ~= 0 then
			local itemX = math.floor(mainmemory.read_s16_le(base + 0x18) * 4)
			local itemY = math.floor(mainmemory.read_s16_le(base + 0x1C) * 4)
			local dx = itemX - kartX
			local dy = itemY - kartY
			local row = math.floor((dx*dir[1] + dy*dir[2]) / cfg.InputResolution)
			local col = math.floor((dx*orth[1] + dy*orth[2]) / cfg.InputResolution)
			
			col = col / (row * (cfg.Skew - 1) + 1)
			if cfg.TiltShift ~= 0 then
				row = math.sqrt(row / cfg.TiltShift)
			end
			
			col = math.floor(col + HalfWidth + 1)
			row = math.floor(cfg.ScreenHeight - row + 1)
			
			if row >= 1 and row <= cfg.ScreenHeight and col >= 1 and col <= cfg.ScreenWidth then
				inputs[(row - 1)*cfg.ScreenWidth+col] = -1.0
			end
		end
	end
	
	-- Add current map inputs
	for i=FirstMap,LastMap do
		if currentCourse == i then
			inputs[#inputs+1] = 1
		else
			inputs[#inputs+1] = 0
		end
	end

	-- Add miscellaneous inputs
	inputs[#inputs+1] = kartSpeed / (1024.0)
	inputs[#inputs+1] = isTurnedAround()
	inputs[#inputs+1] = getItemBox() / 16.0
	
	return inputs
end

local DrawScreen = require("DrawScreen")
function SMKScreen.displayScreen(screen)
	DrawScreen.drawScreen(screen, cfg.ScreenWidth, cfg.ScreenHeight, 5, 120)
	
	local black = 0xFFFFFFFF
	for i=FirstMap,LastMap do
		local v = screen[ScreenSize + 1 + i]
		local x = 80 + 7*i
		local y = 120
		DrawScreen.drawGrayCell(x, y, v, 0, 1)
	end
	gui.drawText(100, 127, "Current Course", black, 0)
	
	for i=1,3 do
		local v = screen[ScreenSize + NumMaps + i]
		local x = 5
		local y = 180+i*10
		DrawScreen.drawGrayCell(x, y, v, -0.25, 1)
		gui.drawText(x+10, y-4, ExtraInputNames[i], black, 0, 10)
	end	
end

function SMKScreen.isGameplay()
	if getGameMode() ~= 0x1C then
		return false
	end

	local lap = getLap()
	if lap >= 5 then
		return false
	end
	
	if lap < 0 then
		return false
	end
	
	return true
end

function SMKScreen.fileHeader(numButtons)
	cfg.NumButtons = numButtons
	
	local text = ""
	for i=1,#ConfigParams do
		text = text .. cfg[ConfigParams[i]] .. " "
	end
	
	return text
end

function SMKScreen.screenText(screen)
	local text = ""
	idx = 1
	for i=1,cfg.ScreenWidth do
		for j=1,cfg.ScreenHeight do
			text = text .. screen[idx] .. " "
			idx = idx + 1
		end
		text = text .. "\n"
	end
	for i=1,NumMaps do
		text = text .. screen[idx] .. " "
		idx = idx + 1
	end
	text = text .. "\n"
	for i=1,#ExtraInputNames do
		text = text .. screen[idx] .. " "
		idx = idx + 1
	end
	text = text .. "\n"
	
	return text
end

function SMKScreen.configure(header, verify)
	for i=1,#header do
		if verify then
			assert(cfg[ConfigParams[i]] == header[i])
		else
			cfg[ConfigParams[i]] = tonumber(header[i])
			print(ConfigParams[i] .. ": " .. header[i])
		end
	end
	
	configUpdated()
end

function SMKScreen.getCheckpoint()
	local checkpoint = mainmemory.readbyte(0x0010DC)
	local lapsize = mainmemory.readbyte(0x000148)
	local lap = mainmemory.readbyte(0x0010C1)-128
	local rank = mainmemory.readbyte(0x1040)/2+1

	return checkpoint + (lap)*lapsize
end

function SMKScreen.getTotalCheckpoints()
	return mainmemory.readbyte(0x000148) * 5
end

function getFrame()
	return mainmemory.read_u16_le(0x38)
end

prevCheckpoint = SMKScreen.getCheckpoint()
prevFrame = getFrame()
function SMKScreen.reward()
	local newCheckpoint = SMKScreen.getCheckpoint()
	
	local curFrame = getFrame()
	if curFrame < prevFrame or curFrame > prevFrame + 60 then
		prevCheckpoint = SMKScreen.getCheckpoint()
	end
	prevFrame = curFrame
	
	local reward = 0
	reward = reward + (newCheckpoint - prevCheckpoint) * 100
	prevCheckpoint = newCheckpoint

	-- Sanity check
	if reward < -5000 then
		return 0
	end
	
	return reward
end

return SMKScreen