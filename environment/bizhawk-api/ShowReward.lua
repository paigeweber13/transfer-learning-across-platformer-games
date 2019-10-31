local messages = {}

function getCheckpoint()
	local checkpoint = mainmemory.readbyte(0x0010DC)
	local lapsize = mainmemory.readbyte(0x000148)
	local lap = mainmemory.readbyte(0x0010C1)-128
	local rank = mainmemory.readbyte(0x1040)/2+1

	return checkpoint + (lap)*lapsize
end

local checkpoint = getCheckpoint()
local Red = 0xFF0000
local Green = 0x00FF00
local Opaque = 0xF0

while true do
	local newCheckpoint = getCheckpoint()
	local diff = newCheckpoint - checkpoint
	
	if diff > -20 and diff < 20 then
		if diff ~= 0 then
			local message = {}
			message.text = tostring(diff*100)
			if diff < 0 then
				message.color = Red
			else
				message.text = "+" .. message.text
				message.color = Green
			end
			message.time = 60
			message.opacity = Opaque
			messages[#messages+1] = message
		end
	end
	
	checkpoint = newCheckpoint
	
	for m=1,#messages do
		local message = messages[m]
		local color = message.opacity * 0x1000000 + message.color
		local background = message.opacity / 8 * 0x1000000
		gui.drawText(110, 40+message.time * 1 / 2, message.text, color, background, 11)
		message.time = message.time - 1
		if message.time < 35 then
			message.opacity = math.floor(message.opacity * 4 / 5)
		end
	end
	
	if #messages >= 1 and messages[1].time <= 0 then
		table.remove(messages, 1)
	end

	emu.frameadvance();
end