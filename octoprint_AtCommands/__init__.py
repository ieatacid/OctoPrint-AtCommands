# coding=utf-8
from __future__ import absolute_import


import octoprint.plugin
import octoprint.settings
import logging
import subprocess
import sys

class AtCommandsPlugin(octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.TemplatePlugin):


    def __init__(self):
        self.at_commands = {}

    def on_settings_initialized(self):
        self.reload_at_commands()

    def reload_at_commands(self):
        self.at_commands = {}

        at_commands_tmp = self._settings.get(["at_commands"])
        self._logger.debug("at_commands: %s" % at_commands_tmp)

        for definition in at_commands_tmp:
            self.at_commands[definition['atName']] = dict(type=definition['type'], command=definition['command'])
            self._logger.info("Add AtCommand '@%s' = %s" % (definition['atName'], definition['command']))

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_at_commands()

    def get_settings_defaults(self):
        return dict(
            at_commands = []
        )

    def get_template_configs(self):
        return [
            dict(type="settings", name="At Commands", custom_bindings=True)
        ]

    def get_assets(self):
        return dict(
            js=["js/AtCommands.js"]
        )

    def get_update_information(self):
        return dict(
            AtCommands=dict(
                displayName="AtCommands Plugin",
                displayVersion=self._plugin_version,

                type="github_release",
                user="ieatacid",
                repo="OctoPrint-AtCommands",
                current=self._plugin_version,

                pip="https://github.com/ieatacid/OctoPrint-AtCommands/archive/{target_version}.zip"
            )
        )

    def atcommand_hook(self, comm, phase, command, parameters, tags=None, *args, **kwargs):
        if command == None:
            return
        else:
            try:
                at_cmd = self.at_commands[command]
                self._logger.info("Command found for '@%s'" % (command))
            except:
                self._logger.error("No command found for '@%s'" % command)
                return (None,)

        if tags is None:
            tags = set()

        self._logger.info("atcommand_hook-> command: %s, parameters: %s, tags: %s" % (command, parameters, tags))

        if at_cmd["type"] == "system":
            self._logger.info("AtCommand '@%s' is type 'system'" % (command))
            self._logger.info("Executing system command '%s'" % (at_cmd["command"]))
            try:
            	if len(parameters) > 0:
            		self._logger.info("...with parameters: %s" % (parameters))
            		r = subprocess.call([at_cmd["command"], parameters])
            	else:
                	r = subprocess.call(at_cmd["command"])
            except:
                e = sys.exc_info()[0]
                self._logger.exception("Error executing command '%s'" % (command))
                return (None,)

            self._logger.info("Command '%s' returned: %s" % (command, r))

        elif at_cmd["type"] == "gcode":
            self._logger.info("AtCommand '@%s' is type 'gcode'" % (command))
            self._logger.info("Executing octoprint command '%s'" % (at_cmd["command"]))
            self._printer.commands(this_command["command"].split(";"))

        else:
            self._logger.error("AtCommand type not found or not known for '@%s'" % command)
            return (None)

        # from terminal:             set(['trigger:printer.commands', 'api:printer.command', 'source:api'])
        # from oprint start gcode:  set(['script:beforePrintStarted', 'source:script', 'source:job', 'trigger:printer.script', 'trigger:comm.send_gcode_script'])
        # from gcode file:             set(['fileline:1', 'source:file', 'filepos:5923'])


__plugin_name__ = "AtCommands"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = AtCommandsPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.atcommand.queuing": __plugin_implementation__.atcommand_hook
    }

