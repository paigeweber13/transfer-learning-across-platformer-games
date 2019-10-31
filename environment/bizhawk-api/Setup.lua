local MenuOption = 0x85
local Lap = 0x10C1
local KartX = 0x101C
local KartState = 0x1010
local StateTimer = 0x1DEC
local StateTimerHigh = 0x1DED
local LakituTimer = 0x1C38
local GameMode = 0x36
local DrivingMode = 0x3A
local CameraX = 0x8D

local triggers = {
	{'reset'},
	{'wait', 250},
	{'press', 'B'},
	{'wait', 10},
	{'press', 'B'},
	{'wait', 12},
	{'memif', {MenuOption, 1}},
	{'press', 'Down'},
	{'wait', 1},
	{'mash', {'B', 430}},
	{'memwait', {0x36, 0x02}},
	{'set', {CameraX, 0x0B}},
	{'wait', 60},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 60},
	{'set', {DrivingMode, 0x06}},
	{'wait', 2},
	{'memwait', {0x41, 0xAF}},
	{'save', 'course1'},
	{'set', {Lap, 134}},
	{'wait', 1},
	{'set', {KartX, 0}},
	{'set', {KartState, 0x78}},
	{'wait', 1},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'mash', {'B', 600}},

	{'memwait', {0x36, 0x02}},
	{'set', {CameraX, 0x0B}},
	{'wait', 60},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 60},
	{'set', {DrivingMode, 0x06}},
	{'wait', 2},
	{'memwait', {0x41, 0xAF}},
	{'save', 'course2'},
	{'set', {Lap, 134}},
	{'wait', 1},
	{'set', {KartX, 0}},
	{'set', {KartState, 0x78}},
	{'wait', 1},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'mash', {'B', 600}},	
	
	{'memwait', {0x36, 0x02}},
	{'set', {CameraX, 0x0B}},
	{'wait', 60},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 60},
	{'set', {DrivingMode, 0x06}},
	{'wait', 2},
	{'memwait', {0x41, 0xAF}},
	{'save', 'course3'},
	{'set', {Lap, 134}},
	{'wait', 1},
	{'set', {KartX, 0}},
	{'set', {KartState, 0x78}},
	{'wait', 1},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'mash', {'B', 600}},
	
	
	{'memwait', {0x36, 0x02}},
	{'set', {CameraX, 0x0B}},
	{'wait', 60},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 60},
	{'set', {DrivingMode, 0x06}},
	{'wait', 2},
	{'memwait', {0x41, 0xAF}},
	{'save', 'course4'},
	{'set', {Lap, 134}},
	{'wait', 1},
	{'set', {KartX, 0}},
	{'set', {KartState, 0x78}},
	{'wait', 1},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'wait', 5},
	{'set', {StateTimer, 1}},
	{'mash', {'B', 600}},
	
	
	{'memwait', {0x36, 0x02}},
	{'set', {CameraX, 0x0B}},
	{'wait', 60},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 2},
	{'set', {LakituTimer, 0x01}},
	{'wait', 60},
	{'set', {DrivingMode, 0x06}},
	{'wait', 2},
	{'memwait', {0x41, 0xAF}},
	{'save', 'course5'},
}

local dir = 'SMKCourses'

-- If directory doesn't exist, create it
os.execute("mkdir " .. dir)

client.speedmode(1000)

-- Reset
-- Set speed
	
local step = 1
while step <= #triggers do
	local act = triggers[step][1]
	
	if act == 'memwait' then
		-- Wait for an address to have a value
		local addr = triggers[step][2][1]
		local val = triggers[step][2][2]
		while mainmemory.readbyte(addr) ~= val do
			emu.frameadvance();
		end
	elseif act == 'memif' then
		local addr = triggers[step][2][1]
		local val = triggers[step][2][2]
		if mainmemory.readbyte(addr) ~= val then
			step = step + 1
		end
	elseif act == 'wait' then
		local frames = triggers[step][2]
		while frames > 0 do
			emu.frameadvance()
			frames = frames - 1
		end
	elseif act == 'save' then
		-- Make a save state
		local name = triggers[step][2]
		savestate.save(dir .. '\\' .. name .. '.State')
	elseif act == 'press' then
		local button = triggers[step][2]
		local j = joypad.get(1)
		j[button] = true
		joypad.set(j, 1)
		emu.frameadvance()
	elseif act == 'mash' then
		local button = triggers[step][2][1]
		local frames = triggers[step][2][2]
		while frames > 0 do
			local j = joypad.get(1)
			j[button] = true
			joypad.set(j, 1)
			emu.frameadvance()
			frames = frames - 1
			emu.frameadvance()
			frames = frames - 1
		end
	elseif act == 'set' then
		-- Set a memory address
		local addr = triggers[step][2][1]
		local val = triggers[step][2][2]
		mainmemory.writebyte(addr, val)
	elseif act == 'reset' then
		-- Reset
		client.reboot_core()
	end
	
	step = step + 1
end

client.reboot_core()

for i=1,500 do
	gui.drawText(70, 100, "Setup Complete.")
	emu.frameadvance()
end