GBWWasteAwareGate = GBWWasteAwareGate or {}

GBWWasteAwareGate.modName = g_currentModName or "FS25_BgaExtensions_OrchardsGreenhousesCompat"
GBWWasteAwareGate.modDirectory = g_currentModDirectory or ""
GBWWasteAwareGate.providerModName = "FS25_orchardsAndGreenhouses_crossplay"
GBWWasteAwareGate.requiredFillType = "ORGANICWASTE"
GBWWasteAwareGate.storeXml = "placeables/gbw/wasteAwareWetSubstratePrep.xml"

local function gbwGateInfo(message, ...)
    if Logging ~= nil and Logging.info ~= nil then
        Logging.info("[GBWWasteAwareGate] " .. message, ...)
    else
        print(string.format("[GBWWasteAwareGate] " .. message, ...))
    end
end

local function gbwGateWarning(message, ...)
    if Logging ~= nil and Logging.warning ~= nil then
        Logging.warning("[GBWWasteAwareGate] " .. message, ...)
    else
        print(string.format("[GBWWasteAwareGate] Warning: " .. message, ...))
    end
end

local function normalizePath(value)
    value = value or ""
    value = value:gsub("\\", "/")
    return value:lower()
end

function GBWWasteAwareGate:isProviderActive()
    if g_modIsLoaded ~= nil then
        return g_modIsLoaded[self.providerModName] == true
    end

    if g_modManager ~= nil and g_modManager.getModByName ~= nil then
        return g_modManager:getModByName(self.providerModName) ~= nil
    end

    return false
end

function GBWWasteAwareGate:hasRequiredFillType()
    if g_fillTypeManager == nil then
        return false
    end

    if g_fillTypeManager.getFillTypeIndexByName ~= nil then
        local fillTypeIndex = g_fillTypeManager:getFillTypeIndexByName(self.requiredFillType)
        if fillTypeIndex ~= nil and (FillType == nil or FillType.UNKNOWN == nil or fillTypeIndex ~= FillType.UNKNOWN) then
            return true
        end
    end

    if g_fillTypeManager.getFillTypeByName ~= nil then
        return g_fillTypeManager:getFillTypeByName(self.requiredFillType) ~= nil
    end

    return false
end

function GBWWasteAwareGate:isSettingEnabled()
    if GBWCompatSettings == nil or GBWCompatSettings.isWasteAwareOrganicSideStreamsEnabled == nil then
        return true
    end

    return GBWCompatSettings:isWasteAwareOrganicSideStreamsEnabled()
end

function GBWWasteAwareGate:getInactiveReason()
    if not self:isSettingEnabled() then
        return "setting disabled"
    end

    if not self:isProviderActive() then
        return string.format("provider mod '%s' is not active", self.providerModName)
    end

    if not self:hasRequiredFillType() then
        return string.format("required fillType '%s' is not registered", self.requiredFillType)
    end

    return nil
end

function GBWWasteAwareGate:findStoreItem()
    if g_storeManager == nil or g_storeManager.items == nil then
        return nil, nil
    end

    local needle = normalizePath(self.storeXml)
    for index, item in ipairs(g_storeManager.items) do
        local xmlFilename = normalizePath(item.xmlFilename or item.xmlFilenameLower)
        if xmlFilename == needle or string.find(xmlFilename, needle, 1, true) ~= nil then
            return item, index
        end
    end

    return nil, nil
end

function GBWWasteAwareGate:hideStoreItem(reason)
    local item = self:findStoreItem()
    if item ~= nil then
        item.showInStore = false
    end

    gbwGateInfo("Waste-aware wet substrate prep shop item hidden: %s.", reason)
end

function GBWWasteAwareGate:registerStoreItem()
    if g_storeManager == nil or g_storeManager.loadItem == nil then
        gbwGateWarning("Store manager is unavailable; waste-aware wet substrate prep cannot be registered.")
        return false
    end

    local existingItem = self:findStoreItem()
    if existingItem ~= nil then
        existingItem.showInStore = true
        gbwGateInfo("Waste-aware wet substrate prep shop item enabled.")
        return true
    end

    local item = g_storeManager:loadItem(self.storeXml, self.modDirectory, self.modName, true, false, nil, nil, true)
    if item == nil then
        gbwGateWarning("Could not load waste-aware wet substrate prep shop item from '%s'.", self.storeXml)
        return false
    end

    item.showInStore = true
    if item.xmlFilenameLower == nil and item.xmlFilename ~= nil then
        item.xmlFilenameLower = item.xmlFilename:lower()
    end

    table.insert(g_storeManager.items, item)

    if g_storeManager.xmlFilenameToItem ~= nil and item.xmlFilenameLower ~= nil then
        g_storeManager.xmlFilenameToItem[item.xmlFilenameLower] = item
    end

    gbwGateInfo("Waste-aware wet substrate prep shop item registered.")
    return true
end

function GBWWasteAwareGate:loadMap()
    if GBWCompatSettings ~= nil and GBWCompatSettings.loadUserSettings ~= nil then
        GBWCompatSettings:loadUserSettings()
    end

    local inactiveReason = self:getInactiveReason()
    if inactiveReason ~= nil then
        self:hideStoreItem(inactiveReason)
        return
    end

    self:registerStoreItem()
end

addModEventListener(GBWWasteAwareGate)
