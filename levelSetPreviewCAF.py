"""
Debug File: Loads the Preview-Caf from the temprel/latest/cafPreview area
"""
import os
import msg
from rapfilecore import assetutils

def addPreviewScene():
    """Adds the prviewcaf to the maya scene"""
    seq = os.getenv("NAV_SEQ")
    shot = os.getenv("NAV_SHOT")
    temprel = "<PATH GOES HERE>"
    path = "{0}/{1}/{2}/levelSetFiles/latest/cafPreview/".format(temprel, seq, shot)

    #Get Element
    scene = msg.defrcvr.iSceneMgr.getCurrentScene()
    elements = scene.getElements()
    masterSet = None
    namespacedName = ""
    for i in elements:
        if not i.getProperty("OOS"):
            if i.getName().endswith("Ocean"):
                #MasterSet
                namespacedName = i.getNamespace()
                if i.getNamespace().startswith("m_"):
                    masterSet = True
                    namespace, elementName = namespacedName.split(".")

                else:
                    elementName = i.getName()

    if masterSet:
        elementFullName = "{0}:{1}:{0}_{0}_{1}.caf".format(namespace, elementName, seq, shot)

    else:
        elementFullName = "{0}:_{0}_{1}.caf".format(elementName, seq, shot)


    cafPath = os.path.join(path, elementFullName)
    print cafPath

    if not os.path.isfile(cafPath):
        msg.postWarning("There is no levelSetCache - Caf {0}".format(cafPath))
        return
    else:
        msg.postStatus("Loading - Caf {0}".format(cafPath))

    elem = assetutils.findAssetByNamespace(scene, namespacedName)

    currentVariant = elem.getVariant()
    elem.setLoadFile(cafPath, variant=currentVariant, varProp='preview')
    elem.setLoadFileValue('preview')
    elem = assetutils.findAssetByNamespace(scene, namespacedName)

    #Invoke Refresh
    elem.setProperty("drawMode", "Unloaded")
    elem.setProperty("drawMode", "Maya+Voodoo")
    msg.postStatus("Updated Preview Caf for element:  {0}".format(elem.getNamespace()))

addPreviewScene()
