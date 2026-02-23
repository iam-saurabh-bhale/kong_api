local BasePlugin = require "kong.plugins.base_plugin"
local responses = require "kong.tools.responses"

local HeaderCheck = BasePlugin:extend()

HeaderCheck.VERSION = "1.0.0"
HeaderCheck.PRIORITY = 1000  -- run early

function HeaderCheck:new()
  HeaderCheck.super.new(self, "header-check")
end

function HeaderCheck:access(conf)
  HeaderCheck.super.access(self)

  -- Only enforce for /health route
  local path = ngx.var.uri
  if path == "/health" then
    local header = ngx.req.get_headers()["saurabh-bhale"]
    if not header or header ~= "present" then
      return responses.send(403, { message = "Forbidden: missing saurabh-bhale header" })
    end
  end
end

return HeaderCheck