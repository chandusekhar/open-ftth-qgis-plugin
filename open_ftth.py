# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenFtth
                                 A QGIS plugin
 QGIS plugin for open ftth
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-02-12
        git sha              : $Format:%H$
        copyright            : (C) 2020 by DAX ApS
        email                : jesper@dax.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QUrl
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction
from .resources import *
from .quick_edit_map_tool import QuickEditMapTool

# Import the code for the DockWidget
from .open_ftth_dockwidget import OpenFtthDockWidget
import os.path


class OpenFtth:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.map_canvas = iface.mapCanvas()
        self.map_tool = QuickEditMapTool(self.map_canvas)

        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OpenFtth_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Open Ftth')
        self.toolbar = self.iface.addToolBar(u'OpenFtth')
        self.toolbar.setObjectName(u'OpenFtth')

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OpenFtth', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/open_ftth/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Open Ftth'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False
        self.map_tool.identified.disconnect(self.onIdentified)
        self.map_canvas.setSelectionColor(QColor('red'))
        self.iface.activeLayer().removeSelection()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Open Ftth'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget == None:
                self.dockwidget = OpenFtthDockWidget()

            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            self.map_canvas.setMapTool(self.map_tool)
            self.map_tool.identified.connect(self.onIdentified)
            self.map_canvas.setSelectionColor(QColor('green'))


    def loadUrl(self, url):
        self.dockwidget.webView.setUrl(QUrl((url)))

    def onIdentified(self, selected_layer, selected_feature):
        selected_layer.removeSelection()
        selected_feature_id = selected_feature.attribute('Id')
        selected_layer.select(selected_feature.id())

