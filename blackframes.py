import os
import shutil
import subprocess
import tempfile

from coreservices.exr import BlackExr

import Imath

def create(paths, res_x, res_y, image_extension, channels=(), verbose=False,
           extra_meta=None):
    """create(paths, res_x, res_y, image_extension, channels=(), verbose=False)

    Create black (empty) images in the given resolution and image format at
    paths. Assumes current process has permission to write to each path
    specified in paths.


    The following only applies when creating an EXR image:

    channels: list of additional EXR channels that will be created for the
    black frame. 'R', 'G', 'B', 'A' and 'Z' are always written out.

    extra_meta: dictionary of additional metadata keys to write into the header

    """
    if isinstance(paths, str):
        raise ValueError("'paths' arg must be a list of paths")

#     # create a temp image in the correct resolution and format
    tmp_img = tempfile.mktemp(dir='/disk1/tmp', suffix='.'+image_extension)
    
    if image_extension.lower()=='exr':       
        dataWindow = Imath.Box2i(Imath.point(0 ,0),Imath.point(res_x-1,res_y-1))
        displayWindow = dataWindow
        
        
        all_channels = ['R', 'G', 'B', 'A', 'Z']
        all_channels.extend(channels)
        
        #Create a blank single part image with the right size and channels filled with black
        img = BlackExr(tmp_img,dataWindow,displayWindow,all_channels,metaData=extra_meta)
        img.write()

    else: 
        #non-exr case uses itconvert
        src_img = "PATH_DELETED FOR SECURITY PURPOSES.%s" % image_extension
        if not os.path.isfile(src_img):
            raise ValueError("No stock black image found for extension '%s'" % image_extension)
        cmd = ['itconvert', src_img, '-resize', str(res_x), str(res_y), '-o', tmp_img]
        subprocess.check_call(cmd)
        
        
    # copy that image to each of the specified paths
    try:
        for path in paths:
            if verbose:
                print "Creating", path
            shutil.copy(tmp_img, path)
    except:
        pass
    finally:
        os.remove(tmp_img)
