import os, subprocess
from PyQt4 import QtGui, QtCore, uic
from coreservices import prodmanUtils as pmu
from rapfile import assetutils
from rapfile.rapfilemgr import RapFileMgr
from coreservices.contexts import daniContext
from shotpublish import pipelineUtils
import msg
import danibb


class LightingObrTask(QtCore.QRunnable):

    def __init__(self, seq, shot, mem=56, spp=32, waves=8, xgen=True,
                 xfilter=True, fml=True, mb=True, dof=True, maxVolumeWaves=1,
                 frames="", pool=None, halfRes=True, dirName=None):
        super(LightingObrTask, self).__init__()
        self.seq = seq
        self.shot = shot
        self.mem = mem 
        self.spp = spp
        self.waves = waves 
        self.xfilter = xfilter 
        self.fml = fml 
        self.mb = mb 
        self.pool = pool
        self.dof = dof
        self.frames = frames
        self.xgen = xgen
        self.maxVolumeWaves = maxVolumeWaves
        self.halfRes = halfRes
        self.shotDir = dirName

    def run( self ):
        cmd = 'lighting_obr %(seq)s %(shot)s --memory %(mem)i --setSPP %(spp)i --setWave %(waves)i --maxVolumeWaves %(maxVolumeWaves)i --crossfilter %(xfilter)i ' % self.__dict__
        cmd = cmd.split()
        if self.fml:
            cmd.append("--fml")
        if not self.mb:
            cmd.append("--noMB")
        if not self.dof:
            cmd.append("--noDoF")
        if self.pool:
            cmd.extend(["--pool", self.pool])
        if self.frames:
            framesStr = "%s" % self.frames
            cmd.extend(["--frameRange", framesStr])
        if not self.xgen:
            cmd.append("--noXgen")
        if self.halfRes:
            cmd.append("--halfRes")
        msg.postStatus("Sending OBR for %(seq)s-%(shot)s" % self.__dict__)
        with daniContext.changeDani(self.shotDir):
            dbb = danibb.readIntoDict()
            subprocess.check_call(cmd)


class LightingObrDialog(QtGui.QDialog):


    def __init__( self, parent=None ):
        super(LightingObrDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'lighting_obr_gui.ui'), self)

        self.setWindowModality(QtCore.Qt.WindowModal)

        self._pool = QtCore.QThreadPool()
        self._pool.setMaxThreadCount(4)

        self._dbb = danibb.readIntoDict()
        self._show = self._dbb["d_show_name"]
        self._seq = self._dbb.get("d_seq_name", "")

        try:
            dept = ""
            dept = self._dbb["d_seq_dept_name"]
            dept  = self._dbb["d_shot_dept_name"]
        except KeyError:
            pass
        finally:
            self._dept = dept

        self.seqComboBox.currentIndexChanged.connect(self.updateShots)
        self.showOOPBox.stateChanged.connect(self.updateSeqs)
        self.accepted.connect(self.renderSelectedShots)

        self.updateSeqs()


    def updateSeqs( self ):
        seq = self.seqComboBox.currentText() or self._seq
        self.seqComboBox.clear()
        showOOP = self.showOOPBox.isChecked()
        seqs = pmu.getSequenceList(OOP=showOOP)
        seqs.sort()
        self.seqComboBox.insertItems(0, seqs)
        idx = self.seqComboBox.findText(self._seq)
        if idx != -1:
            self.seqComboBox.setCurrentIndex(idx)


    def updateShots( self ):
        
        def isPublished( shot ):
            shotRapfile = msg.defrcvr.iStockroom.getShotPath(seq, shot)
            return os.path.exists(shotRapfile)

        self.shotList.clear()
        showOOP = self.showOOPBox.isChecked()
        seq = self.seqComboBox.currentText()
        if seq:
            seq = str(seq)
            shots = filter(isPublished, pmu.getShotList(seq, OOP=showOOP))
            shots.sort()
            self.shotList.insertItems(0, shots)


    def renderSelectedShots(self):
        seq = str(self.seqComboBox.currentText())
        if not seq:
            msg.postWarning("No sequence selected")
            return

        shots = self.shotList.selectedItems()
        if not shots:
            msg.postWarning("No shots selected")
            return

        fml = self.fmlBox.isChecked()
        frames = str(self.framesEdit.text()) if not fml else ""
        xfilter = int(self.xfilterBox.isChecked())
        mb = self.mbBox.isChecked()
        dof = self.dofBox.isChecked()
        mem = self.memBox.value() * 1024
        waves = self.wavesBox.value()
        spp = self.sppBox.value()
        xgen = self.xgenBox.isChecked()
        maxVolumeWaves = self.maxVolumes.value()
        halfRes = self.resolutionCheckBox.isChecked()
        codaPool = self._dept if (self._dept and self._dept != "lighting") else None
        isFoundation = self.foundationCheckBox.isChecked()
        if isFoundation:
            deptName = "foundation"
        else:
            deptName = self._dept

        for i, shot in enumerate(shots):
            shot = str(shot.text())
            shotDir = os.path.join(pipelineUtils.getShotWorkDir(seq, shot, "Sequences"), deptName)
            worker = LightingObrTask(seq, shot, mem, spp, waves, xgen,
                                     xfilter, fml, mb, dof, maxVolumeWaves, frames,
                                     pool=codaPool, halfRes=halfRes, dirName=shotDir)
            self._pool.start(worker)

        self._pool.waitForDone()
        msg.postStatus("all jobs sent")



def lighting_obr_gui():
    dialog = LightingObrDialog()
    dialog.exec_()

