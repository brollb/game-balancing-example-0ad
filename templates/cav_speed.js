var cmpPlayerManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_PlayerManager);
var playerEnt = cmpPlayerManager.GetPlayerByID('1');
let cmpModifiersManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_ModifiersManager);
cmpModifiersManager.AddModifiers("cheat/superfast", {
    "Attack/Ranged/Damage/Pierce": [{ "affects": [["Cavalry"]], "multiply": $speed_multiplier }],
}, playerEnt);
