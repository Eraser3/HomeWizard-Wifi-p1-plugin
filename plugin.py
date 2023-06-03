##           HomeWizard Wi-Fi P1 Meter Plugin
##
##           Author:         Eraser
##           Version:        1.0.1
##           Last modified:  31-05-2023
##
"""
<plugin key="HomeWizardWifiP1Meter" name="HomeWizard Wi-Fi P1 Meter" author="Eraser" version="1.0.1" externallink="https://www.homewizard.nl/p1-meter">
    <description>
        
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1" />
        <param field="Port" label="Port" width="200px" required="true" default="80" />
        <param field="Mode1" label="Data interval" width="200px">
            <options>
                <option label="10 seconds" value="10"/>
                <option label="20 seconds" value="20"/>
                <option label="30 seconds" value="30"/>
                <option label="1 minute" value="60" default="true"/>
                <option label="2 minutes" value="120"/>
                <option label="3 minutes" value="180"/>
                <option label="4 minutes" value="240"/>
                <option label="5 minutes" value="300"/>
            </options>
        </param>
        <param field="Mode3" label="Usage value (Watt)" width="100px" required="false" default="0" />
        <param field="Mode4" label="Production value (Watt)" width="100px" required="false" default="0" />
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import urllib
import urllib.request

class BasePlugin:
    #Plugin variables
    pluginInterval = 10     #in seconds
    dataInterval = 60       #in seconds
    dataIntervalCount = 0
    usageSwitchValue = 0
    productionSwitchValue = 0
    
    #Homewizard P1 meter variables
    wifi_strength = -1              #: [Number] De sterkte van het Wi-Fi signaal in %
    total_power_import_t1_kwh = -1  #: [Number] De stroom afname meterstand voor tarief 1 in kWh
    total_power_import_t2_kwh = -1  #: [Number] De stroom afname meterstand voor tarief 2 in kWh
    total_power_export_t1_kwh = -1  #: [Number] De stroom teruglevering meterstand voor tarief 1 in kWh
    total_power_export_t2_kwh = -1  #: [Number] De stroom teruglevering meterstand voor tarief 2 in kWh
    active_power_w = -1             #: [Number] Het huidig gebruik van alle fases gecombineerd in Watt
    active_power_l1_w = -1          #: [Number] Het huidig gebruik voor fase 1 in Watt (indien van toepassing)
    active_power_l2_w = -1          #: [Number] Het huidig gebruik voor fase 2 in Watt (indien van toepassing)
    active_power_l3_w = -1          #: [Number] Het huidig gebruik voor fase 3 in Watt (indien van toepassing)
    active_voltage_l1_v = -1        #: [Number] Het huidige voltage voor fase 1 in volt (indien van toepassing)
    active_voltage_l2_v = -1        #: [Number] Het huidige voltage voor fase 2 in volt (indien van toepassing)
    active_voltage_l3_v = -1        #: [Number] Het huidige voltage voor fase 3 in volt (indien van toepassing)
    active_current_l1_a = -1        #: [Number] De huidige stroom voor fase 1 in ampere (indien van toepassing)
    active_current_l2_a = -1        #: [Number] De huidige stroom voor fase 2 in ampere (indien van toepassing)
    active_current_l3_a = -1        #: [Number] De huidige stroom voor fase 3 in ampere (indien van toepassing)
    total_gas_m3 = -1               #: [Number] De gas meterstand in m3
    gas_timestamp = -1              #: [Number] De datum en tijd van de meest recente gas meterstand gestructureerd als YYMMDDhhmmss.
    
    #Calculated variables
    total_power = 0                 #: Het totale gecombineerde vermogen.
    import_active_power_w = 0       #: Het huidig vermogen wat momenteel van het net wordt geimporteerd.
    export_active_power_w = 0       #: Het huidig vermogen wat momenteel naar het net wordt geexporteerd.
    
    #Device ID's
    active_power_id = 101
    total_power_id = 102
    active_power_l1_id = 105
    active_power_l2_id = 106
    active_power_l3_id = 107
    active_voltage_l1_id = 108
    active_voltage_l2_id = 109
    active_voltage_l3_id = 110
    active_current_l1_id = 111
    active_current_l2_id = 112
    active_current_l3_id = 113
    total_gas_id = 121
    switch_export_id = 130
    switch_export_value_id = 131
    switch_import_value_id = 132
    wifi_signal_id = 140
    
    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()
        
        # If data interval between 10 sec. and 5 min.
        if 10 <= int(Parameters["Mode1"]) <= 300:
            self.dataInterval = int(Parameters["Mode1"])
        else:
            # If not, set to 60 sec.
            self.dataInterval = 60
            
        # If usage switch value
        if isNumber(Parameters["Mode3"]) == True and 1 <= int(Parameters["Mode3"]) <= 999999:
            self.usageSwitchValue = int(Parameters["Mode3"])
        else:
            # If not, set to 0 (means off)
            self.usageSwitchValue = 0
            
        # If production switch value
        if isNumber(Parameters["Mode4"]) == True and 1 <= int(Parameters["Mode4"]) <= 999999:
            self.productionSwitchValue = int(Parameters["Mode4"])
        else:
            # If not, set to 0 (means off)
            self.productionSwitchValue = 0
        
        # Start the heartbeat
        Domoticz.Heartbeat(self.pluginInterval)
        
        return True
        
    def onConnect(self, Status, Description):
        return True

    def onMessage(self, Data, Status, Extra):
        try:
            Domoticz.Debug("Reading electricity values from input")
            
            self.wifi_strength = Data['wifi_strength']
            self.total_power_import_t1_kwh = int(Data['total_power_import_t1_kwh'] * 1000)
            self.total_power_import_t2_kwh = int(Data['total_power_import_t2_kwh'] * 1000)
            self.total_power_export_t1_kwh = int(Data['total_power_export_t1_kwh'] * 1000)
            self.total_power_export_t2_kwh = int(Data['total_power_export_t2_kwh'] * 1000)
            self.active_power_w = Data['active_power_w']
            
            if ( 'active_power_l1_w' in Data ): self.active_power_l1_w = Data['active_power_l1_w']
            if ( 'active_power_l2_w' in Data ): self.active_power_l2_w = Data['active_power_l2_w']
            if ( 'active_power_l3_w' in Data ): self.active_power_l3_w = Data['active_power_l3_w']
            if ( 'active_voltage_l1_v' in Data ): self.active_voltage_l1_v = float(Data['active_voltage_l1_v'])
            if ( 'active_voltage_l2_v' in Data ): self.active_voltage_l2_v = float(Data['active_voltage_l2_v'])
            if ( 'active_voltage_l3_v' in Data ): self.active_voltage_l3_v = float(Data['active_voltage_l3_v'])
            if ( 'active_current_l1_a' in Data ): self.active_current_l1_a = float(Data['active_current_l1_a'])
            if ( 'active_current_l2_a' in Data ): self.active_current_l2_a = float(Data['active_current_l2_a'])
            if ( 'active_current_l3_a' in Data ): self.active_current_l3_a = float(Data['active_current_l3_a'])
            
            Domoticz.Debug("Reading gas values from input")
            
            #New version has room for multiple gas meters. We only monitor the first one if available.
            for external in Data['external']:
                if ( external['type'] == "gas_meter" ):
                    self.total_gas_m3 = int(external['value'] * 1000)
                    self.gas_timestamp = external['timestamp']
                    break
                
            Domoticz.Debug("Calculating active power")
            
            self.total_power = self.total_power_import_t1_kwh + self.total_power_import_t2_kwh - self.total_power_export_t1_kwh - self.total_power_export_t2_kwh
            
            if ( self.active_power_w >= 0 ):
                self.import_active_power_w = self.active_power_w
                self.export_active_power_w = 0
            else:
                self.import_active_power_w = 0
                self.export_active_power_w = self.active_power_w * -1
                
            #------- Power -------
            try:
                if ( self.active_power_id not in Devices ):
                    Domoticz.Device(Name="Current power usage",  Unit=self.active_power_id, Type=243, Subtype=29).Create()
                    
                #UpdateDevice(self.active_power_id, 0, numStr(self.active_power_w) + ";0", True)
                UpdateDevice(self.active_power_id, 0, numStr(self.active_power_w) + ";" + numStr(self.total_power), True)
            except:
                Domoticz.Error("Failed to update device id " + str(self.active_power_id))
            
            try:
                if ( self.total_power_id not in Devices ):
                    Domoticz.Device(Name="Total power usage",  Unit=self.total_power_id, Type=250, Subtype=1).Create()

                UpdateDevice(self.total_power_id, 0, numStr(self.total_power_import_t1_kwh) + ";" + numStr(self.total_power_import_t2_kwh) + ";" + numStr(self.total_power_export_t1_kwh) + ";" + numStr(self.total_power_export_t2_kwh) + ";" + numStr(self.import_active_power_w) + ";" + numStr(self.export_active_power_w), True)
            except:
                Domoticz.Error("Failed to update device id " + str(self.total_power_id))
            
            #------- Power per fase -------
            if ( self.active_power_l1_w > -1 ):
                try:
                    if ( self.active_power_l1_id not in Devices ):
                        Domoticz.Device(Name="Current phase-1 power usage",  Unit=self.active_power_l1_id, Type=243, Subtype=29).Create()
                        
                    UpdateDevice(self.active_power_l1_id, 0, numStr(self.active_power_l1_w) + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_power_l1_id))
                
            if ( self.active_power_l2_w > -1 ):
                try:
                    if ( self.active_power_l2_id not in Devices ):
                        Domoticz.Device(Name="Current phase-2 power usage",  Unit=self.active_power_l2_id, Type=243, Subtype=29).Create()
                        
                    UpdateDevice(self.active_power_l2_id, 0, numStr(self.active_power_l2_w) + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_power_l2_id))
                
            if ( self.active_power_l3_w > -1 ):
                try:
                    if ( self.active_power_l3_id not in Devices ):
                        Domoticz.Device(Name="Current phase-3 power usage",  Unit=self.active_power_l3_id, Type=243, Subtype=29).Create()
                        
                    UpdateDevice(self.active_power_l3_id, 0, numStr(self.active_power_l3_w) + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_power_l3_id))
                
            #------- Voltage per fase -------
            if ( self.active_voltage_l1_v > -1 ):
                try:
                    if ( self.active_voltage_l1_id not in Devices ):
                        Domoticz.Device(Name="Current phase-1 voltage",  Unit=self.active_voltage_l1_id, Type=243, Subtype=8).Create()
                        
                    UpdateDevice(self.active_voltage_l1_id, 0, f'{self.active_voltage_l1_v:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_voltage_l1_id))
                
            if ( self.active_voltage_l2_v > -1 ):
                try:
                    if ( self.active_voltage_l2_id not in Devices ):
                        Domoticz.Device(Name="Current phase-2 voltage",  Unit=self.active_voltage_l2_id, Type=243, Subtype=8).Create()
                        
                    UpdateDevice(self.active_voltage_l2_id, 0, f'{self.active_voltage_l2_v:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_voltage_l2_id))
            
            if ( self.active_voltage_l3_v > -1 ):            
                try:
                    if ( self.active_voltage_l3_id not in Devices ):
                        Domoticz.Device(Name="Current phase-3 voltage",  Unit=self.active_voltage_l3_id, Type=243, Subtype=8).Create()
                        
                    UpdateDevice(self.active_voltage_l3_id, 0, f'{self.active_voltage_l3_v:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_voltage_l3_id))
                    
            #------- Amperage per fase -------
            if ( self.active_current_l1_a > -1 ):
                try:
                    if ( self.active_current_l1_id not in Devices ):
                        Domoticz.Device(Name="Current phase-1 current",  Unit=self.active_current_l1_id, Type=243, Subtype=23).Create()
                        
                    UpdateDevice(self.active_current_l1_id, 0, f'{self.active_current_l1_a:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_current_l1_id))
                
            if ( self.active_current_l2_a > -1 ):
                try:
                    if ( self.active_current_l2_id not in Devices ):
                        Domoticz.Device(Name="Current phase-2 current",  Unit=self.active_current_l2_id, Type=243, Subtype=23).Create()
                        
                    UpdateDevice(self.active_current_l2_id, 0, f'{self.active_current_l2_a:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_current_l2_id))
            
            if ( self.active_current_l3_a > -1 ):            
                try:
                    if ( self.active_current_l3_id not in Devices ):
                        Domoticz.Device(Name="Current phase-3 current",  Unit=self.active_current_l3_id, Type=243, Subtype=23).Create()
                        
                    UpdateDevice(self.active_current_l3_id, 0, f'{self.active_current_l3_a:.3f}' + ";0", True)
                except:
                    Domoticz.Error("Failed to update device id " + str(self.active_current_l3_id))
            
            #------- Gas -------
            try:
                if ( self.total_gas_id not in Devices ):
                    Domoticz.Device(Name="Total gas",  Unit=self.total_gas_id, TypeName="Gas").Create()

                UpdateDevice(self.total_gas_id, 0, numStr(self.total_gas_m3), True)
            except:
                Domoticz.Error("Failed to update device id " + str(self.total_gas_id))
                
            try:
                if ( self.wifi_signal_id not in Devices ):
                    Domoticz.Device(Name="Wifi signal",  Unit=self.wifi_signal_id, TypeName="Percentage").Create()
                    
                UpdateDevice(self.wifi_signal_id, 0, numStr(self.wifi_strength), True)
            except:
                Domoticz.Error("Failed to update device id " + str(self.wifi_signal_id))
            
            #------- Switches -------
            
            try:
                if ( self.switch_export_id not in Devices ):
                    Domoticz.Device(Name="Production switch",  Unit=self.switch_export_id, TypeName="Switch").Create()
                    
                if ( self.export_active_power_w > 0 ):
                    UpdateDevice(self.switch_export_id, 1, "On")
                else:
                    UpdateDevice(self.switch_export_id, 0, "Off")
            except:
                Domoticz.Error("Failed to update device id " + str(self.switch_export_id))
                
            if ( self.productionSwitchValue > 0 ):
                try:
                    if ( self.switch_export_value_id not in Devices ):
                        Domoticz.Device(Name="Production value switch",  Unit=self.switch_export_value_id, TypeName="Switch").Create()
                        
                    if ( self.export_active_power_w >= self.productionSwitchValue ):
                        UpdateDevice(self.switch_export_value_id, 1, "On")
                    else:
                        UpdateDevice(self.switch_export_value_id, 0, "Off")
                except:
                    Domoticz.Error("Failed to update device id " + str(self.switch_export_value_id))
                    
            if ( self.usageSwitchValue > 0 ):
                try:
                    if ( self.switch_import_value_id not in Devices ):
                        Domoticz.Device(Name="Usage value switch",  Unit=self.switch_import_value_id, TypeName="Switch").Create()
                        
                    if ( self.import_active_power_w >= self.usageSwitchValue ):
                        UpdateDevice(self.switch_import_value_id, 1, "On")
                    else:
                        UpdateDevice(self.switch_import_value_id, 0, "Off")
                except:
                    Domoticz.Error("Failed to update device id " + str(self.switch_import_value_id))
        except:
            Domoticz.Error("Failed to read response data")
            return
           
        return True
                    
    def onCommand(self, Unit, Command, Level, Hue):
        #Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        return True

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        #Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)
        return

    def onHeartbeat(self):
        self.dataIntervalCount += self.pluginInterval
        
        #------- Collect data -------
        if ( self.dataIntervalCount >= self.dataInterval ):
            self.dataIntervalCount = 0
            self.readMeter()
        
        return

    def onDisconnect(self):
        return

    def onStop(self):
        #Domoticz.Log("onStop called")
        return True

    def readMeter(self):
        try:
            APIdata = urllib.request.urlopen("http://" + Parameters["Address"] + ":" + Parameters["Port"] + "/api/v1/data").read()
        except:
            Domoticz.Error("Failed to communicate with Wi-Fi P1 meter at ip " + Parameters["Address"] + " with port " + Parameters["Port"])
            return False
        
        try:
            APIjson = json.loads(APIdata.decode("utf-8"))
        except:
            Domoticz.Error("Failed converting API data to JSON")
            return False
            
        try:
            self.onMessage(APIjson, "200", "")
        except:
            Domoticz.Error("onMessage failed with some error")
            return False

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Description):
    global _plugin
    _plugin.onConnect(Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def numStr(s):
    try:
        return str(s).replace('.','')
    except:
        return "0"

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False, SignalLevel=12):    
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if ((Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (AlwaysUpdate == True)):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), SignalLevel=SignalLevel)
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return
