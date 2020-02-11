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
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D viewport > N bar > View tab > Quick render",
    "warning": "",
    "wiki_url": "https://github.com/Pullusb/Quick_render",
    "category": "3D View" }


import bpy
import os, re
from os import listdir
from os.path import join, dirname, basename, exists, isfile, isdir, splitext, normpath
from time import strftime
from sys import platform
import subprocess

# TODO :
# Store trigerred view history of each render (maybe with a unique ID number + auto name given) as UI list
# (exportable - loadable as json ?)
# add an option to create camera at current view (matrix)...

# This way the user can Go back to a view with history (if real/client/bossman thinks this export is cool) and place a cam on this view
# slightly overkill but I like it !

# quick options (addon prefs or 2/3 preset)

def openFolder(folderpath):
    """
    open the folder at the path given
    with cmd relative to user's OS
    """
    myOS = platform
    if myOS.startswith('linux') or myOS.startswith('freebsd'):
        # linux
        cmd = 'xdg-open '
        #print("operating system : Linux")
    elif myOS.startswith('win'):
        # Windows
        #cmd = 'start '
        cmd = 'explorer '
        #print("operating system : Windows")
        if not folderpath:
            return('/')
        
    else:#elif myOS == "darwin":
        # OS X
        #print("operating system : MACos")
        cmd = 'open '

    if not folderpath:
        return('//')

    # to prevent bad path string use normpath: 
    folderpath = os.path.normpath(folderpath)

    fullcmd = [cmd, folderpath]
    print(fullcmd)
    subprocess.Popen(fullcmd)
    return ' '.join(fullcmd)#back to string to return and print

def ensure_delimiter(name):
    '''Return passed string with a trailing "_" if no ending delimiter found, else return unchanged'''
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
        
        # NOTE : Can use unique ID with date format ! : strftime(%Y%m%d%H%M%S)

        # user pref option for later
        placeholder = "view"
        date_format = r"%Y-%m-%d"#year-month-day

        C = bpy.context
        scn = scene = context.scene

        dest = bpy.context.scene.qrd_savepath
        if not dest:
            foldername = 'quick_render'
            if bpy.data.is_saved:
                dest = join(dirname(bpy.data.filepath), foldername)
            else:
                # bpy.app.tempdir -> temporary dir use by this session only
                dest = join(bpy.context.preferences.filepaths.temporary_directory, foldername)
            if not exists(dest):
                os.mkdir(dest)

        dest = bpy.path.abspath(dest)

        name = bpy.context.scene.qrd_filename

        # Normalize (space to underscore) (TODO, make an option (user pref ?))
        name = name.replace(' ', '_')

        # date_format = r"%d-%H-%M"#-%S day, hours, minutes #seconds

        if not name:
            name = placeholder

        if scn.qrd_insert_date:
            name = ensure_delimiter(name) + strftime(date_format)

        if scn.qrd_insert_frame:
            name = ensure_delimiter(name) + str(scn.frame_current).zfill(4)

        
        fl = [splitext(i)[0] for i in listdir(dest)]

        filename = name#original output name

        ct = 1#skip 01 and go direct to 02 (option always add count, even on first ? I dont like it if you want to name each of your export...)
            
        if '#' in name:#padded
            # always number this from the first
            filename = add_count(name, 1)#first output name have number 1

        else:#not padded
            first = add_count(name, 1)#skip 01 (if was manually renamed) 
            if first in fl:
                filename = first # if a 1 exists avoid exporting version 0 (without number)

        stop = 5000
        while filename in fl:
            ct += 1
            # filename = f'{name}_{str(ct).zfill(2)}'#simple version
            filename = add_count(name, ct)
            
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

        elif self.rendermode == 1:#OGL CAM
            bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=False)
        
        # else:
        #     bpy.ops.render.render(animation=False, write_still=True)#, layer="", scene=""
        
        elif self.rendermode == 2:
            # Add a camera with (copy active cam settings ? better copy user view settings)
            # Put user view matrix  camera matrix
            # option to create camera from view
            # 
            bpy.ops.render.render(animation=False, write_still=True, use_viewport=True)#, layer="", scene=""
        
        elif self.rendermode == 3:
            bpy.ops.render.render(animation=False, write_still=True)#, layer="", scene=""
        

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
        dest = context.scene.qrd_savepath
        if not dest:
            foldername = 'quick_render'#define in user pref ?
            if bpy.data.is_saved:
                dest = join(dirname(bpy.data.filepath), foldername)
            else:
                # bpy.app.tempdir -> temporary dir use by this session only
                dest = join(bpy.context.preferences.filepaths.temporary_directory, foldername)
            # if not exists(dest):
            #     os.mkdir(dest)

        dest = bpy.path.abspath(dest)
        if not exists(dest):
            dest = dirname(dest)
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

        layout.prop(context.scene, 'qrd_savepath', text='save folder')
        layout.prop(context.scene, 'qrd_filename', text='filename')

        row = layout.row(align=False)
        row.prop(context.scene, 'qrd_insert_date')
        row.prop(context.scene, 'qrd_insert_frame')

        layout.label(text='OpenGL render')
        row = layout.row(align=False)
        row.operator("render.qv_render_ops", text='openGl view', icon='RENDER_STILL').rendermode = 0
        row.operator("render.qv_render_ops", text='openGl cam', icon='RESTRICT_RENDER_OFF').rendermode = 1

        layout = self.layout
        layout.label(text='Render')
        row = layout.row(align=False)
        # row.operator("render.qv_render_ops", text='render view', icon='RENDER_STILL').rendermode = 2
        row.operator("render.qv_render_ops", text='render cam', icon='OUTLINER_OB_CAMERA').rendermode = 3
        layout.separator()
        layout.operator("render.qv_open_loc", icon='OUTPUT')#text='render cam', FILE_FOLDER, OUTPUT (print like images)

classes = (
    QRD_OT_render_view,
    QRD_PT_quickrenderbuttons,
    QRD_OT_open_export_folder
)

def register():
    #add one for path
    bpy.types.Scene.qrd_filename = bpy.props.StringProperty(description="The filename used for export. You can leave it empty\nYou can specify padding e.g: flashrender_###")#(use template set in your user preferences)
    bpy.types.Scene.qrd_savepath = bpy.props.StringProperty(subtype='DIR_PATH', description="Export location, if not specify, create a 'quick_render' directory aside blend location")#(change defaut name in user_prefernece)
    bpy.types.Scene.qrd_insert_date = bpy.props.BoolProperty(name="insert date", default=False, description="Insert the date as suffix in filename\ne.g.: beloved-cube_2020-02-11")
    bpy.types.Scene.qrd_insert_frame = bpy.props.BoolProperty(name="insert frame", default=False, description="Insert the frame number as suffix in filename\ne.g: beloved_cube_0250\n(or with date : beloved_cube_2020-02-11_0250)")
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.qrd_filename
    del bpy.types.Scene.qrd_savepath
    del bpy.types.Scene.qrd_insert_date
    del bpy.types.Scene.qrd_insert_frame

if __name__ == "__main__":
    register()