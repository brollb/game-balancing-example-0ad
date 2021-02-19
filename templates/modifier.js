(function() {
    const cmpPlayerManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_PlayerManager);
    const playerEnt = cmpPlayerManager.GetPlayerByID('1');
    const cmpModifiersManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_ModifiersManager);
    cmpModifiersManager.AddModifiers("cheat/$parameter", {
        "$parameter": [{ "affects": [["Cavalry"]], "multiply": $multiplier }],
    }, playerEnt);
})()
