getmetatable('').__index = function(str,i) return string.sub(str,i,i) end

local NNClient = {}

NNClient.client = nil

function NNClient.connect(host)
	local socket = require("socket")
	local port = 2222
	print("Connecting to " .. host  .. ":" .. port .. "...")
	NNClient.client = socket.connect(host, port)
	if NNClient.client == nil then
		print('Error connecting to server at ' .. host .. ':' .. port .. '.')
	end
	
	NNClient.client:settimeout(-1)
	NNClient.client:setoption("tcp-nodelay", true)
end

function NNClient.close()
	if NNClient.client ~= nil then
		NNClient.client:send("close\n")
		NNClient.client:close()
	end
	NNClient.client = nil
end

function NNClient.isConnected()
	return NNClient.client ~= nil
end

function NNClient.sendList(list)
	local send = ""
	local first = true
	for i=1,#list do
		if first then
			first = false
		else
			send = send .. " "
		end
		send = send .. list[i]
	end
	
	send = send .. "\n"
	
	NNClient.client:send(send)
end

function receiveLine()
	local line = ""
	local data = nil
	local err = nil
	while data ~= "\n" do
		data,err = NNClient.client:receive(1)
		
		if err ~= nil then
			print("Socket Error: " .. err)
			
			NNClient.close()
			return nil
		end
		
		if data ~= nil and data ~= "\n" then
			line = line .. data
		end
	end
	
	return line
end

function NNClient.receiveButtons(ButtonNames)
	local data = receiveLine()
	
	if data == nil then
		return nil
	end
	
	if #data ~= 2*#ButtonNames-1 then
		NNClient.close()
		print("Data Error: Unexpected buttons length " .. #data)
		return
	end

	local jstate = {}
	for i=1,#ButtonNames do
		local button = ButtonNames[i]
		local pressed = data[i*2-1]
		if pressed == "0" then
			jstate[button] = false
		elseif pressed == "1" then
			jstate[button] = true
		else
			print("Data Error: Invalid Press State " .. pressed)
		end
	end
	
	return jstate
end

function NNClient.receiveQ()
	local Q = {}
	local line = receiveLine()
	while line ~= 'end' do
		Q[#Q+1] = tonumber(line)
		line = receiveLine()
	end
	
	return Q
end

function NNClient.receiveProbabilities()
	local probs = {}
	local line = receiveLine()
	while line ~= 'end' do
		probs[#probs+1] = tonumber(line)
		line = receiveLine()
	end
	
	return probs
end

function NNClient.receiveHeader()
	local numParams = receiveLine()
	local header = {}
	for i=1,numParams do
		header[i] = receiveLine()
	end
	
	return header
end

function NNClient.receiveConfig()
	local config = {}
	local name = receiveLine()
	while name ~= 'end' do
		local val = tonumber(receiveLine())
		config[name] = val
		name = receiveLine()
	end
	
	return config
end

function NNClient.receiveControllerLookup()
	local lookup = {}
	
	local line = receiveLine()
	
	while line ~= 'end' do
		local buttons = {}
		while line ~= 'done' do
			local button = line
			line = receiveLine()
			if line == 'false' then
				buttons[button] = false
			else
				buttons[button] = true
			end
			
			line = receiveLine()
		end
		
		lookup[#lookup+1] = buttons
	
		line = receiveLine()
	end
	
	return lookup
end
	

return NNClient