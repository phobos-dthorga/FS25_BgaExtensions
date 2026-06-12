GBWCompatSettings = GBWCompatSettings or {}

GBWCompatSettings.modName = g_currentModName or "FS25_BgaExtensions_OrchardsGreenhousesCompat"
GBWCompatSettings.modSettingsDirectory = g_currentModSettingsDirectory
    or ((g_modSettingsDirectory or "") .. GBWCompatSettings.modName .. "/")
GBWCompatSettings.xmlFilename = GBWCompatSettings.modSettingsDirectory .. "settings.xml"
GBWCompatSettings.wasteAwareOrganicSideStreams = true
GBWCompatSettings.loaded = false

local function gbwSettingsInfo(message, ...)
    if PhobosFS25 ~= nil and PhobosFS25.Logging ~= nil and PhobosFS25.Logging.infoSource ~= nil then
        PhobosFS25.Logging.infoSource("GBWCompatSettings", message, ...)
    elseif Logging ~= nil and Logging.info ~= nil then
        Logging.info("[GBWCompatSettings] " .. message, ...)
    else
        print(string.format("[GBWCompatSettings] " .. message, ...))
    end
end

local function gbwSettingsText(key, fallback)
    if g_i18n ~= nil and g_i18n.modEnvironments ~= nil then
        local modEnvironment = g_i18n.modEnvironments[GBWCompatSettings.modName]
        if modEnvironment ~= nil and modEnvironment.texts ~= nil and modEnvironment.texts[key] ~= nil then
            return modEnvironment.texts[key]
        end
    end

    if g_i18n ~= nil and g_i18n.getText ~= nil then
        local ok, value = pcall(function()
            return g_i18n:getText(key)
        end)

        if ok and value ~= nil and value ~= "" and value ~= key then
            return value
        end
    end

    return fallback
end

function GBWCompatSettings:loadUserSettings()
    if self.loaded then
        return
    end

    self.loaded = true

    if g_client == nil or XMLFile == nil then
        return
    end

    local xmlFile = XMLFile.loadIfExists("GBWCompatSettings", self.xmlFilename)
    if xmlFile ~= nil then
        self.wasteAwareOrganicSideStreams = xmlFile:getBool(
            "gbwCompatSettings.wasteAwareOrganicSideStreams#enabled",
            self.wasteAwareOrganicSideStreams
        )
        xmlFile:delete()
    end
end

function GBWCompatSettings:saveUserSettings()
    if g_client == nil or XMLFile == nil then
        return
    end

    if createFolder ~= nil then
        createFolder(self.modSettingsDirectory)
    end

    local xmlFile = XMLFile.create("GBWCompatSettings", self.xmlFilename, "gbwCompatSettings")
    if xmlFile ~= nil then
        xmlFile:setBool(
            "gbwCompatSettings.wasteAwareOrganicSideStreams#enabled",
            self.wasteAwareOrganicSideStreams
        )
        xmlFile:save()
        xmlFile:delete()
    end
end

function GBWCompatSettings:isWasteAwareOrganicSideStreamsEnabled()
    self:loadUserSettings()
    return self.wasteAwareOrganicSideStreams == true
end

function GBWCompatSettings:setWasteAwareOrganicSideStreams(enabled)
    self.wasteAwareOrganicSideStreams = enabled == true
    self.loaded = true
    self:saveUserSettings()
    gbwSettingsInfo(
        "Waste-aware organic side-streams setting is %s. Shop availability updates on next save load.",
        self.wasteAwareOrganicSideStreams and "enabled" or "disabled"
    )
end

function GBWCompatSettings:addOptionToLayout(gameSettingsLayout, cloneElement, id, textId, settingsTemplate)
    cloneElement.id = id

    local tooltip = cloneElement.elements ~= nil and cloneElement.elements[1] or nil
    if tooltip ~= nil then
        tooltip.text = gbwSettingsText(textId .. "Tooltip", "")
        tooltip.sourceText = tooltip.text
    end

    if settingsTemplate == nil or settingsTemplate.elements == nil or settingsTemplate.elements[2] == nil then
        gameSettingsLayout:addElement(cloneElement)
        return
    end

    local optionTitle = settingsTemplate.elements[2]:clone()
    optionTitle.id = id .. "Title"
    optionTitle:applyProfile("fs25_settingsMultiTextOptionTitle", true)
    optionTitle:setText(gbwSettingsText(textId, textId))

    local optionContainer = settingsTemplate:clone()
    optionContainer.id = id .. "Container"
    optionContainer:applyProfile("fs25_multiTextOptionContainer", true)

    for key in pairs(optionContainer.elements) do
        optionContainer.elements[key] = nil
    end

    optionContainer:addElement(optionTitle)
    optionContainer:addElement(cloneElement)
    gameSettingsLayout:addElement(optionContainer)
end

function GBWCompatSettings.initGameSettingsGui(frame)
    if frame == nil or frame.gbwWasteAwareOrganicSideStreams ~= nil then
        return
    end

    if frame.gameSettingsLayout == nil or frame.checkTraffic == nil then
        return
    end

    GBWCompatSettings:loadUserSettings()

    local layout = frame.gameSettingsLayout
    local elementCount = #layout.elements
    if elementCount < 1 then
        return
    end

    local headerTemplate = layout.elements[math.min(7, elementCount)]
    if headerTemplate ~= nil then
        local header = headerTemplate:clone()
        header:applyProfile("fs25_settingsSectionHeader", true)
        header:setText(gbwSettingsText("settings_header_gbwCompat", "Gekko BioWorks"))
        header.focusChangeData = {}

        if FocusManager ~= nil and FocusManager.serveAutoFocusId ~= nil then
            header.focusId = FocusManager.serveAutoFocusId()
        end

        layout:addElement(header)
    end

    local settingsTemplate = layout.elements[math.min(5, elementCount)]
    local option = frame.checkTraffic:clone()
    option.target = GBWCompatSettings
    option.onClickCallback = GBWCompatSettings.onSettingsStateChanged
    option.buttonLRChange = GBWCompatSettings.onSettingsStateChanged
    option.texts[1] = gbwSettingsText("ui_off", "Off")
    option.texts[2] = gbwSettingsText("ui_on", "On")

    frame.gbwWasteAwareOrganicSideStreams = option
    GBWCompatSettings:addOptionToLayout(
        layout,
        frame.gbwWasteAwareOrganicSideStreams,
        "gbwWasteAwareOrganicSideStreams",
        "setting_gbwWasteAwareOrganicSideStreams",
        settingsTemplate
    )

    frame.gbwWasteAwareOrganicSideStreams:setIsChecked(
        GBWCompatSettings.wasteAwareOrganicSideStreams,
        true
    )
    frame.gbwWasteAwareOrganicSideStreams:updateSelection()
    layout:invalidateLayout()
end

function GBWCompatSettings.onSettingsStateChanged(_, stateOrElement, maybeElement)
    local element = maybeElement
    if element == nil and type(stateOrElement) == "table" then
        element = stateOrElement
    end

    if element == nil or element.id ~= "gbwWasteAwareOrganicSideStreams" then
        return
    end

    local enabled = false
    if element.getIsChecked ~= nil then
        enabled = element:getIsChecked()
    end

    GBWCompatSettings:setWasteAwareOrganicSideStreams(enabled)
end

function GBWCompatSettings:loadMap()
    self:loadUserSettings()
end

if InGameMenuSettingsFrame ~= nil and Utils ~= nil and Utils.appendedFunction ~= nil then
    InGameMenuSettingsFrame.onFrameOpen = Utils.appendedFunction(
        InGameMenuSettingsFrame.onFrameOpen,
        GBWCompatSettings.initGameSettingsGui
    )
end

addModEventListener(GBWCompatSettings)
