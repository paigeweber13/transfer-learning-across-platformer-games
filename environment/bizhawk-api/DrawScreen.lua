local DrawScreen = {}

function DrawScreen.drawGrayCell(x, y, val, minVal, maxVal)
	local color = math.floor((val-minVal)/(maxVal-minVal)*256)
	if color > 255 then color = 255 end
	if color < 0 then color = 0 end
	local opacity = 0xFF000000
	--if cell.value == 0 then
	--	opacity = 0x50000000
	--end
	color = opacity + color*0x10000 + color*0x100 + color
	gui.drawBox(x, y, x+5, y+5,opacity,color)
end

function DrawScreen.drawScreen(screen, ScreenWidth, ScreenHeight, X, Y)
	cells = {}
	i = 1
	
	local HalfWidth = math.floor(ScreenWidth / 2)
	local HalfHeight = math.floor(ScreenHeight / 2)
	
	for dy=-HalfHeight,HalfHeight do
		for dx=-HalfWidth,HalfWidth do
			cell = {}
			cell.x = X+HalfWidth*5+5*dx
			cell.y = Y+HalfHeight*5+5*dy
			cell.value = screen[i]
			cells[i] = cell
			i = i + 1
		end
	end
	gui.drawBox(X+HalfWidth*5-HalfWidth*5-3,Y+HalfHeight*5-HalfHeight*5-3,X+HalfWidth*5+HalfWidth*5+2,Y+HalfHeight*5+HalfHeight*5+2,0xFF000000, 0x80808080)
	for n,cell in pairs(cells) do
		if cell.value == nil then
			-- Debug info
			print(n)
			print(cell)
			print(cell.value)
		end
		DrawScreen.drawGrayCell(cell.x-2, cell.y-2, cell.value, -1.5, 1.5)
	end
	
	gui.drawBox(X+HalfWidth*5, Y+ScreenHeight*5-5, X+HalfWidth*5+1, Y+ScreenHeight*5-1, 0xFFFF0000)
end

return DrawScreen