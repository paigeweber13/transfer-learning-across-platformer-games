local DrawSmiley = {}

SmileyMin = 0
SmileyMax = 1

Black = 0xFF000000
Yellow = 0xFFFFFF00

function DrawSmiley.draw(q)
	if q > SmileyMax then
		SmileyMax = q
	end
	if q < SmileyMin then
		SmileyMin = q
	end
		
	local happiness = (q - SmileyMin) / (SmileyMax - SmileyMin)
	
	gui.drawEllipse(210, 20, 25, 25, Black, Yellow)
	local mouth = {
		{215, 40 - happiness * 7},
		{219, 35 + happiness * 7},
		{226, 35 + happiness * 7},
		{230, 40 - happiness * 7},
	}
	gui.drawBezier(mouth, Black)
	
	gui.drawEllipse(217, 27, 3, 3, Black, Black)
	gui.drawEllipse(225, 27, 3, 3, Black, Black)
end

local frame = 0

while true do
	frame = frame + 1
	if frame >= 3600 then
		frame = 0
		SmileyMin = prevQ
		SmileyMax = prevQ + 1
	end

	if prevQ ~= nil then
		DrawSmiley.draw(prevQ)
	end
	
	emu.frameadvance()
end
	
return DrawSmiley