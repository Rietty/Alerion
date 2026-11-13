-- Everybody Codes - Repository-local Neovim configuration

local M = {}

-- Configuration
local TEMPLATE = "src/solutions/template.py"
local APP = "src/app.py"
local MAX_QUEST = 20
local PARTS = { "1", "2", "3" }

local function project_root()
	return vim.fs.root(0, { "pyproject.toml", ".git" }) or vim.fn.getcwd()
end

-- Get event/quest from current file path (.../e2025/quest01.py)
local function get_current_quest()
	local file = vim.api.nvim_buf_get_name(0)

	local event, quest = file:match("[/\\]e(%d+)[/\\]quest(%d+)%.py$")

	if event and quest then
		return event, tonumber(quest)
	end

	return nil, nil
end

-- Ask for event and quest when they cannot be inferred
local function get_ec_quest(callback)
	local event, quest = get_current_quest()

	if event and quest then
		callback(event, quest)
		return
	end

	vim.ui.input({ prompt = "Event: " }, function(input_event)
		if not input_event or not input_event:match("^%d%d%d%d$") then
			return
		end

		vim.ui.input({ prompt = "Quest: " }, function(input_quest)
			local parsed_quest = tonumber(input_quest)

			if not parsed_quest or parsed_quest < 1 or parsed_quest > MAX_QUEST then
				return
			end

			callback(input_event, parsed_quest)
		end)
	end)
end

-- Create a new quest's solution
function M.create_quest()
	local root = project_root()

	local template = root .. "/" .. TEMPLATE

	if vim.fn.filereadable(template) == 0 then
		vim.notify("Template not found: " .. TEMPLATE, vim.log.levels.ERROR)
		return
	end

	get_ec_quest(function(event, quest)
		local quest_padded = string.format("%02d", quest)

		local destination_dir = string.format("%s/src/solutions/e%s", root, event)

		local destination = string.format("%s/quest%s.py", destination_dir, quest_padded)

		if vim.fn.filereadable(destination) == 1 then
			vim.notify("Already exists, opening: " .. destination, vim.log.levels.WARN)
			vim.cmd("edit " .. vim.fn.fnameescape(destination))
			return
		end

		vim.fn.mkdir(destination_dir, "p")

		local contents = vim.fn.readfile(template)

		if vim.fn.writefile(contents, destination) ~= 0 then
			vim.notify("Failed to create solution", vim.log.levels.ERROR)
			return
		end

		vim.notify("Created " .. destination, vim.log.levels.INFO)

		vim.cmd("edit " .. vim.fn.fnameescape(destination))
	end)
end

-- Run an Everybody Codes solution
function M.run()
	local root = project_root()

	get_ec_quest(function(event, quest)
		vim.ui.select(PARTS, {
			prompt = "Select Everybody Codes part:",
		}, function(part)
			if not part then
				return
			end

			vim.ui.select({
				"Run",
				"Test",
				"Submit",
			}, {
				prompt = "Select execution mode:",
			}, function(mode)
				if not mode then
					return
				end

				local args = {
					"uv",
					"run",
					APP,
					"-e",
					tostring(event),
					"-q",
					tostring(quest),
					"-p",
					part,
				}

				if mode == "Test" then
					table.insert(args, "-t")
				elseif mode == "Submit" then
					table.insert(args, "-s")
				end

				-- Open terminal split
				vim.cmd("botright 15new")

				vim.fn.termopen(args, {
					cwd = root,
				})

				vim.cmd("startinsert")
			end)
		end)
	end)
end

-- Keybindings
vim.keymap.set("n", "<leader>an", M.create_quest, {
	desc = "EC: Create new quest",
})

vim.keymap.set("n", "<leader>ar", M.run, {
	desc = "EC: Run solution",
})

return M