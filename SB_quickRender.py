'''
Copyright (C) 2019 Samuel Bernou
Bernou.samuel@gmail.com

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
    "name": "Render fast",
    "description": "Buttons in 3D view to quick render and export openGL view and cam",
    "author": "Samuel Bernou",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "location": "3D viewport > N bar > View tab > Quick render",
    "warning": "",
    "wiki_url": "",
    "category": "3D View" }


import bpy
import os
from os import listdir
from os.path import join, dirname, basename, exists, isfile, isdir, splitext, normpath
from time import strftime

# add history as UI list
# quick options (addon prefs or 2/3 preset)

class RDFAST_OT_render_opengl(bpy.types.Operator):
    bl_idname = "render.opengl_ops"
    bl_label = "Test operator multiple"
    bl_description = ""
    bl_options = {"REGISTER"}

    rendermode : bpy.props.IntProperty()

    def execute(self, context):
        C = bpy.context
        scn = scene = context.scene

        dest = bpy.context.scene.rdfast_savepath
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

        name = bpy.context.scene.rdfast_filename
        name = name.replace(' ', '_')

        if not name:
            name = strftime("render_%d-%H-%M")#-%S day, hours, minutes #seconds

        fl = [splitext(i)[0] for i in listdir(dest)]

        filename = name

        ct = 1#skip 01 and got to 02

        stop = 99
        while filename in fl:
            ct += 1
            filename = f'{name}_{str(ct).zfill(2)}'
            if ct == stop:
                break

        fp = normpath(join(dest, filename))
        # print(filename)
        # print('fp: ', fp)


        org = scn.render.filepath
        scn.render.filepath = fp
        
        if self.rendermode == 0:
            bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=True)

        elif self.rendermode == 1:
            bpy.ops.render.opengl(animation=False, sequencer=False, write_still=True, view_context=False)
        
        else:
            bpy.ops.render.render(animation=False, write_still=True)#, layer="", scene=""

        #reset
        scn.render.filepath = org

        return {"FINISHED"}


class RDFAST_PT_quickrenderbuttons(bpy.types.Panel):
    bl_idname = "RDFAST_PT_quickpanel"
    bl_label = "Quick render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"

    def draw(self, context):
        layout = self.layout
        #layout.use_property_split = True#send properties to the right side
        # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        #row = layout.split(align=True,percentage=0.5)
        layout.prop(context.scene, 'rdfast_savepath', text='save folder')
        layout.prop(context.scene, 'rdfast_filename', text='filename')

        layout.label(text='openGL render')
        row = layout.row(align=False)
        row.operator("render.opengl_ops", text='openGl view', icon='RENDER_STILL').rendermode = 0
        row.operator("render.opengl_ops", text='openGl cam', icon='RESTRICT_RENDER_OFF').rendermode = 1

        layout = self.layout
        layout.label(text='Render')
        layout.operator("render.opengl_ops", text='render', icon='OUTLINER_OB_CAMERA').rendermode = 2

classes = (
    RDFAST_OT_render_opengl,
    RDFAST_PT_quickrenderbuttons
)

def register():
    #add one for path
    bpy.types.Scene.rdfast_filename = bpy.props.StringProperty()
    bpy.types.Scene.rdfast_savepath = bpy.props.StringProperty(subtype='DIR_PATH')
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rdfast_filename
    del bpy.types.Scene.rdfast_savepath

if __name__ == "__main__":
    register()