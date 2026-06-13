GBWDataPacks = GBWDataPacks or {}

GBWDataPacks.API_VERSION = "1"
GBWDataPacks.MAX_ROUTES_PER_PACK = 12
GBWDataPacks.MAX_ACTIVE_BY_TARGET = {
    biomassIntake = 6,
    wetSubstratePrep = 8,
    dryFuelProcessor = 6
}

GBWDataPacks.TIERS = {
    exceptional = { value = 1.00 },
    excellent = { value = 0.85 },
    good = { value = 0.65 },
    fair = { value = 0.45 },
    emergency = { value = 0.25 }
}

GBWDataPacks.TEMPLATES = {
    forageSilage = {
        target = "biomassIntake",
        outputFillType = "SILAGE_IN",
        pathway = "forageSilage"
    },
    rootMash = {
        target = "wetSubstratePrep",
        outputFillType = "GBW_ROOT_MASH",
        pathway = "wetMash"
    },
    greenMash = {
        target = "wetSubstratePrep",
        outputFillType = "GBW_GREEN_MASH",
        pathway = "wetMash"
    },
    sweetMash = {
        target = "wetSubstratePrep",
        outputFillType = "GBW_SWEET_MASH",
        pathway = "wetMash"
    },
    residueMash = {
        target = "wetSubstratePrep",
        outputFillType = "GBW_RESIDUE_MASH",
        pathway = "wetMash"
    },
    strawPretreatment = {
        target = "biomassIntake",
        outputFillType = "SILAGE_IN",
        pathway = "difficultFermentation",
        requiresSilageAdditive = true
    },
    hayPelletFuel = {
        target = "dryFuelProcessor",
        outputFillType = "HAY_PELLETS",
        pathway = "pelletFuel",
        requiresWater = true,
        requiresMolasses = true
    },
    strawPelletFuel = {
        target = "dryFuelProcessor",
        outputFillType = "STRAW_PELLETS",
        pathway = "pelletFuel",
        requiresWater = true,
        requiresMolasses = true
    }
}

GBWDataPacks.registeredPacks = GBWDataPacks.registeredPacks or {}
GBWDataPacks.registeredPackKeys = GBWDataPacks.registeredPackKeys or {}
GBWDataPacks.activeRoutes = {}
GBWDataPacks.activeCountsByTarget = {}
GBWDataPacks.loadedPackIds = {}

local function gbwInfo(message, ...)
    if PhobosFS25 ~= nil and PhobosFS25.Logging ~= nil and PhobosFS25.Logging.infoSource ~= nil then
        PhobosFS25.Logging.infoSource("GBWDataPacks", message, ...)
    elseif Logging ~= nil and Logging.info ~= nil then
        Logging.info("[GBWDataPacks] " .. message, ...)
    else
        print(string.format("[GBWDataPacks] " .. message, ...))
    end
end

local function gbwWarning(message, ...)
    if PhobosFS25 ~= nil and PhobosFS25.Logging ~= nil and PhobosFS25.Logging.warnSource ~= nil then
        PhobosFS25.Logging.warnSource("GBWDataPacks", message, ...)
    elseif Logging ~= nil and Logging.warning ~= nil then
        Logging.warning("[GBWDataPacks] " .. message, ...)
    else
        print(string.format("[GBWDataPacks] Warning: " .. message, ...))
    end
end

local function isValidIdentifier(value)
    return type(value) == "string" and value:match("^%a[%w_]*$") ~= nil
end

local function normalizeFillType(value)
    if type(value) ~= "string" then
        return nil
    end

    value = value:upper()
    if value:match("^[A-Z0-9_]+$") == nil then
        return nil
    end

    return value
end

local function namespacedProductionId(packId, routeId)
    return string.format("gbwData_%s_%s", packId, routeId)
end

function GBWDataPacks.registerPack(modName, xmlFilename)
    if type(modName) ~= "string" or modName == "" then
        gbwWarning("A data pack tried to register without a valid mod name.")
        return false
    end

    if type(xmlFilename) ~= "string" or xmlFilename == "" then
        gbwWarning("Data pack '%s' tried to register without a valid XML filename.", modName)
        return false
    end

    local registrationKey = modName .. "|" .. xmlFilename
    if GBWDataPacks.registeredPackKeys[registrationKey] then
        return true
    end

    GBWDataPacks.registeredPackKeys[registrationKey] = true
    table.insert(GBWDataPacks.registeredPacks, {
        modName = modName,
        xmlFilename = xmlFilename
    })

    gbwInfo("Registered data pack '%s' for Stage 1 validation.", modName)
    return true
end

function GBWDataPacks:resetLoadedRoutes()
    self.activeRoutes = {}
    self.activeCountsByTarget = {}
    self.loadedPackIds = {}

    for target in pairs(self.MAX_ACTIVE_BY_TARGET) do
        self.activeCountsByTarget[target] = 0
    end
end

function GBWDataPacks:getFillTypeId(fillTypeName)
    if PhobosFS25 ~= nil and PhobosFS25.FillTypes ~= nil and PhobosFS25.FillTypes.getIndex ~= nil then
        return PhobosFS25.FillTypes.getIndex(fillTypeName)
    end

    if g_fillTypeManager == nil or g_fillTypeManager.getFillTypeIndexByName == nil then
        return nil
    end

    return g_fillTypeManager:getFillTypeIndexByName(fillTypeName)
end

function GBWDataPacks:loadRoute(xmlFile, routeKey, pack, routeIndex)
    if routeIndex > self.MAX_ROUTES_PER_PACK then
        gbwWarning("Data pack '%s' exceeds the route cap of %d. Extra route at index %d was skipped.", pack.packId, self.MAX_ROUTES_PER_PACK, routeIndex)
        return false
    end

    local routeId = xmlFile:getValue(routeKey .. "#id")
    if not isValidIdentifier(routeId) then
        gbwWarning("Data pack '%s' has an invalid or missing route id at index %d.", pack.packId, routeIndex)
        return false
    end

    if pack.routeIds[routeId] then
        gbwWarning("Data pack '%s' has duplicate route id '%s'.", pack.packId, routeId)
        return false
    end
    pack.routeIds[routeId] = true

    local inputFillType = normalizeFillType(xmlFile:getValue(routeKey .. "#inputFillType"))
    if inputFillType == nil then
        gbwWarning("Data pack '%s' route '%s' has an invalid or missing inputFillType.", pack.packId, routeId)
        return false
    end

    local target = xmlFile:getValue(routeKey .. "#target")
    if self.MAX_ACTIVE_BY_TARGET[target] == nil then
        gbwWarning("Data pack '%s' route '%s' uses unknown target '%s'.", pack.packId, routeId, tostring(target))
        return false
    end

    local templateId = xmlFile:getValue(routeKey .. "#template")
    local template = self.TEMPLATES[templateId]
    if template == nil then
        gbwWarning("Data pack '%s' route '%s' uses unknown template '%s'.", pack.packId, routeId, tostring(templateId))
        return false
    end

    if template.target ~= target then
        gbwWarning("Data pack '%s' route '%s' uses template '%s' with target '%s'; expected '%s'.", pack.packId, routeId, templateId, target, template.target)
        return false
    end

    local tierId = xmlFile:getValue(routeKey .. "#tier")
    local tier = self.TIERS[tierId]
    if tier == nil then
        gbwWarning("Data pack '%s' route '%s' uses unknown tier '%s'.", pack.packId, routeId, tostring(tierId))
        return false
    end

    local inputFillTypeId = self:getFillTypeId(inputFillType)
    if inputFillTypeId == nil then
        gbwInfo("Skipping data pack route '%s/%s': input fillType '%s' is not registered.", pack.packId, routeId, inputFillType)
        return false
    end

    local outputFillTypeId = self:getFillTypeId(template.outputFillType)
    if outputFillTypeId == nil then
        gbwWarning("Data pack '%s' route '%s' cannot use missing output fillType '%s'.", pack.packId, routeId, template.outputFillType)
        return false
    end

    if self.activeCountsByTarget[target] >= self.MAX_ACTIVE_BY_TARGET[target] then
        gbwWarning("Data pack route '%s/%s' skipped because target '%s' reached the active route cap of %d.", pack.packId, routeId, target, self.MAX_ACTIVE_BY_TARGET[target])
        return false
    end

    local productionId = namespacedProductionId(pack.packId, routeId)
    if self.activeRoutes[productionId] ~= nil then
        gbwWarning("Data pack route '%s/%s' collided with existing production id '%s'.", pack.packId, routeId, productionId)
        return false
    end

    self.activeCountsByTarget[target] = self.activeCountsByTarget[target] + 1
    self.activeRoutes[productionId] = {
        productionId = productionId,
        packId = pack.packId,
        routeId = routeId,
        title = pack.title,
        author = pack.author,
        inputFillType = inputFillType,
        inputFillTypeId = inputFillTypeId,
        outputFillType = template.outputFillType,
        outputFillTypeId = outputFillTypeId,
        target = target,
        template = templateId,
        pathway = template.pathway,
        tier = tierId,
        tierValue = tier.value,
        requiresSilageAdditive = template.requiresSilageAdditive == true,
        requiresWater = template.requiresWater == true,
        requiresMolasses = template.requiresMolasses == true
    }

    return true
end

function GBWDataPacks:loadPack(registration)
    local xmlFile = nil
    if PhobosFS25 ~= nil and PhobosFS25.XmlFile ~= nil and PhobosFS25.XmlFile.load ~= nil then
        xmlFile = PhobosFS25.XmlFile.load("GBWDataPack", registration.xmlFilename)
    elseif XMLFile ~= nil and XMLFile.load ~= nil then
        xmlFile = XMLFile.load("GBWDataPack", registration.xmlFilename)
    end

    if xmlFile == nil then
        gbwWarning("Could not load data pack XML for '%s': %s", registration.modName, registration.xmlFilename)
        return 0
    end

    local rootKey = "gbwDataPack"
    local hasRoot = false
    if PhobosFS25 ~= nil and PhobosFS25.XmlFile ~= nil and PhobosFS25.XmlFile.hasProperty ~= nil then
        hasRoot = PhobosFS25.XmlFile.hasProperty(xmlFile, rootKey)
    else
        hasRoot = xmlFile:hasProperty(rootKey)
    end

    if not hasRoot then
        gbwWarning("Data pack '%s' has no gbwDataPack root node.", registration.modName)
        xmlFile:delete()
        return 0
    end

    local apiVersion = xmlFile:getValue(rootKey .. "#apiVersion")
    if apiVersion ~= self.API_VERSION then
        gbwWarning("Data pack '%s' uses unsupported API version '%s'. Expected '%s'.", registration.modName, tostring(apiVersion), self.API_VERSION)
        xmlFile:delete()
        return 0
    end

    local packId = xmlFile:getValue(rootKey .. "#packId")
    if not isValidIdentifier(packId) then
        gbwWarning("Data pack '%s' has an invalid or missing packId.", registration.modName)
        xmlFile:delete()
        return 0
    end
    if self.loadedPackIds[packId] then
        gbwWarning("Data pack '%s' uses duplicate packId '%s'.", registration.modName, packId)
        xmlFile:delete()
        return 0
    end
    self.loadedPackIds[packId] = true

    local pack = {
        packId = packId,
        title = xmlFile:getValue(rootKey .. "#title") or registration.modName,
        author = xmlFile:getValue(rootKey .. "#author") or "Unknown",
        routeIds = {}
    }

    local loadedRoutes = 0
    local routeIndex = 0
    local function loadRoute(_, routeKey)
        routeIndex = routeIndex + 1
        if self:loadRoute(xmlFile, routeKey, pack, routeIndex) then
            loadedRoutes = loadedRoutes + 1
        end
    end

    if PhobosFS25 ~= nil and PhobosFS25.XmlFile ~= nil and PhobosFS25.XmlFile.iterate ~= nil then
        PhobosFS25.XmlFile.iterate(xmlFile, rootKey .. ".routes.route", loadRoute, self.MAX_ROUTES_PER_PACK + 1)
    else
        xmlFile:iterate(rootKey .. ".routes.route", loadRoute)
    end

    if routeIndex == 0 then
        gbwWarning("Data pack '%s' does not define any routes.", packId)
    end

    xmlFile:delete()
    return loadedRoutes
end

function GBWDataPacks:loadRegisteredPacks()
    self:resetLoadedRoutes()

    local activeRoutes = 0
    for _, registration in ipairs(self.registeredPacks) do
        activeRoutes = activeRoutes + self:loadPack(registration)
    end

    if #self.registeredPacks > 0 then
        gbwInfo("Prepared %d active route(s) from %d data pack(s). Recipe injection is disabled in this Stage 1 build.", activeRoutes, #self.registeredPacks)
    end
end

function GBWDataPacks:loadMap()
    self:loadRegisteredPacks()
end

function GBWDataPacks:deleteMap()
    self:resetLoadedRoutes()
end

function GBWDataPacks:getActiveRoutes()
    return self.activeRoutes
end

addModEventListener(GBWDataPacks)
