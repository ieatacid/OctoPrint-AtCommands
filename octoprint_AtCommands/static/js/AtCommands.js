/*
 * View model for OctoPrint-AtCommands
 *
 * Author: ieatacid
 * License: AGPLv3
 */
$(function() {
    function AtCommandsViewModel(parameters) {
        var self = this;

        self.global_settings = parameters[0];

        self.at_commands = ko.observableArray();

        self.addAtCommand = function() {
            self.at_commands.push({atName:"", type:"", command:""});
        };

        self.removeAtCommand = function(definition) {
            self.at_commands.remove(definition);
        };

        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.AtCommands;
            self.at_commands(self.settings.at_commands.slice(0));
        };

        self.onSettingsBeforeSave = function () {
            self.global_settings.settings.plugins.AtCommands.at_commands(self.at_commands.slice(0));
        };
    }

    OCTOPRINT_VIEWMODELS.push([
        AtCommandsViewModel,
        [ "settingsViewModel" ],
        [ "#settings_plugin_AtCommands" ]
    ]);
});
