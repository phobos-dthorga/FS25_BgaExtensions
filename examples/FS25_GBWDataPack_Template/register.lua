local modName = g_currentModName or "FS25_GBWDataPack_Template"
local modDirectory = g_currentModDirectory or ""
local xmlFilename = Utils.getFilename("gbwDataPack.xml", modDirectory)

if GBWDataPacks ~= nil and GBWDataPacks.registerPack ~= nil then
    GBWDataPacks.registerPack(modName, xmlFilename)
elseif Logging ~= nil and Logging.warning ~= nil then
    Logging.warning("[FS25_GBWDataPack_Template] GBWDataPacks API is not available. Enable FS25_BgaExtensions and keep it as a dependency.")
end
