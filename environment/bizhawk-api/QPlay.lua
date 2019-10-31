local Game = nil

Game = require("SMKScreen")

client.pause()

ButtonNames = {
	"Left",
	"Right",
	"B",
}

function getController()
	local buttons = {}
	local state = joypad.get(1)
	
	for b=1,#ButtonNames do
		button = ButtonNames[b] 
		if state[button] then
			buttons[b] = 1
		else
			buttons[b] = 0
		end
	end	
	
	return buttons
end

function softmax(v, temperature)
	-- Get the maximum value
	m = v[1]
	for i=2,#v do
		m = math.max(m, v[i])
	end
	
	m = m / temperature

	-- Get the exponentiated values and their sum
	local s = {}
	local sum = 0

	for i=1,#v do
		s[i] = math.exp(v[i] / temperature - m)
		sum = sum + s[i]
	end
	
	-- Squish in range [0,1]
	for i=1,#v do
		s[i] = s[i] / sum
	end
	
	return s
end

function sample_softmax(s)
	local r = math.random()
	
	for i=1,#s do
		r = r - s[i]
		if r <= 0 then
			return i
		end
	end
end

controller_lookup = {
	{["Left"] = false, ["Right"] = false, ["B"] = false},
	{["Left"] = false, ["Right"] = false, ["B"] = true},
	{["Left"] = false, ["Right"] = true, ["B"] = false},
	{["Left"] = false, ["Right"] = true, ["B"] = true},
	{["Left"] = true, ["Right"] = false, ["B"] = false},
	{["Left"] = true, ["Right"] = false, ["B"] = true},
}

qclient = require("QClient")

function connect()
	local hostnameFile, err = io.open('hostname.txt', 'w')
	hostnameFile:write(forms.gettext(hostnameBox))
	hostnameFile:close()

	if qclient.isConnected() then
		forms.settext(connectButton, "NN Start")
		qclient.close()
	else
		forms.settext(connectButton, "NN Stop")
		qclient.connect(forms.gettext(hostnameBox))
		if qclient.isConnected() then
			print("Connected.")
		else
			print("Unable to connect.")
		end
		
		header = qclient.receiveHeader()
		Game.configure(header, false)
		config = qclient.receiveConfig()
		controller_lookup = qclient.receiveControllerLookup()
		print(config)
		
		local j = {}
		for b=1,#ButtonNames do
			local name = ButtonNames[b]
			j[name] = controller_lookup[1][name]
		end	

		joypad.set(j, 1)
	end
end

display = false

function displayCallback()
	display = not display
	if display then
		forms.settext(displayButton, "-Screen")
	else
		forms.settext(displayButton, "+Screen")
	end
		
end

manual = false
function toggleManual()
	manual = not manual
	
	if manual then
		forms.settext(manualButton, "-Manual")
	else
		forms.settext(manualButton, "+Manual")
	end
end

function setSuggestedLabel(buttons)
	local text = "MaxQ: "
	for b=1,#ButtonNames do
		if buttons[ButtonNames[b]] then
			text = text .. ButtonNames[b] .. " "
		end
	end
	
	forms.settext(suggestedLabel, text)
end

randomize = true
function randomizeGreedy()
	randomize = not randomize
	
	if randomize then
		forms.settext(randomButton, "-Randomize")
	else
		forms.settext(randomButton, "+Randomize")
	end
end

interactive = false
local interactiveTimer = 1
function toggleInteractive()
	interactive = not interactive
	
	if interactive then
		forms.settext(interactiveButton, "-Interactive")
	else
		forms.settext(interactiveButton, "+Interactive")
	end
end

do_display = 1
function toggleNetDisp()
	do_display = 1 - do_display
	if do_display == 1 then
		forms.settext(toggleNetworkDisplayButton, "-NetDisp")
	else
		forms.settext(toggleNetworkDisplayButton, "+NetDisp")
	end
end

form = forms.newform(195, 335, "QPlay")
hostnameBox = forms.textbox(form, "", 100, 20, "TEXT", 60, 70)
forms.label(form, "Hostname:", 3, 73)
connectButton = forms.button(form, "NN Start", connect, 3, 100)
manualButton = forms.button(form, "+Manual", toggleManual, 3, 130)
displayButton = forms.button(form, "+Screen", displayCallback, 3, 170, 150)
suggestedLabel = forms.label(form, "[None]", 3, 40)
rewardLabel = forms.label(form, "[None]", 3, 20)
greedyBox = forms.textbox(form, 50, 50, 20, "UNSIGNED", 3, 200)
randomButton = forms.button(form, "-Randomize", randomizeGreedy, 80, 200)
interactiveButton = forms.button(form, "+Interactive", toggleInteractive, 3, 230)
toggleNetworkDisplayButton = forms.button(form, "-NetDisp", toggleNetDisp, 3, 260)

local hostnameFile, err = io.open('hostname.txt', 'r')
if not err then
	forms.settext(hostnameBox, hostnameFile:read())
	hostnameFile:close()
end

function onExit()
	forms.destroy(form)
	
	qclient.close()
end

event.onexit(onExit)

recFrame = 0
screen = nil
nnJoypad = joypad.get(1)
local totalReward = 0.0
local currentCourse = 1
local timeOnCourse = 0

function getLap()
	return mainmemory.readbyte(0x10C1)-128
end

function SecondsToClock(seconds)
  local seconds = tonumber(seconds)

  if seconds <= 0 then
    return "0:00";
  else
    mins = string.format("%d", math.floor(seconds/60));
    secs = string.format("%02d", math.floor(seconds - mins *60));
    return mins..":"..secs
  end
end

local Places = {
	"1st",
	"2nd",
	"3rd",
	"4th",
	"5th",
	"6th",
	"7th",
	"8th",
}

savestate.load("SMKCourses\\Course" .. currentCourse .. ".State")

prevQ = 0
prevQVals = {0, 0, 0}
local Black = 0xFF000000
local Red = 0xFFFF0000

while true do
	if qclient.isConnected() then
		if getLap() >= 5 or timeOnCourse > 60*config.seconds_per_course then
			local place = mainmemory.readbyte(0x1040)/2+1
			print('Exiting course ' .. currentCourse .. ' at checkpoint ' .. Game.getCheckpoint() .. '/' .. Game.getTotalCheckpoints() .. ' at ' .. SecondsToClock(timeOnCourse/60) .. ' in ' .. Places[place])
		
			currentCourse = currentCourse + 1
			--if currentCourse > 15 then
			if currentCourse > 5 then
				currentCourse = 1
			end
			--currentCourse = 1
			
			savestate.load("SMKCourses\\Course" .. currentCourse .. ".State")
			timeOnCourse = 0
		end

		forms.settext(connectButton, "NN Stop")
	
		if interactive then
			interactiveTimer = interactiveTimer - 1
			if interactiveTimer < 0 then
				toggleManual()
				interactiveTimer = math.random(60, 300)
			end
			
			if manual then
				gui.drawText(5, 5, "Player Control")
			else
				gui.drawText(5, 5, "MarIQ Control")
			end
		end
		
		if randomize and not manual then
			gui.drawText(5, 5, "Tryhard: " .. forms.gettext(greedyBox) .. "%")
		end

		if recFrame % math.floor(60 / config.steps_per_second) == 0 then
			screen = Game.getScreen(1)
			
			if qclient.isConnected() then
				local currentReward = Game.reward()
				totalReward = totalReward * config.discount + currentReward
				forms.settext(rewardLabel, totalReward)

				qclient.sendList(screen)
				qclient.sendList(getController())
				qclient.sendList({currentReward})
				qclient.sendList({do_display})
				if config.track_position then
					qclient.sendList(Game.getPosition())
				end
				
				local QVals = qclient.receiveQ()
				
				local maxQ = QVals[1]
				local maxIndex = 1
				for i=2,#QVals do
					if QVals[i] > maxQ then
						maxQ = QVals[i]
						maxIndex = i
					end
				end
				
				local probs = qclient.receiveProbabilities()			
				local greedy = tonumber(forms.gettext(greedyBox))
				if math.random(1, 100) > greedy then
					local maxQ = QVals[1]
					local maxQIndex = 1
					for i=2,#QVals do
						if QVals[i] > maxQ then
							maxQ = QVals[i]
							maxQIndex = i
						end
					end
					
					--QVals[maxQIndex] = -10000
					
					local s = softmax(QVals, config.exploration_softmax)
					maxIndex = sample_softmax(s)
					
					buttons = controller_lookup[maxScoreIndex]
				end
				
				local buttons = controller_lookup[maxIndex]
				prevQ = QVals[maxIndex]
				prevQVals = QVals
				
				for b=1,#ButtonNames do
					name = ButtonNames[b]
					nnJoypad[name] = buttons[name]
				end
				
				setSuggestedLabel(buttons)
			end
			
			
		end
		if not manual then
			joypad.set(nnJoypad, 1)
		end
		
		if recFrame % 1200 == 0 and randomize then
			forms.settext(greedyBox, math.random(config.tryhard_min, 100))
		end

		recFrame = recFrame + 1
		timeOnCourse = timeOnCourse + 1
		
		if display then
			Game.displayScreen(screen)
		end
	else
		forms.settext(connectButton, "NN Start")
	end
	
	emu.frameadvance();
end