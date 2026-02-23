local CustomHandler = {
  PRIORITY = 1000,
  VERSION = "1.0"
}

function CustomHandler:access(conf)
  local talentica_header = kong.request.get_header("Talentica")

  if not talentica_header then
    return kong.response.exit(403, {
      message = "Talentica header missing"
    })
  end
end

function CustomHandler:header_filter(conf)
  kong.response.set_header("X-Platform-Secure", "true")
end

return CustomHandler

