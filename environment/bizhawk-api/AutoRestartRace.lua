function getLap()
	return mainmemory.readbyte(0x10C1)-128
end


while true do
	if getLap() > 5 then
		savestate.load("race1.state")
	end
	
	emu.frameadvance();
end