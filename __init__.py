'''
Copyright (C) 2020 Samuel Bernou
bernou.samuel@gmail.com

Created by Samuel Bernou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Quick render",
    "description": "Quickly Render/openGL from view/cam and save image",
    "author": "Samuel Bernou",
    "version": (1, 2, 1),
    "blender": (2, 82, 0),
    "location": "3D viewport > sidebar (N) > View tab > Quick render",
    "warning": "",
    "tracker_url": "https://github.com/Pullusb/Quick_render/issues/new",
    "category": "3D View" }


import bpy
import os, re
from os import listdir
from pathlib import Path
from os.path import join, dirname, basename, exists, isfile, isdir, splitext, normpath
from time import strftime
from sys import platform
import subprocess


def get_addon_prefs():
    '''
    function to read current addon preferences properties

    access a prop like this :
    prefs = get_addon_prefs()
    option_state = prefs.super_special_option

    oneliner : get_addon_prefs().super_special_option
    '''
    import os 
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)

def set_collection(ob, collection, unlink=True) :
    ''' link an object in a collection and create it if necessary, if unlink object is removed from other collections'''
    scn     = bpy.context.scene
    col     = None
    visible = False
    linked  = False

    # check if collection exist or create it
    for c in bpy.data.collections :
        if c.name == collection : col = c
    if not col : col = bpy.data.collections.new(name=collection)

    # link the collection to the scene's collection if necessary
    for c in scn.collection.children :
        if c.name == col.name : visible = True
    if not visible : scn.collection.children.link(col)

    # check if the object is already in the collection and link it if necessary
    for o in col.objects :
        if o == ob : linked = True
    if not linked : col.objects.link(ob)

    # remove object from scene's collection
    for o in scn.collection.objects :
        if o == ob : scn.collection.objects.unlink(ob)

    # if unlink flag we remove the object from other collections
    if unlink :
        for c in ob.users_collection :
            if c.name != collection : c.objects.unlink(ob)


def openFolder(folderpath):
    """
    open the folder at the path given
    with cmd relative to user's OS
    """
    myOS = platform
    if myOS.startswith('linux') or myOS.startswith('freebsd'):
        # linux
        cmd = 'xdg-open'
        #print("operating system : Linux")
    elif myOS.startswith('win'):
        # Windows
        #cmd = 'start '
        cmd = 'explorer'
        #print("operating system : Windows")
        if not folderpath:
            return('/')
        
    else:#elif myOS == "darwin":
        # OS X
        #print("operating system : MACos")
        cmd = 'open'

    if not folderpath:
        return('//')

    # to prevent bad path string use normpath: 
    folderpath = os.path.normpath(folderpath)

    fullcmd = [cmd, folderpath]
    print(fullcmd)
    subprocess.Popen(fullcmd)
    return ' '.join(fullcmd)#back to string to return and print

def view3d_find():
    for area in bpy.data.window_managers[0].windows[0].screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    return area, region, rv3d
    return None, None, None

def get_view_origin_position():
    '''get view vector location (or matrix)'''
    ## method 1
    # from bpy_extras import view3d_utils
    # region = bpy.context.region
    # rv3d = bpy.context.region_data
    # view_loc = view3d_utils.region_2d_to_origin_3d(region, rv3d, (region.width/2.0, region.height/2.0))
    # print("view_loc1", view_loc)#Dbg

    ## method 2
    r3d = bpy.context.space_data.region_3d
    view_loc2 = r3d.view_matrix.inverted()#.translation
    # print("view_loc2", view_loc2)#Dbg

    return view_loc2


def create_cam_at_view(name):
    '''Instanciate a camera at viewpoint and render'''
    warn = []
    cam = bpy.context.scene.camera
    
    area = bpy.context.area
    region = bpy.context.region
    # w, h = region.width, region.height
    
    rv3d = bpy.context.region_data
    view_matrix = rv3d.view_matrix.inverted()
    # view_matrix = get_view_origin_position()
    print(f'is_perspective : {rv3d.is_perspective}')
    print(f'perspective : {rv3d.view_perspective}')

    
    mode = 'free'
    
    '''Check if already in a cam view...# Not woking, don't know how to check if in cam !
    if cam:
        print('cam: ', cam.name)
        cam_matrix = cam.matrix_world

        ### CHECK if in cam view (must be a prop...)!
        if view_matrix == cam_matrix:
            # print('In camera view')
            mode = 'cam'
            # Just render classic and return
            bpy.ops.render.render(animation=False, write_still=True)
            return
    '''
    # print("in free navigation")
    
    lens = area.spaces[0].lens
    if cam:
        if cam.data.lens != lens:
            warn.append(f'Different Focal length for active camera ({cam.data.lens}) and view ({lens})')
    
    #create new cam
    camdata = bpy.data.cameras.new('quickcam_'+ name)
    qcam = bpy.data.objects.new(name, camdata)
    # bpy.context.scene.collection.objects.link(qcam)
    set_collection(qcam, 'quick_cams')
    
    qcam.matrix_world = rv3d.view_matrix.inverted()# In one session there was a bug where rotation was Ok but not translation...
    qcam.location = rv3d.view_matrix.inverted().to_translation()
    bpy.context.scene.camera = qcam

    # Add a camera with (copy active cam settings ? better copy USER VIEW SETTINGS)
    camdata.lens = lens #use viewer lens

    return warn

def ensure_delimiter(name):
    '''Return passed string with a trailing "_" if no ending delimiter found, else return unchanged'''
    if name == '': return name
    if not name.endswith(('.', '-', '_')):
        name += '_'
    return name

def remove_delimiter(name):
    return name.rstrip('._-')

def pad_count(match, count):#unused regex callback (dont know how to pass arg)
    return str(count).zfill(len(match.group(0)))

def add_count(name, count, pad = 2):
    '''
    return string with passed count
    if # found, use this padding to write the count
    '''
    if not '#' in name:
        return ensure_delimiter(name) + str(count).zfill(pad) #name(_)

    ### r'\#{1,10}'# all '#...' in string --- r'\#{1,10}(?!.*\#)' # only last '#...'
    ## return re.sub(r'\#{1,10}(?!.*\#)', pad_count(match, count), name) #oneliner : but how to pas argument to a function callback ??
    
    # long method
    repad = re.search(r'\#{1,10}(?!.*\#)', name)
    padsize = len(repad.group(0))
    new = re.sub(r'\#{1,10}(?!.*\#)', str(count).zfill(padsize), name)
    ## kill other '#' in name ?
    # new = re.sub(r'\#{1,10}', '', name)

    return new

class QRD_OT_render_view(bpy.types.Operator):
    bl_idname = "render.qv_render_ops"
    bl_label = "Quick view render"
    bl_description = "Render/openGL view/cam"
    bl_options = {"REGISTER"}

    rendermode : bpy.props.IntProperty()

    def execute(self, context):
        
        # NOTE : Can use unique ID with date format ! : strftime()
        pref = get_addon_prefs()
        # user pref option for later
        
        placeholder = pref.placeholder
        date_format = pref.timestring
        userpad = pref.padding
        mask_cams = pref.mask_cams

        C = bpy.context
        scn = scene = context.scene

        dest = context.scene.qrd_prop.savepath
        if not dest:
            foldername = 'quick_render'
            if bpy.data.is_saved:
                dest = join(dirname(bpy.data.filepath), foldername)
            else:
                # bpy.app.tempdir -> temporary dir use by this session only
                dest = join(context.preferences.filepaths.temporary_directory, foldername)
            if not exists(dest):
                os.mkdir(dest)

        dest = bpy.path.abspath(dest)

        name = context.scene.qrd_prop.filename
        if bpy.data.is_saved and context.scene.qrd_prop.use_blend_name:
            name = Path(bpy.data.filepath).stem

        if pref.normalize:
            name = name.replace(' ', '_')


        if not name and not scn.qrd_prop.insert_date and not scn.qrd_prop.insert_frame:
            name = 'view'

        if scn.qrd_prop.insert_date:
            name = ensure_delimiter(name) + strftime(date_format)

        if scn.qrd_prop.insert_frame:
            name = ensure_delimiter(name) + 'f' + str(scn.frame_current).zfill(4)

        
        fl = [splitext(i)[0] for i in listdir(dest)]

        filename = name#original output name

        ct = 1#skip 01 and go direct to 02 (option to force always add count, even on first. dont like it, you may want to name each of your export...)
            
        if '#' in name:#padded
            # always number this from the first
            filename = add_count(name, 1, pad = userpad)#first output name have number 1

        else:#not padded
            first = add_count(name, 1, pad = userpad)#skip 01 (if was manually renamed) 
            if first in fl:
                filename = first # if a 1 exists avoid exporting version 0 (without number)

        stop = 5000
        while filename in fl:
            ct += 1
            # filename = f'{name}_{str(ct).zfill(2)}'#simple version
            filename = add_count(name, ct, pad = userpad)
            
            if ct >= stop:#hard num limiter
                self.report({'ERROR'}, 'Reach Hardcoded limit of files to increment in this quick render directory')#WARNING, ERROR
                return {"CANCELLED"}
                # break

        fp = normpath(join(dest, filename))
        # print(filename)
        # print('fp: ', fp)


        org = scn.render.filepath
        scn.render.filepath = fp
        
        if self.rendermode == 0:#OGL view
            bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=True)

        elif self.rendermode == 1:#OGL CAM # always render as solid view... so better use view render mode...
            bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=False)
        
        
        elif self.rendermode == 2:
            warn = create_cam_at_view(filename)
            if warn:
                mess = '\n'.join(warn)
                self.report({'WARNING'}, mess)#WARNING, ERROR
            
            bpy.ops.render.render(animation=False, write_still=True)
            # bpy.ops.render.render(animation=False, write_still=True, use_viewport=True)#, layer="", scene=""
        
        elif self.rendermode == 3:
            bpy.ops.render.render(animation=False, write_still=True)#, layer="", scene=""
        
        qc_viewlayer_col = C.scene.view_layers['View Layer'].layer_collection.children.get('quick_cams')
        if mask_cams:
            if qc_viewlayer_col: qc_viewlayer_col.exclude = True
        #reset
        scn.render.filepath = org

        return {"FINISHED"}

class QRD_OT_open_export_folder(bpy.types.Operator):
    bl_idname = "render.qv_open_loc"
    bl_label = "Open export folder"
    bl_description = "Open the folder of file output"
    bl_options = {"REGISTER"}

    rendermode : bpy.props.IntProperty()

    def execute(self, context):
        C = context
        scn = scene = context.scene
        dest = context.scene.qrd_prop.savepath
        if not dest:
            foldername = 'quick_render'#define in user pref ?
            if bpy.data.is_saved:
                dest = join(dirname(bpy.data.filepath), foldername)
            else:
                # bpy.app.tempdir -> temporary dir use by this session only
                dest = join(bpy.context.preferences.filepaths.temporary_directory, foldername)
            """if not exists(dest):
                dest = dirname(dest)
            if not exists(dest):
                return {'CANCELLED'} """

        dest = bpy.path.abspath(dest)
        if not exists(dest):
            dest = dirname(dest)
            mess = f'Not exists {dest}'
            self.report({'WARNING'}, mess)#WARNING
        
        if not exists(dest):#open parent folder (tolerance mode)
            mess = f'Not exists {dest}'
            self.report({'ERROR'}, mess)#WARNING, ERROR
            return {"CANCELLED"}

        openFolder(dest)        

        return {"FINISHED"}


class QRD_PT_quickrenderbuttons(bpy.types.Panel):
    bl_idname = "QRD_PT_quickpanel"
    bl_label = "Quick render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"

    def draw(self, context):
        layout = self.layout
        #layout.use_property_split = True#send properties to the right side
        # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        #row = layout.split(align=True,percentage=0.5)

        layout.prop(context.scene.qrd_prop, 'savepath', text='Save Folder')
        
        col = layout.column()
        col.prop(context.scene.qrd_prop, 'filename', text='File Name')
        col.enabled = not context.scene.qrd_prop.use_blend_name

        layout.prop(context.scene.qrd_prop, 'use_blend_name')

        row = layout.row(align=False)
        row.prop(context.scene.qrd_prop, 'insert_date')
        row.prop(context.scene.qrd_prop, 'insert_frame')

        layout.label(text='OpenGL render')
        row = layout.row(align=False)
        row.operator("render.qv_render_ops", text='openGl view', icon='RENDER_STILL').rendermode = 0
        # row.operator("render.qv_render_ops", text='openGl cam', icon='RESTRICT_RENDER_OFF').rendermode = 1# openGL forced trough cam Always appear as solid... remove button for now

        layout = self.layout
        layout.label(text='Render')
        row = layout.row(align=False)
        row.operator("render.qv_render_ops", text='render view', icon='RENDER_STILL').rendermode = 2
        row.operator("render.qv_render_ops", text='render cam', icon='OUTLINER_OB_CAMERA').rendermode = 3
        layout.separator()
        layout.operator("render.qv_open_loc", icon='OUTPUT')#text='render cam', FILE_FOLDER, OUTPUT (print like images)


class QRD_addon_pref(bpy.types.AddonPreferences):
    bl_idname = __name__
    #some_bool_prop to display in the addon pref

    normalize : bpy.props.BoolProperty(
        name='Normalize filename (space to underscore)',
        description="convert any space in filename to '_'",
        default=True)

    mask_cams : bpy.props.BoolProperty(
        name='Mask generated cameras',
        description="Disable the 'quick_cams' collection when a camera is generated to render a view",
        default=True)

    padding : bpy.props.IntProperty(
        name="number padding", 
        description="Padding number to use when filename already exists (ex: 2 = view_05, 3 = view_005)", 
        default=2, min=1, max=6, soft_min=1, soft_max=4, step=1)

    placeholder : bpy.props.StringProperty(
        name="placeholder", 
        description="filename to use when nothing is specified in UI filename field\nHint: This field empty with 'insert date' enabled will write date only", 
        default="view")

    timestring : bpy.props.StringProperty(
        name="date  format", 
        description="define a specific time format for the date string", 
        default="%Y-%m-%d_%H-%M-%S")

    def draw(self, context):
            layout = self.layout

            ## some 2.80 UI options
            layout.use_property_split = True
            flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)
            layout = flow.column()
            
            layout.prop(self, "placeholder")
            layout.separator()
            layout.prop(self, "padding")
            layout.separator()
            layout.prop(self, "mask_cams")
            layout.separator()
            layout.prop(self, "normalize")
            layout.separator()
            layout.prop(self, "timestring")
            layout.label(text='Date format is defining how to write current time, exemples:')
            # layout.label(text='')
            layout.label(text='%Y-%m-%d_%H-%M-%S (default)')
            layout.label(text='2020-03-02_23-19-55 (year-month-day_hour-min-seconds)')
            layout.separator()
            layout.label(text='%Y-%m-%d')
            layout.label(text='2020-03-02 (year-month-day)')
            layout.separator()
            layout.label(text='%d-%H-%M-%S')
            layout.label(text='02-23-19-55 (day-hours-minutes-seconds)')
            layout.separator()
            layout.label(text='%Y%m%d%H%M%S')
            layout.label(text='20200302231955 (compacted year,month,day,hours,minutes,seconds)')
            layout.separator()
            layout.operator("wm.url_open", text="Link to more detail on time format").url = "https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes"


class QRD_PGT_settings(bpy.types.PropertyGroup) :

    # (use template set in your user preferences)
    filename : bpy.props.StringProperty(
        description="The filename used for export. You can leave it empty\nYou can specify padding e.g: flashrender_###")

    use_blend_name : bpy.props.BoolProperty(
        name="Use Blend Name", default=False, description="Use current blend filename for export")

    # change defaut name in user_preferences
    savepath : bpy.props.StringProperty(
        subtype='DIR_PATH', 
        description="Export location, if not specify, create a 'quick_render' directory aside blend location")

    insert_date : bpy.props.BoolProperty(
        name="Insert Date", default=False, 
        description="Insert the date as suffix in filename\ne.g.: beloved-cube_2020-02-11")

    insert_frame : bpy.props.BoolProperty(
        name="Insert Frame", default=False, 
        description="Insert the frame number as suffix in filename\ne.g: beloved_cube_0250\n(or with date : beloved_cube_2020-02-11_0250)")

### register ===

classes = (
    QRD_PGT_settings,
    QRD_addon_pref,
    QRD_OT_render_view,
    QRD_PT_quickrenderbuttons,
    QRD_OT_open_export_folder
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.qrd_prop = bpy.props.PointerProperty(type = QRD_PGT_settings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.qrd_prop

if __name__ == "__main__":
    register()