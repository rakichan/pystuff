
import blurdev
import blurdev.gui
import os.path
import re
from PIL import Image
from MtlGear.gui import plugin
from blur3d.gui import WaitCursor
from studio.gui.resource.icons import Icons
from Py3dsMax import mxs
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
	QWidget,
	QTreeWidgetItem,
	QColor,
	QApplication,
	QMessageBox,
	QFileDialog,
)

__pluginClasses__ = [
	'BitmapTrackerWidget',
]

# =============================================================================
# CLASSES
# =============================================================================

class RepathMapsDialog(blurdev.gui.Dialog):
	def __init__(self, items, *args, **kwargs):
		super(RepathMapsDialog, self).__init__(*args, **kwargs)
		blurdev.gui.loadUi(__file__, self, 'repathmapsdialog')
		self.uiBrowseBTN.setIcon(Icons.getIcon('folder-search-result'))
		self.uiBrowseBTN.released.connect(self._browseDirectory)
		self.uiChangeRDO.toggled.connect(self._toggleChange)
		self.uiFindRDO.toggled.connect(self._toggleFind)
		self.uiFindReplaceWID.setHidden(True)
		self._items = items

	@property
	def items(self):
		return self._items

	def accept(self, *args, **kwargs):
		if self.uiChangeRDO.isChecked():
			targetDir = unicode(self.uiDirectoryLINE.text())
			if not targetDir or not os.path.exists(targetDir):
				QMessageBox.critical(
					self,
					'Repath Failed',
					'Requested target directory does not exist.',
					QMessageBox.Ok,
					QMessageBox.NoButton,
				)
				return self.reject()
			with WaitCursor():
				for item in self.items:
					item.changeMapDirectory(targetDir)
		else:
			find = unicode(self.uiFindLINE.text())
			replace = unicode(self.uiReplaceLINE.text())
			if find:
				with WaitCursor():
					for item in self.items:
						item.findReplacePath(find, replace)
			else:
				return self.reject()
		return super(RepathMapsDialog, self).accept(*args, **kwargs)

	def _browseDirectory(self):
		dirPath = QFileDialog.getExistingDirectory(
			self,
			'Choose a Directory',
			os.path.dirname(self.items[0].mapPath),
		)
		if dirPath:
			self.uiDirectoryLINE.setText(dirPath)

	def _toggleChange(self, state):
		self.uiChangeWID.setHidden(not state)

	def _toggleFind(self, state):
		self.uiFindReplaceWID.setHidden(not state)

# =============================================================================

class BitmapTreeWidgetItem(QTreeWidgetItem):
	def __init__(self, bitmap, *args, **kwargs):
		super(BitmapTreeWidgetItem, self).__init__(*args, **kwargs)
		self._bitmap = bitmap
		self._mapPath = self._mapPathFromNode(bitmap)
		if mxs.iskindof(bitmap, mxs.vrayhdri):
			self.setIcon(0, Icons.getIcon('vray'))
		else:
			self.setIcon(0, Icons.getIcon('3dsmax-huge'))

	@property
	def bitmap(self):
		return self._bitmap

	@property
	def mapPath(self):
		return self._mapPath

	def changeMapDirectory(self, targetDir):
		base = os.path.basename(self.mapPath)
		newPath = os.path.join(targetDir, base)
		if mxs.classof(self.bitmap) == mxs.vrayhdri:
			self.bitmap.HDRIMapName = newPath
		else:
			if mxs.isProperty(self.bitmap, 'bitmap') and self.bitmap.bitmap:
				mxs.free(self.bitmap.bitmap)
			self.bitmap.filename = newPath
	
	def raw_string(self, s):
		if isinstance(s, str):
			s = s.encode('string-escape')
		elif isinstance(s, unicode):
			s = s.encode('unicode-escape')
		return s

	def findReplacePath(self, find, replace):
		find = self.raw_string(find)
		replace = self.raw_string(replace)
		newPath = re.sub(find, replace, self.mapPath)
		if mxs.classof(self.bitmap) == mxs.vrayhdri:
			self.bitmap.HDRIMapName = newPath
		else:
			if mxs.isProperty(self.bitmap, 'bitmap') and self.bitmap.bitmap:
				mxs.free(self.bitmap.bitmap)
			self.bitmap.filename = newPath

	def reloadMap(self):
		# For vray loaders just resetting the the same map
		# triggers a reload.  For bitmaptex loaders we can
		# tell Max to free the bitmap and then trigger a
		# reload by resetting the file path to the same value.
		if mxs.classof(self.bitmap) == mxs.vrayhdri:
			self.bitmap.HDRIMapName = self.bitmap.HDRIMapName
		else:
			if mxs.isProperty(self.bitmap, 'bitmap') and self.bitmap.bitmap:
				mxs.free(self.bitmap.bitmap)
			self.bitmap.filename = self.bitmap.filename

	def replaceWithSolidColor(self):
		if not self.mapPath or not os.path.exists(self.mapPath):
			return
		i = Image.open(self.mapPath)
		h = i.histogram()
		r = h[0:256]
		g = h[256:256*2]
		b = h[256*2: 256*3]
		sr = sum(r)
		sg = sum(g)
		sb = sum(b)
		vrc = mxs.VRayColor()
		if sr != 0:
			vrc.red = float(sum(i*w for i, w in enumerate(r)) / sr) / 256.0
		else:
			vrc.red = 0.0
		if sg != 0:
			vrc.green = (sum(i*w for i, w in enumerate(g)) / sum(g)) / 256.0
		else:
			vrc.green = 0.0
		if sb != 0:
			vrc.blue = float(sum(i*w for i, w in enumerate(b)) / sum(b)) / 256.0
		else:
			vrc.blue = 0.0
		mxs.replaceInstances(self.bitmap, vrc)

	def _mapPathFromNode(self, node):
		if mxs.classof(node) == mxs.vrayhdri:
			return node.HDRIMapName
		return node.filename

# =============================================================================

class BitmapTrackerWidget(plugin.MtlGearPlugin):
	def __init__(self, *args, **kwargs):
		super(BitmapTrackerWidget, self).__init__(*args, **kwargs)
		blurdev.gui.loadUi(__file__, self, 'bitmaptrackerwidget')
		self.uiDeleteBTN.setIcon(Icons.getIcon('minus'))
		self.uiVrayBTN.setIcon(Icons.getIcon('vray'))
		self.uiRepathBTN.setIcon(Icons.getIcon('arrow-switch'))
		self.uiShowBTN.setIcon(Icons.getIcon('eye'))
		self.uiReloadBTN.setIcon(Icons.getIcon('arrow-circle-double'))
		self.uiAverageBTN.setIcon(Icons.getIcon('color-swatch'))
		self.uiFilterEDIT.textChanged.connect(self._filterTree)
		self.uiFilterCOMBO.currentIndexChanged.connect(self._filterTree)
		self.uiDeleteBTN.released.connect(self._deleteSelected)
		self.uiShowCOMBO.currentIndexChanged.connect(self.refresh)
		self.uiShowBTN.released.connect(self._showInMaterialEditor)
		self.uiVrayBTN.released.connect(self._convertSelectedToVray)
		self.uiRepathBTN.released.connect(self._repathMaps)
		self.uiReloadBTN.released.connect(self._reloadMaps)
		self.uiAverageBTN.released.connect(self._replaceWithSolidColor)
		self.uiBitmapsTREE.itemDoubleClicked.connect(self._checkAndPopulate)
		self.uiBitmapsTREE.sortItems(2, Qt.AscendingOrder)
		self._isPopulated = False

	def getIcon(self):
		return Icons.getIcon('painting')

	def getTitle(self):
		return 'Bitmap/HDRI Tracker'

	def refresh(self):
		with WaitCursor():
			self.uiBitmapsTREE.clear()
			if self._isPopulated:
				self.uiBitmapsTREE.setRootIsDecorated(True)
			else:
				self.uiBitmapsTREE.setRootIsDecorated(False)
				msg = 'Double click to populate map list!  This might take a few minutes.'
				defItem = QTreeWidgetItem([msg])
				defItem.setIcon(0, Icons.getIcon('exclamation'))
				defItem.isDefaultItem = True
				self.uiBitmapsTREE.addTopLevelItem(defItem)
				self.uiBitmapsTREE.setFirstItemColumnSpanned(defItem, True)
				return
			bitmaps = mxs.getClassInstances(mxs.bitmapTex, processChildren=True)
			bitmaps.extend(mxs.getClassInstances(mxs.VRayHDRI, processChildren=True))
			for bitmap in bitmaps:
				QApplication.processEvents()
				deps = mxs.refs.dependentNodes(bitmap)
				if mxs.classof(bitmap) == mxs.bitmapTex:
					filePath = bitmap.filename
				else:
					filePath = bitmap.HDRIMapName
				if self.uiShowCOMBO.currentIndex() == 1:
					if filePath and filePath != '':
						continue
				elif self.uiShowCOMBO.currentIndex() == 2:
					if filePath and filePath != '' and os.path.exists(filePath):
						continue
				elif self.uiShowCOMBO.currentIndex() == 3:
					if deps:
						continue
				elif self.uiShowCOMBO.currentIndex() == 4:
					if mxs.classof(bitmap) != mxs.vrayhdri:
						continue
				elif self.uiShowCOMBO.currentIndex() == 5:
					if mxs.classof(bitmap) != mxs.bitmaptex:
						continue
				dirname = ''
				basename = ''
				if filePath:
					dirname = os.path.dirname(filePath)
					basename = os.path.basename(filePath)
				mapItem = BitmapTreeWidgetItem(
					bitmap,
					['', bitmap.name, basename, dirname],
				)
				for obj in deps:
					objItem = QTreeWidgetItem(
						mapItem,
						['', obj.name, '', ''],
					)
					objItem.setFlags(Qt.ItemIsEnabled)
				self.uiBitmapsTREE.addTopLevelItem(mapItem)
				if not filePath or filePath == '' or not os.path.exists(filePath):
					mapItem.setTextColor(2, QColor(128, 0, 0))
					mapItem.setTextColor(3, QColor(128, 0, 0))
				if not deps:
					mapItem.setTextColor(1, QColor(128, 0, 0))
			self._filterTree()
			for i in range(self.uiBitmapsTREE.columnCount()):
				self.uiBitmapsTREE.resizeColumnToContents(i)

	def _checkAndPopulate(self, item):
		if not hasattr(item, 'isDefaultItem'):
			return
		self._isPopulated = True
		self.refresh()

	def _convertSelectedToVray(self):
		selectedItems = self.uiBitmapsTREE.selectedItems()
		bitmapItems = [i for i in selectedItems if mxs.classof(i.bitmap) == mxs.bitmaptex]
		if not bitmapItems:
			return
		title = 'Continue with conversion?'
		msg = 'Are you sure you want to convert the selected bitmaps to VrayHDRIs?'
		answer = QMessageBox.question(
			self,
			title,
			msg,
			QMessageBox.Ok,
			QMessageBox.Cancel,
		)
		if answer == QMessageBox.Ok:
			allConverted = True
			with WaitCursor():
				defaultBitmap = mxs.bitmaptex()
				propNames = mxs.getPropNames(defaultBitmap)
				skipProps = ['filename','alphaSource','bitmap']
				for item in bitmapItems:
					depPairs = plugin.getDirectDependencies(item.bitmap)
					bm = item.bitmap
					hdri = mxs.vrayhdri()
					hdri.hdriMapName = item.bitmap.fileName
					hdri.name = item.bitmap.name
					mxs.replaceInstances(hdri.uvgen, bm.coordinates)
					mxs.replaceInstances(hdri.output, bm.output)
					hdri.cropPlace_mode = bm.cropPlace
					hdri.cropPlace_width = bm.clipW
					hdri.cropPlace_height = bm.clipH
					hdri.cropPlace_u = bm.clipU
					hdri.cropPlace_v = bm.clipV
					hdri.rgbOutput = bm.rgbOutput
					hdri.monoOutput = bm.monoOutput
					hdri.alphaSource = bm.alphaSource
					hdri.iflStartFrame = bm.startTime
					hdri.iflPlaybackRate = bm.playbackRate
					hdri.iflEndCondition = bm.endCondition
					for dep, propNames in depPairs:
						for propName in propNames:
							dep.setProperty(propName, hdri)
					mxs.free(item.bitmap)
				self.refresh()
			if allConverted:
				msg = 'All selected bitmaps have been converted to VrayHDRI.'
			else:
				msg = 'Some bitmaps were not converted because they had changes that would not translate.'
			QMessageBox.information(
				self,
				'Conversion Complete',
				msg,
				QMessageBox.Ok,
				QMessageBox.NoButton,
			)

	def _deleteSelected(self):
		title = 'Continue with deletion?'
		msg = 'Are you sure you want to delete the selected bitmaps?'
		answer = QMessageBox.question(
			self,
			title,
			msg,
			QMessageBox.Ok,
			QMessageBox.Cancel,
		)
		if answer == QMessageBox.Ok:
			with WaitCursor():
				mxs.MatEditor.Close()
				for item in self.uiBitmapsTREE.selectedItems():
					bitmap = item.bitmap
					if mxs.classof(bitmap) == mxs.bitmapTex:
						bitmap.filename = ''
					else:
						bitmap.HDRIMapName = ''
					# Not much else we can do if this fails, so we'll
					# let it continue on.  At least we emptied out the
					# path, right?
					try:
						mxs.blur3dhelper.removeBitmapSubs(item.bitmap)
					except RuntimeError:
						pass
			self.refresh()

	def _filterTree(self):
		match = str(self.uiFilterEDIT.text())
		match = match.replace('*', '.*')
		if match == '.*':
			prog = re.compile(match, re.IGNORECASE)
		else:
			prog = re.compile(
				'{start}{match}{end}'.format(
					start='.*',
					match=match,
					end='.*'
				),
				re.IGNORECASE
			)
		column = (self.uiFilterCOMBO.currentIndex() + 1)
		for index in range(self.uiBitmapsTREE.topLevelItemCount()):
			item = self.uiBitmapsTREE.topLevelItem(index)
			if prog.match(item.text(column)):
				item.setHidden(False)
			else:
				item.setHidden(True)
		for i in range(self.uiBitmapsTREE.columnCount()):
			self.uiBitmapsTREE.resizeColumnToContents(i)

	def _reloadMaps(self):
		selection = self.uiBitmapsTREE.selectedItems()
		if not selection:
			return
		with WaitCursor():
			for item in selection:
				item.reloadMap()
		QMessageBox.information(
			self,
			'Reload Complete',
			'Selected maps have been successfully reloaded.',
			QMessageBox.Ok,
			QMessageBox.NoButton,
		)

	def _repathMaps(self):
		selection = self.uiBitmapsTREE.selectedItems()
		if not selection:
			return
		dialog = RepathMapsDialog(selection, self)
		if dialog.exec_():
			self.window().refresh()

	def _replaceWithSolidColor(self):
		selection = self.uiBitmapsTREE.selectedItems()
		if not selection:
			return
		ret = QMessageBox.question(
			self,
			'Continue?',
			'This will replace all instances of the selected maps with VRayColors.  Continue?',
			QMessageBox.Yes,
			QMessageBox.No,
		)
		if ret:
			with WaitCursor():
				failed = []
				for item in selection:
					try:
						item.replaceWithSolidColor()
					except IOError:
						failed.append(item)
			self.window().refresh()
			if not failed:
				QMessageBox.information(
					self,
					'Success!',
					'All selected maps have been replaced.',
					QMessageBox.Ok,
					QMessageBox.NoButton,
				)
			else:
				QMessageBox.warning(
					self,
					'Some Replacements Failed',
					'The following could not be converted:\n\n{}'.format(
						'\n'.join([i.mapPath for i in failed]),
					),
					QMessageBox.Ok,
					QMessageBox.NoButton,
				)

	def _showInMaterialEditor(self):
		items = self.uiBitmapsTREE.selectedItems()
		if not items:
			return
		mxs.setMeditMaterial(1, items[0].bitmap)
		mxs.activeMeditSlot = 1
		mxs.MatEditor.Open()






