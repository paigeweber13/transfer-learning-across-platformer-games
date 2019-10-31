local DrawArrows = {}

Black = 0xFF000000
PartialBlack = 0x80000000
PartialYellow = 0x80FFFF00

ArrowSize = 7
ArrowShaftRadius = 3

MinQEver = -100

-- Arrow lengths
DiffCo = 7   -- Coefficient for relative difference
AbsDiv = 45  -- Amount to divide absolute value by

function drawArrow(baseX, baseY, length, angle)
	points = {
		{-ArrowShaftRadius, 0},
		{-ArrowShaftRadius, -length+ArrowSize},
		{-ArrowSize, -length+ArrowSize},
		{0, -length},
		{ArrowSize, -length+ArrowSize},
		{ArrowShaftRadius, -length+ArrowSize},
		{ArrowShaftRadius, 0},
	}
	
	for i=1,#points do
		local x = points[i][1]
		local y = points[i][2]
		
		local rx = x*math.cos(angle) - y*math.sin(angle)
		local ry = x*math.sin(angle) + y*math.cos(angle)
		
		points[i] = {rx+baseX, ry+baseY}
		
	end
	
	gui.drawPolygon(points, Black, PartialYellow)
end

function DrawArrows.draw(q_vals)
	local minQ = nil
	local maxQ = nil
	for i=1,#q_vals do
		local q = q_vals[i]
		if q < MinQEver then
			MinQEver = q
		end		
		if maxQ == nil or q > maxQ then
			maxQ = q
		end
		if minQ == nil or q < minQ then
			minQ = q
		end
	end
	
	if minQ >= maxQ then
		maxQ = minQ + 0.1
	end
	
	local d = maxQ - minQ
	
	lengths = {}
	for i = 1,#q_vals do
		lengths[i] = ((q_vals[i] - minQ) / d) * DiffCo + ArrowSize + 1 + (q_vals[i] - MinQEver) / AbsDiv
	end
	
	drawArrow(128, 69, lengths[1], 0)
	drawArrow(136, 75, lengths[2], 1.0)
	drawArrow(120, 75, lengths[3], -1.0)
end

while true do
	if prevQVals ~= nil then
		DrawArrows.draw(prevQVals)
	end

	emu.frameadvance()
end

return DrawArrows